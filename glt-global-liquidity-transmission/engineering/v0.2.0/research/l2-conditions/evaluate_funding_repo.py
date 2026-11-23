"""Compare GLT domestic funding flags against NY Fed overnight repo awards."""
import argparse
import hashlib
import json
from bisect import bisect_right
from collections import defaultdict
from datetime import date
from pathlib import Path

from evaluate import fred, reference_rates
from evaluate_funding_rolling import thresholds


def repo_awards(path, cutoff):
    operations = json.loads(path.read_text(encoding="utf-8"))["repo"]["operations"]
    days = defaultdict(int)
    seen, exercises = set(), []
    for entry in operations:
        day = date.fromisoformat(entry["operationDate"])
        if day > cutoff:
            continue
        identifier = entry["operationId"]
        if identifier in seen or (entry["operationType"], entry["term"], entry["auctionStatus"]) != (
            "Repo", "Overnight", "Results"
        ):
            raise ValueError(f"Unexpected or duplicate operation: {identifier}")
        seen.add(identifier)
        accepted = entry["totalAmtAccepted"]
        if type(accepted) is not int or accepted < 0 or sum(
            item["amtAccepted"] for item in entry["details"]
        ) != accepted:
            raise ValueError(f"Award detail does not reconcile: {identifier}")
        if "exercise" in (entry.get("note") or "").casefold():
            exercises.append({"date": str(day), "accepted_usd": accepted, "operation_id": identifier})
        else:
            days[day] += accepted
    return dict(days), exercises, len(seen)


def compare(rows, threshold):
    events = sum(row[0] >= threshold for row in rows)
    n = len(rows)
    result = {"n": n, "events": events, "event_rate_pct": round(100 * events/n, 2)}
    for label, mask in (
        ("fixed", [row[1] for row in rows]),
        ("rolling", [row[2] for row in rows]),
        ("persistence", [row[3] >= threshold for row in rows]),
    ):
        alerts = sum(mask)
        hits = sum(alert and row[0] >= threshold for alert, row in zip(mask, rows))
        result[label] = {"alerts": alerts, "hits": hits,
                         "precision_pct": round(100 * hits/alerts, 2) if alerts else None,
                         "recall_pct": round(100 * hits/events, 2) if events else None}
    return result


def run(folder, repo_file, cutoff):
    repo, exercises, operations = repo_awards(repo_file, cutoff)
    repo_days = sorted(repo)
    month_ends = {d for d, next_day in zip(repo_days, repo_days[1:]) if d.month != next_day.month}
    sofr = reference_rates(folder / "sofr.json", "SOFR")
    effr = reference_rates(folder / "effr.json", "EFFR")
    iorb = fred(folder / "iorb.csv", "IORB")
    funding = [(d, int((sofr[d] - iorb[d]) * 100), int((effr[d] - iorb[d]) * 100))
               for d in sorted(sofr.keys() & effr.keys() & iorb.keys()) if d <= cutoff]
    fixed = thresholds([r for r in funding if r[0].year < 2025])
    comparisons = []
    for i, (day, secure, unsecure) in enumerate(funding):
        if day.year < 2025 or i < 252 or day not in repo:
            continue
        # Market rates become available the following business morning.
        # Target the second operation date after the underlying transaction date.
        index = bisect_right(repo_days, day) + 1
        if index >= len(repo_days):
            continue
        end = repo_days[index]
        trailing = thresholds(funding[i-252:i])
        comparisons.append((day, end, repo[end], secure > fixed[0] and unsecure > fixed[1],
                            secure > trailing[0] and unsecure > trailing[1], repo[day]))
    largest = sorted(repo, key=repo.get, reverse=True)[:5]
    return {
        "eligible_for_official_score": False, "cutoff": str(cutoff),
        "repo_source_hash": hashlib.sha256(repo_file.read_bytes()).hexdigest(),
        "repo_operations": operations, "exercises": exercises, "regular_operation_dates": len(repo),
        "largest_award_dates": [{"date": str(d), "accepted_usd": repo[d], "month_end": d in month_ends}
                                for d in largest],
        "latest_reg_repo": {"date": str(repo_days[-1]), "accepted_usd": repo[repo_days[-1]]},
        "primary_1bn": compare([r[2:] for r in comparisons], 1_000_000_000),
        "ex_month_end_1bn": compare([r[2:] for r in comparisons if r[1] not in month_ends], 1_000_000_000),
        "sensitivity_5bn": compare([r[2:] for r in comparisons], 5_000_000_000),
        "by_signal_year_1bn": {str(year): compare([r[2:] for r in comparisons if r[0].year == year], 1_000_000_000)
                               for year in (2025, 2026)},
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("rates_folder", type=Path)
    p.add_argument("repo_file", type=Path)
    p.add_argument("--cutoff", type=date.fromisoformat, required=True)
    a = p.parse_args()
    print(json.dumps(run(a.rates_folder, a.repo_file, a.cutoff), indent=2))
