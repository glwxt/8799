#!/usr/bin/env python3
"""Publish metadata-only FRED evidence summaries for GLT reports.

Source CSV remains an artifact, never auto-promoted into the scoring engine.
A failed collection yields an explicit failure report, not yesterday's values
silently labeled as today's successful download.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import urlparse
from batch_stage import SERIES, parse_csv

def parse_time(value):
    t = dt.datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("timezone required")
    return t.astimezone(dt.timezone.utc)

def validate_manifest(manifest):
    if manifest.get("status") != "staging_only" or manifest.get("eligible_for_official_glt_score") is not False:
        raise ValueError("Only non-scoring FRED staging manifests can be published")
    t=parse_time(manifest["retrieved_at_utc"])
    if t > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise ValueError("Future retrieval time")
    success=manifest["series"]
    failures=manifest["errors"]
    if not isinstance(success,dict) or not isinstance(failures,dict):
        raise ValueError("Bad manifest types")
    if (set(success) | set(failures)) != set(SERIES) or set(success) & set(failures):
        raise ValueError("All six series must be accounted for exactly once")
    if manifest.get("success_count") != len(success) or manifest.get("failure_count") != len(failures):
        raise ValueError("Count mismatch")
    records={}
    for key, item in success.items():
        url=item.get("source_url","")
        parts=urlparse(url)
        if parts.scheme!="https" or parts.netloc!="fred.stlouisfed.org":
            raise ValueError("Untrusted FRED source")
        digest=item.get("sha256","")
        if not re.fullmatch("[a-f0-9]{64}",digest):
            raise ValueError("Bad source checksum")
        date=dt.date.fromisoformat(item["last_observation_date"])
        if date > t.date() + dt.timedelta(days=1):
            raise ValueError("Future observation")
        number=float(item["last_value_current_vintage"])
        if not math.isfinite(number):
            raise ValueError("Non-finite observed value")
        series_time=parse_time(item["retrieved_at_utc"])
        if series_time < t - dt.timedelta(minutes=20) or series_time > t + dt.timedelta(minutes=30):
            raise ValueError("Series retrieval time inconsistent with run")
        if item.get("release_timestamp_verified") is not False:
            raise ValueError("Publication time wrongly marked verified")
        if item.get("unit")!=SERIES[key]["unit"] or item.get("indicator")!=SERIES[key]["indicator"]:
            raise ValueError("Unexpected unit or indicator")
        records[key]={
            "indicator":item["indicator"],
            "observation_date":date.isoformat(),
            "value_current_vintage":number,
            "unit":item["unit"],
            "frequency":item["frequency"],
            "source_url":url,
            "sha256_raw_csv":digest,
            "retrieved_at_utc":series_time.isoformat(),
            "release_timestamp_verified":False,
            "historical_vintage_verified":False
        }
    return t,records

def verify_raw_bundle(manifest, folder):
    """Reject altered or missing raw CSV before the metadata enters GitHub."""
    folder=Path(folder)
    for sid,entry in manifest["series"].items():
        path=folder/(sid+".csv")
        raw=path.read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=entry["sha256"]:
            raise ValueError("Raw CSV hash mismatch: "+sid)
        parsed=parse_csv(raw,sid)
        if parsed["last_observation_date"]!=entry["last_observation_date"]:
            raise ValueError("Raw CSV observation date mismatch: "+sid)
        if parsed["last_value_current_vintage"]!=float(entry["last_value_current_vintage"]):
            raise ValueError("Raw CSV value mismatch: "+sid)

def build(manifest, threshold=4):
    t,records=validate_manifest(manifest)
    zone=dt.timezone(dt.timedelta(hours=8))
    local=t.astimezone(zone)
    error_summary={key:str(value)[:450] for key,value in sorted(manifest["errors"].items())}
    return {
        "schema":"glt-fred-evidence-summary-v1",
        "generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "data_retrieved_at_utc":t.isoformat(),
        "data_retrieved_at_taipei":local.isoformat(),
        "local_calendar_date":local.date().isoformat(),
        "source":"FRED graph current-vintage CSV",
        "expected_series":len(SERIES),
        "success_count":len(records),
        "failure_count":len(error_summary),
        "collection_status":"OK" if len(records)>=threshold else "DEGRADED",
        "collection_min_success":threshold,
        "series":records,
        "errors":error_summary,
        "coverage_note":"Collection success is not GLT 19-indicator coverage.",
        "official_glt_score":None,
        "eligible_for_official_glt_score":False,
        "input_to_official_glt_engine":False,
        "source_release_timestamps_verified":False,
        "historical_point_in_time_backtest_valid":False,
        "report_delivery_status":"not_managed_by_this_workflow",
    }

def markdown(out):
    lines=[
        "# GLT FRED 最新采集证据（非正式评分）","",
        "采集时间（台湾）："+out["data_retrieved_at_taipei"],
        "采集状态："+out["collection_status"]+"；成功："+str(out["success_count"])+"/"+str(out["expected_series"]),
        "",
        "**注意：仅反映FRED抓取时可见的当前修订版数据，不代表当时原始发布时间；不能作为GLT正式评分覆盖率，也不能冒充实时报价。**",
        "",
        "| FRED | 最新观测日 | 当前版本数值 | 单位 | 来源 |",
        "|---|---|---:|---|---|",
    ]
    for key in SERIES:
        if key in out["series"]:
            s=out["series"][key]
            lines.append("| "+key+" | "+s["observation_date"]+" | "+str(s["value_current_vintage"])+" | "+s["unit"]+" | "+s["source_url"]+" |")
        else:
            lines.append("| "+key+" | NA | NA | NA | 失败；详见 JSON errors |")
    lines.extend(["","正式GLT综合分：不生成；BTC-GT / GOLD-GT / EQUITY-GT：不生成。","","自动日报与本数据暂存流程分别运行；需确认本报告读取了哪个采集版本。",""])
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True,type=Path)
    ap.add_argument("--destination",required=True,type=Path)
    ap.add_argument("--min-success",type=int,default=4)
    args=ap.parse_args()
    if not 1<=args.min_success<=len(SERIES):
        ap.error("Invalid minimum")
    m=json.loads(args.manifest.read_text(encoding="utf-8"))
    result=build(m,args.min_success)
    verify_raw_bundle(m,args.manifest.parent)
    args.destination.mkdir(parents=True,exist_ok=True)
    (args.destination/"fred_latest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (args.destination/"fred_latest.md").write_text(markdown(result),encoding="utf-8")
    print(json.dumps({"state":result["collection_status"],"success":result["success_count"],"file":str(args.destination/"fred_latest.json")},ensure_ascii=False))
    if result["collection_status"]!="OK":
        raise SystemExit("DEGRADED; summary written with explicit errors")

if __name__=="__main__":
    main()
