"""Matched-sample research comparison; never creates a GLT scoring input."""
import argparse
import csv
import io
import math
import re
from bisect import bisect_right
from datetime import date, datetime, timedelta
from pathlib import Path
from zipfile import ZipFile

from evaluate_gld import START, evaluate, read_gld, report

WEIGHTS = {"EUR": .576, "JPY": .136, "GBP": .119, "CAD": .091, "SEK": .042, "CHF": .036}


def ecb_basket(row):
    usd_per_eur = float(row["USD"])
    eur_quote = {c: float(row[c]) for c in WEIGHTS if c != "EUR"}
    eur_quote["EUR"] = 1.
    quotes = {c: eur_quote[c] / usd_per_eur for c in WEIGHTS}
    if any(not math.isfinite(q) or q <= 0 for q in quotes.values()):
        raise ValueError("Invalid reference FX")
    return 50.14348112 * math.prod(quotes[c] ** w for c, w in WEIGHTS.items())


def read_ecb(path, cutoff):
    with ZipFile(path) as zf, zf.open("eurofxref-hist.csv") as source:
        rows = []
        for row in csv.DictReader(io.TextIOWrapper(source, encoding="utf-8-sig")):
            day = date.fromisoformat(row["Date"])
            if day <= cutoff and all(row[c] not in ("", "N/A") for c in ("USD", "JPY", "GBP", "CAD", "SEK", "CHF")):
                rows.append((day, ecb_basket(row)))
    return sorted(rows)


def read_broad(html, cutoff):
    pattern = r'<th id="r1" headers="a1">\s*(\d{1,2}-[A-Z]{3}-\d{2})\s*</th>\s*<td headers="a2 a1 r1">\s*([0-9.]+)\s*</td>'
    rows = [(datetime.strptime(d, "%d-%b-%y").date(), float(v))
            for d, v in re.findall(pattern, html.read_text(encoding="utf-8")) if v != "."]
    return sorted((d, v) for d, v in rows if d <= cutoff)


def read_treasury(folder, cutoff):
    obs = {}
    for file in sorted(folder.glob("real_*.csv")):
        with file.open(encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                day = datetime.strptime(row["Date"], "%m/%d/%Y").date()
                value = row["10 YR"]
                if day <= cutoff and value not in ("", "N/A"):
                    v = float(value)
                    if day in obs and obs[day] != v:
                        raise ValueError(f"Conflicting Treasury yields on {day}")
                    obs[day] = v
    return sorted(obs.items())


def matched_samples(gold, real, broad, basket, horizon):
    series = (real, broad, basket, basket)
    dates = tuple([day for day, _ in values] for values in series)
    matched = [[] for _ in range(3)]
    for i in range(6, len(gold) - horizon):
        day, close, _ = gold[i]
        prev = gold[i - 1][0]
        if day < START:
            continue
        bounds = (prev, day - timedelta(days=10), day - timedelta(days=10), prev)
        eligible = tuple(bisect_right(ds, bound) - 1 for ds, bound in zip(dates, bounds))
        if min(eligible) < 5 or (day - prev).days > 7:
            continue
        if any((day - obs[j][0]).days > age for obs, j, age in zip(series, eligible, (7, 16, 16, 7))):
            continue
        # Same dates, targets, and non-dollar features for all three models.
        end_day, end_price, _ = gold[i + horizon]
        y = math.log(end_price / close)
        r = eligible[0]
        real_chg = real[r][1] - real[r - 5][1]
        etf_chg = math.log(gold[i - 1][2] / gold[i - 6][2])
        for rows, dollar, j in zip(matched, series[1:], eligible[1:]):
            dx = math.log(dollar[j][1] / dollar[j - 5][1])
            rows.append((day, end_day, [real_chg, dx, etf_chg], y))
    return matched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--cutoff", type=date.fromisoformat, required=True)
    a = parser.parse_args()
    gld = read_gld(a.folder / "gld.xlsx", a.cutoff)
    broad = read_broad(a.folder / "broad.htm", a.cutoff)
    basket = read_ecb(a.folder / "ecb.zip", a.cutoff)
    real = read_treasury(a.folder, a.cutoff)
    for name, rows in zip(("Fed broad", "ECB basket", "Treasury real"), (broad, basket, real)):
        if len(rows) < 2500:
            raise ValueError(f"Insufficient data for {name}: {len(rows)}")
        print(name, len(rows), rows[0], rows[-1])
    for horizon in (1, 5):
        for label, dataset in zip(("broad-10d", "ECB-10d", "ECB-prior-GLD-day"), matched_samples(gld, real, broad, basket, horizon)):
            out = evaluate(dataset)
            report(out, f"{horizon}d {label}, all")
            report([x for x in out if x[0] >= date(2024, 1, 1)], f"{horizon}d {label}, 2024+")
            if horizon == 5:
                blocks = []
                for row in out:
                    if not blocks or row[0] >= blocks[-1][1]:
                        blocks.append(row)
                report(blocks, f"{horizon}d {label}, non-overlapping")


if __name__ == "__main__":
    main()
