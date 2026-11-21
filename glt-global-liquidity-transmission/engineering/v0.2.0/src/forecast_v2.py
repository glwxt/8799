#!/usr/bin/env python3
"""Versioned GLT forecast v2: immutable-by-CLI price snapshots and strict scoring.

Does not edit old forecast.py or historical prediction logs. File-exclusivity is
a guard against accidental overwrites, NOT tamper-proof archival storage.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
from urllib.parse import urlparse

DIRECTIONS = ("偏多", "震荡偏多", "震荡", "震荡偏空", "偏空")
MODELS = ("BTC-GT", "GOLD-GT", "EQUITY-GT")
HOURS = {"24h": 24, "7d": 168}

def utc(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone")
    return parsed.astimezone(dt.timezone.utc)

def valid_url(value):
    parsed = urlparse(value)
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise ValueError("Evidence URL must be HTTP(S)")
    return value

def number(value, positive=False):
    result = float(value)
    if not math.isfinite(result) or (positive and result <= 0):
        raise ValueError("Invalid numeric value")
    return result

def bands_to_direction(return_percent, neutral, strong):
    """Precommitted five-class price move definition."""
    movement = abs(return_percent)
    if movement <= neutral:
        return "震荡"
    if movement <= strong:
        return "震荡偏多" if return_percent > 0 else "震荡偏空"
    return "偏多" if return_percent > 0 else "偏空"

def save_once(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    handle = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True) if hasattr(path, "unlink") else None
        raise

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def create_forecast(root, *, model, horizon, direction, asof, baseline_at,
                    baseline_price, baseline_source, neutral_pct, strong_pct,
                    confidence, rationale, asset):
    if model not in MODELS or horizon not in HOURS or direction not in DIRECTIONS:
        raise ValueError("Invalid model, horizon, or direction")
    asof_dt, base_dt = utc(asof), utc(baseline_at)
    if base_dt > asof_dt:
        raise ValueError("Baseline price cannot be published in the future relative to forecast")
    if (asof_dt - base_dt) > dt.timedelta(days=4):
        raise ValueError("Baseline price too old; document market closures separately")
    baseline_price = number(baseline_price, positive=True)
    neutral_pct = number(neutral_pct, positive=True)
    strong_pct = number(strong_pct, positive=True)
    confidence = number(confidence)
    if strong_pct <= neutral_pct or not 0 <= confidence <= 1:
        raise ValueError("Thresholds or confidence invalid")
    if not rationale.strip() or not asset.strip():
        raise ValueError("Rationale and asset identifier required")
    valid_url(baseline_source)
    record = dict(schema="GLT-forecast-v2", model=model, asset=asset,
                  horizon=horizon, direction=direction, confidence=confidence,
                  asof=asof_dt.isoformat(), baseline_at=base_dt.isoformat(),
                  baseline_price=baseline_price, baseline_source=baseline_source,
                  neutral_pct=neutral_pct, strong_pct=strong_pct, rationale=rationale,
                  target_at=(asof_dt + dt.timedelta(hours=HOURS[horizon])).isoformat(),
                  created_at=dt.datetime.now(dt.timezone.utc).isoformat())
    immutable_id = hashlib.sha256(("|".join([model, asset, horizon,
                     asof_dt.isoformat()])).encode("utf-8")).hexdigest()[:24]
    record["id"] = immutable_id
    save_once(Path(root) / "logs" / "v2" / "forecasts" / (immutable_id + ".json"), record)
    return record

def record_outcome(root, *, forecast_id, observed_at, observed_price, source):
    path = Path(root) / "logs" / "v2" / "forecasts" / (forecast_id + ".json")
    f = load(path)
    if f.get("schema") != "GLT-forecast-v2":
        raise ValueError("Unknown forecast format")
    observed_at_dt = utc(observed_at)
    target_dt = utc(f["target_at"])
    # Only compare the horizon end or the next eligible trading observation.
    if observed_at_dt < target_dt or observed_at_dt > target_dt + dt.timedelta(hours=96):
        raise ValueError("Observed price outside target window; mark as non-comparable")
    observed_price = number(observed_price, positive=True)
    valid_url(source)
    change = (observed_price / f["baseline_price"] - 1) * 100
    direction = bands_to_direction(change, f["neutral_pct"], f["strong_pct"])
    result = dict(schema="GLT-outcome-v2", id=forecast_id, asset=f["asset"],
                  observed_at=observed_at_dt.isoformat(), observed_price=observed_price,
                  evidence_url=source, move_pct=round(change, 6), observed_direction=direction,
                  forecast_direction=f["direction"], exact_match=direction == f["direction"],
                  recorded_at=dt.datetime.now(dt.timezone.utc).isoformat())
    save_once(Path(root) / "logs" / "v2" / "outcomes" / (forecast_id + ".json"), result)
    return result

def review(root, minimum=30):
    root = Path(root) / "logs" / "v2"
    forecasts = sorted((root / "forecasts").glob("*.json")) if (root / "forecasts").exists() else []
    outcomes = root / "outcomes"
    groups = {}
    for path in forecasts:
        f = load(path)
        answer = outcomes / (f["id"] + ".json")
        if not answer.exists():
            continue
        o = load(answer)
        key = f["model"] + "/" + f["horizon"]
        row = groups.setdefault(key, {"paired": 0, "exact": 0, "by_direction": {}})
        row["paired"] += 1
        row["exact"] += int(o["exact_match"])
        d = row["by_direction"].setdefault(f["direction"], {"paired": 0, "exact": 0})
        d["paired"] += 1
        d["exact"] += int(o["exact_match"])
    for g in groups.values():
        g["exact_rate"] = round(g["exact"]/g["paired"], 4) if g["paired"] >= minimum else None
        g["warning"] = "样本不足" if g["paired"] < minimum else "描述性准确率；尚需基准比较及样本外检验"
    return {"total_forecasts":len(forecasts),"groups":groups,"minimum_samples":minimum}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("predict")
    for field in ("model", "horizon", "direction", "asof", "baseline-at",
                  "baseline-price", "baseline-source", "neutral-pct", "strong-pct",
                  "confidence", "rationale", "asset"):
        p.add_argument("--" + field, required=True)
    o = sub.add_parser("result")
    for field in ("forecast-id", "observed-at", "observed-price", "source"):
        o.add_argument("--" + field, required=True)
    sub.add_parser("review")
    args = parser.parse_args()
    root = Path(args.root)
    if args.command == "predict":
        fields = vars(args).copy()
        for key in ("root", "command"):
            fields.pop(key)
        result = create_forecast(root, **{k.replace("-", "_"):v for k,v in fields.items()})
    elif args.command == "result":
        result = record_outcome(root, forecast_id=args.forecast_id,
                                observed_at=args.observed_at, observed_price=args.observed_price,
                                source=args.source)
    else:
        result = review(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
