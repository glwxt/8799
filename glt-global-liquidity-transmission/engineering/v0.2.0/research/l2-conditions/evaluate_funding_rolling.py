"""Evaluate fixed and trailing L2 funding flags against a later VIX risk proxy."""
import argparse
import hashlib
import json
from bisect import bisect_right
from datetime import date
from pathlib import Path

from evaluate import fred, percentile, reference_rates

TRAIN_END = date(2025, 1, 1)
WINDOW = 252
VIX_INCREASE = 3


def evaluate(folder, cutoff):
    sources = ("sofr.json", "effr.json", "iorb.csv", "VIXCLS.csv")
    sofr, effr = (reference_rates(folder / file, kind)
                  for file, kind in zip(sources[:2], ("SOFR", "EFFR")))
    iorb = fred(folder / sources[2], "IORB")
    vix = {day: amount for day, amount in fred(folder / sources[3], "VIXCLS").items()
           if day <= cutoff}
    vix_dates = sorted(vix)
    funding = [(d, int((sofr[d] - iorb[d]) * 100), int((effr[d] - iorb[d]) * 100))
               for d in sorted(sofr.keys() & effr.keys() & iorb.keys()) if d <= cutoff]
    initial = [row for row in funding if row[0] < TRAIN_END]
    fixed = thresholds(initial)
    observations = []
    for i, (day, secured, unsecured) in enumerate(funding):
        if day < TRAIN_END or i < WINDOW:
            continue
        next_close = bisect_right(vix_dates, day)
        if next_close + 5 >= len(vix_dates):
            continue
        anchor = vix_dates[next_close]
        if (anchor - day).days > 4:
            continue
        high = max(vix[d] for d in vix_dates[next_close + 1:next_close + 6])
        event = high - vix[anchor] >= VIX_INCREASE
        trailing = thresholds(funding[i - WINDOW:i])
        observations.append((day, event, secured > fixed[0] and unsecured > fixed[1],
                             secured > trailing[0] and unsecured > trailing[1]))
    return {
        "asof_cutoff": str(cutoff), "eligible_for_official_score": False,
        "window": WINDOW, "fixed_thresholds_bp": fixed, "event_vix_increase": VIX_INCREASE,
        "source_sha256": {f: hashlib.sha256((folder / f).read_bytes()).hexdigest() for f in sources},
        "full": summary(observations),
        "by_effective_year": {str(year): summary([r for r in observations if r[0].year == year])
                              for year in (2025, 2026)},
    }


def thresholds(rows):
    return [percentile([r[i] for r in rows], 95) for i in (1, 2)]


def summary(rows):
    n = len(rows)
    if not n:
        raise ValueError("No complete test rows")
    events = sum(r[1] for r in rows)
    both = {}
    for index, name in ((2, "fixed"), (3, "trailing")):
        flags = sum(r[index] for r in rows)
        hits = sum(r[index] and r[1] for r in rows)
        both[name] = {"flags": flags, "event_hits": hits,
                      "precision_pct": round(hits / flags * 100, 2) if flags else None,
                      "recall_pct": round(hits / events * 100, 2) if events else None}
    return {"sample_count": n, "vix_events": events, "unconditional_event_pct": round(events/n*100, 2),
            "first_effective_date": str(rows[0][0]), "last_effective_date": str(rows[-1][0]), **both}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--cutoff", required=True, type=date.fromisoformat)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.folder, args.cutoff), ensure_ascii=False, indent=2))
