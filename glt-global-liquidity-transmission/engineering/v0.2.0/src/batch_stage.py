#!/usr/bin/env python3
"""Fetch FRED current-vintage graph CSV into a dated *non-scoring* evidence bundle.

No release-vintage inference and NO automatic promotion to observations.csv.
Uses stdlib only. Each run has its own timestamped directory.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

SERIES = {
    "WRESBAL": {"indicator":"reserves","unit":"Millions of USD","frequency":"weekly"},
    "WALCL": {"indicator":"fed_assets","unit":"Millions of USD","frequency":"weekly"},
    "RRPONTSYD": {"indicator":"on_rrp","unit":"Billions of USD","frequency":"daily"},
    "DFII10": {"indicator":"us_10y_real","unit":"Percent","frequency":"daily"},
    "DGS10": {"indicator":"us_10y_nominal","unit":"Percent","frequency":"daily"},
    "BAMLH0A0HYM2": {"indicator":"hy_spread","unit":"Percent","frequency":"daily"},
}
PROVENANCE_WARNING = (
    "FRED graph CSV represents data available at retrieval time, including revisions. "
    "Not proof of historical release timestamps. Staging ONLY; do not score."
)
def parse_csv(raw, series):
    content = raw.decode("utf-8-sig")
    rd = csv.DictReader(io.StringIO(content))
    if rd.fieldnames is None or series not in rd.fieldnames:
        raise ValueError("Unexpected CSV columns")
    date_key = "DATE" if "DATE" in rd.fieldnames else "observation_date" if "observation_date" in rd.fieldnames else None
    if date_key is None:
        raise ValueError("Missing observation date column")
    count = 0
    last_date = None
    last_value = None
    for row in rd:
        d = row[date_key]
        v = row[series]
        dt.date.fromisoformat(d)
        if v not in ("", "."):
            value = float(v)
            if not (-1e308 < value < 1e308):
                raise ValueError("Non-finite value")
            count += 1
            if last_date is None or d > last_date:
                last_date, last_value = d, value
    if count == 0:
        raise ValueError("Series has no valid observations")
    return {"rows_numeric":count,"last_observation_date":last_date,"last_value_current_vintage":last_value}
def download_one(series,opener=urllib.request.urlopen):
    start_date = (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=430)).isoformat()
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urllib.parse.urlencode({"id":series,"cosd":start_date})
    req = urllib.request.Request(url,headers={"User-Agent":"GLT-Provenance-Staging/0.2.1"})
    with opener(req,timeout=30) as response:
        data = response.read(12_000_000)
    if len(data) >= 12_000_000:
        raise ValueError("Response too large")
    parsed = parse_csv(data,series)
    return url,data,parsed
def collect(directory,opener=urllib.request.urlopen,retries=2):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    manifest = {
       "retrieved_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
       "status":"staging_only",
       "source":"Federal Reserve Bank of St. Louis FRED graph CSV",
       "provenance_warning":PROVENANCE_WARNING,
       "series":{}, "errors":{},
       "eligible_for_official_glt_score":False
    }
    for sid,info in SERIES.items():
        err=None
        for attempt in range(retries+1):
            try:
                url,raw,parsed=download_one(sid,opener)
                (directory / (sid+".csv")).write_bytes(raw)
                manifest["series"][sid]=dict(info,**parsed,source_url=url,sha256=hashlib.sha256(raw).hexdigest(),retrieved_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),data_vintage="current_at_retrieval",release_timestamp_verified=False)
                err=None
                break
            except (HTTPError,URLError,TimeoutError,ValueError,OSError,UnicodeError) as exc:
                err=f"{type(exc).__name__}: {exc}"
                if attempt < retries:time.sleep(min(attempt+1,3))
        if err:manifest["errors"][sid]=err
    manifest["success_count"]=len(manifest["series"])
    manifest["failure_count"]=len(manifest["errors"])
    manifest["source_availability_ratio"]=round(len(manifest["series"])/len(SERIES),4)
    manifest["glt_scoring_coverage"]="NOT_CALCULATED"
    (directory/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return manifest

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--min-success",type=int,default=4)
    args=parser.parse_args()
    run=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=args.root/"staging"/"runs"/run
    result=collect(out)
    print(json.dumps({"directory":str(out),"success":result["success_count"],"failed":result["failure_count"],"glt_score":"NOT_CALCULATED"},ensure_ascii=False))
    if result["success_count"] < args.min_success:
        raise SystemExit("Too few staging sources; see manifest.json")
if __name__=="__main__":main()
