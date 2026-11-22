"""Collect Treasury and TWSE evidence for the operations report."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TAIPEI = timezone(timedelta(hours=8))
TREASURY = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance"
TWSE = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"
FOREIGN = "外資及陸資(不含外資自營商)"


def fetch(url):
    request = Request(url, headers={"User-Agent": "GLT evidence collection", "Accept": "application/json"})
    with urlopen(request, timeout=12) as response:
        raw = response.read()
    return json.loads(raw), raw


def treasury(today):
    url = TREASURY + "?" + urlencode({
        "filter": f"record_date:gte:{today - timedelta(days=7)},record_date:lte:{today}",
        "sort": "-record_date", "page[size]": 100,
    })
    payload, raw = fetch(url)
    rows = [row for row in payload["data"]
            if row["account_type"] == "Treasury General Account (TGA) Closing Balance"]
    row = max(rows, key=lambda item: item["record_date"])
    return url, raw, {
        "observation_date": row["record_date"], "value": int(row["open_today_bal"]),
        "unit": "USD millions", "scope": "Treasury DTS Table I closing balance",
    }


def taiwan(today):
    for offset in range(8):
        day = today - timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        stamp = day.strftime("%Y%m%d")
        url = TWSE + "?" + urlencode({"dayDate": stamp, "type": "day", "response": "json"})
        payload, raw = fetch(url)
        if payload.get("stat") != "OK":
            if "沒有符合條件" in payload.get("stat", ""):
                continue
            raise ValueError("TWSE returned an unexpected status")
        if payload["date"] != stamp:
            raise ValueError("TWSE returned a different trading date")
        columns = payload["fields"]
        row = next(row for row in payload["data"] if row[columns.index("單位名稱")] == FOREIGN)
        buy, sell, net = (int(row[columns.index(key)].replace(",", ""))
                          for key in ("買進金額", "賣出金額", "買賣差額"))
        if buy - sell != net:
            raise ValueError("TWSE net flow does not reconcile with buy and sell amounts")
        return url, raw, {"observation_date": day.isoformat(), "value": net,
                           "unit": "TWD", "scope": FOREIGN}
    raise ValueError("No TWSE trading session found in the last eight days")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    args = parser.parse_args()
    now = datetime.now(TAIPEI)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    evidence, errors = {}, {}
    for key, collect in (("TGA", treasury), ("TWSE_FOREIGN_NET", taiwan)):
        try:
            url, raw, observation = collect(now.date())
            (args.raw_dir / (key + ".json")).write_bytes(raw)
            evidence[key] = dict(observation, source_url=url, sha256=hashlib.sha256(raw).hexdigest(),
                                 retrieved_at=datetime.now(TAIPEI).isoformat())
        except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
            errors[key] = f"{type(error).__name__}: {error}"
    result = {"started_at": now.isoformat(), "observations": evidence, "errors": errors,
              "eligible_for_official_score": False, "source_release_timestamps_verified": False}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Official-source evidence: {len(evidence)}/2")


if __name__ == "__main__":
    main()
