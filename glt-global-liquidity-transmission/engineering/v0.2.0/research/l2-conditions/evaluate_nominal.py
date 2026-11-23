"""GLT L2 candidate test: realized equity return vs nominal-yield remainder."""
import argparse
import csv
import hashlib
import json
from bisect import bisect_right
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np

SERIES = ("SP500", "DGS10", "DFII10", "T10YIE")
HOLDOUT = date(2025, 1, 1)


def read(path, series, cutoff):
    with path.open(newline="", encoding="utf-8-sig") as source:
        values = {date.fromisoformat(row["observation_date"]): float(row[series])
                  for row in csv.DictReader(source) if row[series] not in ("", ".")}
    return {day: value for day, value in values.items() if day <= cutoff}


def samples(inputs, sessions_forward):
    equity, nominal, real, published_breakeven = (inputs[name] for name in SERIES)
    equity_days = sorted(equity)
    rate_days = sorted(nominal.keys() & real.keys() & published_breakeven.keys())
    breakeven = {day: nominal[day] - real[day] for day in rate_days}
    if any(abs(breakeven[day] - published_breakeven[day]) > 0.02 for day in rate_days):
        raise ValueError("Nominal, real and breakeven data fail unit and date reconciliation")
    for i in range(1, len(equity_days) - sessions_forward):
        day = equity_days[i]
        index = bisect_right(rate_days, equity_days[i - 1]) - 1
        if index < 5 or (day - rate_days[index]).days > 7:
            continue
        new, old = rate_days[index], rate_days[index - 5]
        x = [real[new] - real[old], breakeven[new] - breakeven[old]]
        end = equity_days[i + sessions_forward]
        yield day, end, x, np.log(equity[end] / equity[day])


def predict(rows):
    months = defaultdict(list)
    for row in rows:
        if row[0] >= HOLDOUT:
            months[row[0].strftime("%Y-%m")].append(row)
    for block in months.values():
        train = [r for r in rows if r[1] < block[0][0]]
        if len(train) < 500:
            continue
        target = np.array([r[3] for r in train])
        mean_target = target.mean()
        fits = []
        for width in (1, 2):
            x = np.array([r[2][:width] for r in train])
            mean, sd = x.mean(axis=0), x.std(axis=0)
            sd[sd == 0] = 1
            z = (x - mean) / sd
            coef = np.linalg.solve(z.T @ z + np.eye(width), z.T @ (target - mean_target))
            fits.append((width, mean, sd, coef))
        for day, end, x, actual in block:
            predicted = [float(mean_target)]
            for width, mean, sd, coef in fits:
                predicted.append(float(mean_target + ((x[:width] - mean) / sd) @ coef))
            yield day, end, actual, predicted


def summarize(rows):
    actual = np.array([r[2] for r in rows])
    forecast = np.array([r[3] for r in rows])
    errors = np.abs(forecast - actual[:, None])
    gains = errors[:, 1] - errors[:, 2]
    return {
        "count": len(rows), "first_signal": str(rows[0][0]), "last_signal": str(rows[-1][0]),
        "mae_bp": np.round(errors.mean(axis=0) * 10000, 2).tolist(),
        "direction_hit_pct": np.round((np.sign(forecast) == np.sign(actual[:, None])).mean(axis=0) * 100, 2).tolist(),
        "incremental_mae_gain_without_best_signal_bp": round(float(np.delete(gains, np.argmax(gains)).mean() * 10000), 2),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("folder", type=Path)
    p.add_argument("--cutoff", required=True, type=date.fromisoformat)
    a = p.parse_args()
    inputs = {s: read(a.folder / (s + ".csv"), s, a.cutoff) for s in SERIES}
    result = {"eligible_for_official_score": False, "cutoff": str(a.cutoff),
              "order": ["historical_mean", "real_yield", "real_yield_plus_breakeven"],
              "sha256": {s: hashlib.sha256((a.folder / (s + ".csv")).read_bytes()).hexdigest()
                         for s in SERIES}}
    for horizon in (1, 5):
        output = list(predict(list(samples(inputs, horizon))))
        result[f"{horizon}session"] = summarize(output)
        for year in (2025, 2026):
            result[f"{horizon}session_{year}"] = summarize([r for r in output if r[0].year == year])
        if horizon == 5:
            subset = []
            for row in output:
                if not subset or row[0] >= subset[-1][1]:
                    subset.append(row)
            result["5session_nonoverlap"] = summarize(subset)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
