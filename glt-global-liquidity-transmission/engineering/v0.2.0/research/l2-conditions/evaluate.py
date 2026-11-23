"""Audit GLT L2 research candidates with same-day source observations."""
import argparse
import csv
import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path


def fred(path, series):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return {date.fromisoformat(r["observation_date"]): Decimal(r[series])
                for r in csv.DictReader(file) if r[series] not in ("", ".")}


def reference_rates(path, kind):
    rows = json.loads(path.read_text(encoding="utf-8"))["refRates"]
    result = {}
    for row in rows:
        if row["type"] != kind or row.get("percentRate") is None:
            continue
        day = date.fromisoformat(row["effectiveDate"])
        if day in result:
            raise ValueError(f"Duplicate {kind} date: {day}")
        if row.get("revisionIndicator") not in (None, "", False):
            continue
        result[day] = Decimal(str(row["percentRate"]))
    return result


def percentile(values, fraction):
    values = sorted(values)
    if not values:
        raise ValueError("Empty calibration sample")
    rank = max(0, (len(values) * fraction + 99) // 100 - 1)
    return values[rank]


def analyse(folder, cutoff):
    rate_files = ("sofr.json", "effr.json", "iorb.csv", "DGS10.csv", "DFII10.csv", "T10YIE.csv")
    sofr = reference_rates(folder / rate_files[0], "SOFR")
    effr = reference_rates(folder / rate_files[1], "EFFR")
    iorb = fred(folder / rate_files[2], "IORB")
    funding = {
        d: (int((sofr[d] - iorb[d]) * 100), int((effr[d] - iorb[d]) * 100))
        for d in sorted(sofr.keys() & effr.keys() & iorb.keys()) if d <= cutoff
    }
    train = [v for d, v in funding.items() if d.year < 2025]
    test = {d: v for d, v in funding.items() if d.year >= 2025}
    secure_cut, unsecured_cut = (percentile([row[i] for row in train], 95) for i in range(2))
    # A strictly greater value avoids counting every observation tied at the reference percentile.
    high_secured = [d for d, (s, _) in test.items() if s > secure_cut]
    high_unsecured = [d for d, (_, u) in test.items() if u > unsecured_cut]
    joint = sorted(set(high_secured) & set(high_unsecured))
    latest_funding = max(funding)

    nominal = fred(folder / "DGS10.csv", "DGS10")
    real = fred(folder / "DFII10.csv", "DFII10")
    breakeven = fred(folder / "T10YIE.csv", "T10YIE")
    common = sorted(d for d in nominal.keys() & real.keys() & breakeven.keys() if d <= cutoff)
    checks = [abs((nominal[d] - real[d] - breakeven[d]) * 100) for d in common]
    prior, latest = common[-2:]
    return {
        "asof_observation_date": cutoff.isoformat(),
        "eligible_for_official_score": False,
        "source_sha256": {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in rate_files},
        "funding": {
            "latest_common_date": latest_funding.isoformat(),
            "latest_spreads_bp_secured_unsecured": list(funding[latest_funding]),
            "training_size_before_2025": len(train),
            "evaluation_size_from_2025": len(test),
            "training_p95_bp_secured_unsecured": [secure_cut, unsecured_cut],
            "evaluation_strict_upper_tail_counts": [len(high_secured), len(high_unsecured)],
            "joint_upper_tail_count": len(joint),
            "joint_upper_tail_dates": [d.isoformat() for d in joint],
            "november_23_has_complete_same_day_inputs": date(2026, 11, 23) in funding,
        },
        "yield_decomposition": {
            "common_observations": len(common), "max_identity_residual_bp": str(max(checks)),
            "latest_common_date": latest.isoformat(), "previous_common_date": prior.isoformat(),
            "percentage_levels_nominal_real_breakeven": [str(x[latest]) for x in (nominal, real, breakeven)],
            "change_bp_nominal_real_breakeven": [str((x[latest] - x[prior])*100)
                                                  for x in (nominal, real, breakeven)],
        }
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_folder", type=Path)
    parser.add_argument("--cutoff", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    print(json.dumps(analyse(args.source_folder, args.cutoff), indent=2))
