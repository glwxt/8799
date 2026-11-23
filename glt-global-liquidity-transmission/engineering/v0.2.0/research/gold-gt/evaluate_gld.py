"""Reproduce exploratory GOLD-GT comparisons from the issuer archive and FRED CSVs."""
import argparse
import csv
from bisect import bisect_right
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
from openpyxl import load_workbook

START = date(2016, 1, 1)
EVALUATION_START = date(2019, 1, 1)
COLUMNS = ("Closing Price", "Ounces of Gold per Share", "Total Ounces of Gold in the Trust")


def read_fred(path, series, cutoff):
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = [(date.fromisoformat(row["observation_date"]), float(row[series]))
                for row in csv.DictReader(source) if row[series] not in ("", ".")]
    return [(day, value) for day, value in rows if day <= cutoff]


def read_gld(path, cutoff):
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        data = iter(workbook["US GLD Historical Archive"].values)
        headings = next(data)
        cols = [headings.index(name) for name in COLUMNS]
        rows = []
        for row in data:
            if not row[0]:
                continue
            trading_day = datetime.strptime(row[0], "%d-%b-%Y").date()
            values = [row[i] for i in cols]
            if trading_day <= cutoff and all(isinstance(v, (int, float)) and v > 0 for v in values):
                close, ounces_per_share, ounces = values
                rows.append((trading_day, close, ounces / ounces_per_share))
    finally:
        workbook.close()
    if any(a[0] >= b[0] for a, b in zip(rows, rows[1:])):
        raise ValueError("GLD archive dates must increase")
    return rows


def samples(gold, yields, dollar, horizon):
    yield_days = [day for day, _ in yields]
    dollar_days = [day for day, _ in dollar]
    rows = []
    for i in range(6, len(gold) - horizon):
        day, close, _ = gold[i]
        if day < START:
            continue
        prev_day = gold[i - 1][0]
        y = bisect_right(yield_days, prev_day) - 1
        d = bisect_right(dollar_days, day - timedelta(days=10)) - 1
        if (min(y, d) < 5 or (day - yields[y][0]).days > 7
                or (day - dollar[d][0]).days > 16 or (day - prev_day).days > 7):
            continue
        etf_change = np.log(gold[i - 1][2] / gold[i - 6][2])
        x = [yields[y][1] - yields[y - 5][1], np.log(dollar[d][1] / dollar[d - 5][1]), etf_change]
        end_day, end_price, _ = gold[i + horizon]
        rows.append((day, end_day, x, np.log(end_price / close)))
    return rows


def evaluate(rows):
    months = defaultdict(list)
    for row in rows:
        if row[0] >= EVALUATION_START:
            months[row[0].strftime("%Y-%m")].append(row)
    out = []
    for block in months.values():
        training = [r for r in rows if r[1] < block[0][0]]
        if len(training) < 500:
            continue
        y = np.array([r[3] for r in training])
        fits = []
        for width in (2, 3):
            x = np.array([r[2][:width] for r in training])
            mean, sd = x.mean(axis=0), x.std(axis=0)
            sd[sd == 0] = 1
            z = (x - mean) / sd
            coef = np.linalg.solve(z.T @ z + np.eye(width), z.T @ (y - y.mean()))
            fits.append((width, mean, sd, coef))
        for day, end, x, actual in block:
            preds = [float(y.mean())]
            for width, mean, sd, coef in fits:
                preds.append(float(y.mean() + ((x[:width] - mean) / sd) @ coef))
            out.append((day, end, actual, preds))
    return out


def report(rows, name):
    actual = np.array([r[2] for r in rows])
    predictions = np.array([r[3] for r in rows])
    mae = np.mean(np.abs(predictions - actual[:, None]), axis=0)
    hits = np.mean(np.sign(predictions) == np.sign(actual[:, None]), axis=0)
    print(name, rows[0][0], rows[-1][0], len(rows),
          "MAE bp:", np.round(mae * 10000, 2).tolist(),
          "direction %:", np.round(hits * 100, 2).tolist())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_folder", type=Path)
    parser.add_argument("--cutoff", required=True, type=date.fromisoformat)
    args = parser.parse_args()
    folder = args.source_folder
    gold = read_gld(folder / "gld.xlsx", args.cutoff)
    yields = read_fred(folder / "DFII10.csv", "DFII10", args.cutoff)
    dollar = read_fred(folder / "DTWEXBGS.csv", "DTWEXBGS", args.cutoff)
    for horizon in (1, 5):
        output = evaluate(samples(gold, yields, dollar, horizon))
        report(output, f"{horizon} sessions all")
        report([r for r in output if r[0] >= date(2024, 1, 1)], f"{horizon} sessions 2024+")
        if horizon == 5:
            selected = []
            for row in output:
                if not selected or row[0] >= selected[-1][1]:
                    selected.append(row)
            report(selected, "5 sessions non-overlapping")


if __name__ == "__main__":
    main()
