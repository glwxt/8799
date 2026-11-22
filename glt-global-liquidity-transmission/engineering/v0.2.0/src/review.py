#!/usr/bin/env python3
"""Inspect forecast accuracy without altering historic forecast or outcome rows."""
import argparse,collections,json
from pathlib import Path
from datetime import datetime, timezone
from price_review import PROTOCOL, timestamp
from forecast import read
DIRECTIONS=['偏多','震荡偏多','震荡','震荡偏空','偏空']
def price_summary(forecasts, outcomes, asof):
    groups = {}
    for forecast in forecasts:
        if forecast.get("protocol") != PROTOCOL or timestamp(forecast["issued_at"]) > asof:
            continue
        benchmark = forecast["benchmark"]
        key = "/".join((forecast["model"], forecast["horizon"],
                        benchmark["instrument"], benchmark["series_id"],
                        benchmark["neutral_pct"], benchmark["price_type"], benchmark["unit"]))
        group = groups.setdefault(key, {
            "due": 0, "pending": 0, "missing_quote": 0, "scored": 0,
            "hits": 0, "neutral_baseline_hits": 0, "by_direction": {},
        })
        if timestamp(benchmark["maturity_at"]) > asof:
            group["pending"] += 1
            continue
        group["due"] += 1
        outcome = outcomes.get(forecast["id"])
        if (outcome is None or outcome.get("protocol") != PROTOCOL
                or timestamp(outcome["evaluated_at"]) > asof):
            group["missing_quote"] += 1
            continue
        group["scored"] += 1
        group["hits"] += int(outcome["exact_match"])
        group["neutral_baseline_hits"] += int(outcome["observed_direction"] == "震荡")
        direction = group["by_direction"].setdefault(
            outcome["expected_direction"], {"count": 0, "hits": 0}
        )
        direction["count"] += 1
        direction["hits"] += int(outcome["exact_match"])
    for group in groups.values():
        count = group["scored"]
        group["sample_status"] = "样本不足" if count < 30 else "描述性统计"
        group["hit_rate"] = round(group["hits"] / count, 4) if count >= 30 else None
        group["neutral_baseline_rate"] = (
            round(group["neutral_baseline_hits"] / count, 4) if count >= 30 else None
        )
    return groups


def evaluate(root, asof=None):
 forecasts=read(root/'logs/forecasts.jsonl');outcomes={x['id']:x for x in read(root/'logs/outcomes.jsonl')}
 groups=collections.defaultdict(lambda:{'total':0,'exact':0,'by_direction':collections.defaultdict(lambda:{'total':0,'exact':0})})
 for f in forecasts:
  if f.get('protocol') == PROTOCOL:continue
  out=outcomes.get(f['id'])
  if not out:continue
  g=groups[(f['model'],f['horizon'])];g['total']+=1
  exact=f['direction']==out['observed_direction'];g['exact']+=int(exact)
  by=g['by_direction'][f['direction']];by['total']+=1;by['exact']+=int(exact)
 results={}
 for key,g in groups.items():
  results['/'.join(key)]={'count':g['total'],'exact_rate':round(g['exact']/g['total'],4) if g['total']>=30 else None,'warning':'样本不足，需至少30笔配对结果' if g['total']<30 else '仅描述性命中率，未完成与基准模型比较','by_direction':{k:dict(v) for k,v in g['by_direction'].items()}}
 return {'forecast_count':len(forecasts),'outcome_count':len(outcomes),'results':results,'price_review':price_summary(forecasts,outcomes,asof or datetime.now(timezone.utc))}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();print(json.dumps(evaluate(a.root),ensure_ascii=False,indent=2))
