#!/usr/bin/env python3
"""Inspect forecast accuracy without altering historic forecast or outcome rows."""
import argparse,collections,json
from pathlib import Path
from forecast import read
DIRECTIONS=['偏多','震荡偏多','震荡','震荡偏空','偏空']
def evaluate(root):
 forecasts=read(root/'logs/forecasts.jsonl');outcomes={x['id']:x for x in read(root/'logs/outcomes.jsonl')}
 groups=collections.defaultdict(lambda:{'total':0,'exact':0,'by_direction':collections.defaultdict(lambda:{'total':0,'exact':0})})
 for f in forecasts:
  out=outcomes.get(f['id'])
  if not out:continue
  g=groups[(f['model'],f['horizon'])];g['total']+=1
  exact=f['direction']==out['observed_direction'];g['exact']+=int(exact)
  by=g['by_direction'][f['direction']];by['total']+=1;by['exact']+=int(exact)
 results={}
 for key,g in groups.items():
  results['/'.join(key)]={'count':g['total'],'exact_rate':round(g['exact']/g['total'],4) if g['total']>=30 else None,'warning':'样本不足，需至少30笔配对结果' if g['total']<30 else '仅描述性命中率，未完成与基准模型比较','by_direction':{k:dict(v) for k,v in g['by_direction'].items()}}
 return {'forecast_count':len(forecasts),'outcome_count':len(outcomes),'results':results}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();print(json.dumps(evaluate(a.root),ensure_ascii=False,indent=2))
