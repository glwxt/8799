#!/usr/bin/env python3
"""Fetch FRED current-vintage graph CSV into a dated *non-scoring* evidence bundle.

No release-vintage inference and NO automatic promotion to observations.csv.
Uses stdlib only. Each run has its own timestamped directory.
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "WRESBAL": {"indicator":"reserves","unit":"Millions of USD","frequency":"weekly"},
    "WALCL": {"indicator":"fed_assets","unit":"Millions of USD","frequency":"weekly"},
    "RRPONTSYD": {"indicator":"on_rrp","unit":"Billions of USD","frequency":"daily"},
    "DFII10": {"indicator":"us_10y_real","unit":"Percent","frequency":"daily"},
    "DGS10": {"indicator":"us_10y_nominal","unit":"Percent","frequency":"daily"},
    "BAMLH0A0HYM2": {"indicator":"hy_spread","unit":"Percent","frequency":"daily"},
    "VIXCLS": {"indicator":"vix","unit":"Percent","frequency":"daily"},
    "SWPT": {"indicator":"global_usd","unit":"Millions of USD","frequency":"weekly"},
    "SOFR": {"indicator":"usd_funding","unit":"Percent","frequency":"daily"},
    "IORB": {"indicator":"usd_funding","unit":"Percent","frequency":"daily"},
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
    url, data = download_graph([series], opener)
    return url, data, parse_csv(data, series)


def download_graph(series_ids, opener):
    end_date = dt.datetime.now(dt.timezone.utc).date()
    start_date = end_date - dt.timedelta(days=21)
    query = {"id": ",".join(series_ids), "cosd": start_date.isoformat(), "coed": end_date.isoformat()}
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url,headers={"User-Agent":"GLT-Provenance-Staging/0.2.1"})
    with opener(req,timeout=30) as response:
        data = response.read(12_000_000)
    if len(data) >= 12_000_000:
        raise ValueError("Response too large")
    return url, data
FETCH_ERRORS = (OSError, ValueError, http.client.HTTPException)


def download_with_retry(series, opener, retries):
    for attempt in range(retries + 1):
        try:
            url, raw, parsed = download_one(series, opener)
            retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
            return url, raw, parsed, retrieved_at
        except FETCH_ERRORS:
            if attempt == retries:
                raise
            time.sleep(min(2 ** attempt, 8))


def api_csv(raw, series):
    observations = json.loads(raw)["observations"]
    data = io.StringIO()
    writer = csv.writer(data)
    writer.writerow(("observation_date", series))
    for observation in observations:
        writer.writerow((observation["date"], observation["value"]))
    return data.getvalue().encode("utf-8")


def collect_api(directory, manifest, series_ids, opener, api_key):
    end = dt.datetime.now(dt.timezone.utc).date()
    for sid in series_ids:
        params = {
            "series_id": sid, "file_type": "json",
            "observation_start": (end - dt.timedelta(days=21)).isoformat(),
            "observation_end": end.isoformat(),
        }
        public_url = FRED_API_URL + "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            public_url + "&" + urllib.parse.urlencode({"api_key": api_key}),
            headers={"Accept": "application/json"},
        )
        try:
            with opener(request, timeout=10) as response:
                raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError("Response too large")
            data = api_csv(raw, sid)
            parsed = parse_csv(data, sid)
        except urllib.error.HTTPError as exc:
            manifest["errors"][sid] = f"FRED API HTTP {exc.code}"
            if exc.code in (401, 403, 429):
                break
            continue
        except FETCH_ERRORS + (KeyError, TypeError) as exc:
            manifest["errors"][sid] = "FRED API " + type(exc).__name__
            continue
        retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
        save_series(directory, manifest, sid, public_url, data, parsed, retrieved_at)
        (directory / (sid + ".json")).write_bytes(raw)
        manifest["series"][sid]["sha256_raw_json"] = hashlib.sha256(raw).hexdigest()


def collect(directory,opener=urllib.request.urlopen,retries=2, *, batch=False, api_key=None):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    manifest = {
       "retrieved_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
       "status":"staging_only",
       "source":"Federal Reserve Bank of St. Louis FRED graph CSV",
       "provenance_warning":PROVENANCE_WARNING,
       "series":{}, "errors":{},
       "eligible_for_official_glt_score":False
    }
    # One request avoids competing connections to the same FRED endpoint.
    # Individual requests still recover missing or malformed batch columns.
    if api_key:
        collect_api(directory, manifest, SERIES, opener, api_key)
    downloads_needed = [sid for sid in SERIES if sid not in manifest["series"]]
    if len(downloads_needed) > 1 and batch:
        try:
            url, raw = download_graph(downloads_needed, opener)
            retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
            for sid in list(downloads_needed):
                try:
                    parsed = parse_csv(raw, sid)
                except FETCH_ERRORS:
                    continue
                save_series(directory, manifest, sid, url, raw, parsed, retrieved_at)
                manifest["errors"].pop(sid, None)
                downloads_needed.remove(sid)
        except FETCH_ERRORS as exc:
            print(f"FRED batch request failed ({type(exc).__name__}): {exc}; trying each series")

    with ThreadPoolExecutor(max_workers=3) as executor:
        downloads = {
            sid: executor.submit(download_with_retry, sid, opener, retries)
            for sid in downloads_needed
        }
        for sid, future in downloads.items():
            try:
                url, raw, parsed, retrieved_at = future.result()
            except FETCH_ERRORS as exc:
                prior = manifest["errors"].get(sid)
                graph_error = f"{type(exc).__name__}: {exc}"
                manifest["errors"][sid] = f"{prior}; graph CSV {graph_error}" if prior else graph_error
                continue
            save_series(directory, manifest, sid, url, raw, parsed, retrieved_at)
            manifest["errors"].pop(sid, None)
    manifest["success_count"]=len(manifest["series"])
    manifest["failure_count"]=len(manifest["errors"])
    manifest["source_availability_ratio"]=round(len(manifest["series"])/len(SERIES),4)
    manifest["glt_scoring_coverage"]="NOT_CALCULATED"
    (directory/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return manifest

def save_series(directory, manifest, sid, url, raw, parsed, retrieved_at):
    (directory / (sid + ".csv")).write_bytes(raw)
    manifest["series"][sid] = dict(
        SERIES[sid], **parsed, source_url=url,
        sha256=hashlib.sha256(raw).hexdigest(),
        retrieved_at_utc=retrieved_at,
        data_vintage="current_at_retrieval", release_timestamp_verified=False,
    )


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--min-success",type=int,default=4)
    args=parser.parse_args()
    run=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=args.root/"staging"/"runs"/run
    result=collect(out, batch=True, api_key=os.environ.get("FRED_API_KEY"))
    print(json.dumps({"directory":str(out),"success":result["success_count"],"failed":result["failure_count"],"glt_score":"NOT_CALCULATED"},ensure_ascii=False))
    if result["success_count"] < args.min_success:
        raise SystemExit("Too few staging sources; see manifest.json")
if __name__=="__main__":main()
