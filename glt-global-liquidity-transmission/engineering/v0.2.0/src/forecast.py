#!/usr/bin/env python3
"""Append-only forecast ledger; separate append-only outcome log."""
import argparse,datetime,hashlib,json
from pathlib import Path
DIRECTIONS=['偏多','震荡偏多','震荡','震荡偏空','偏空']
def append_jsonl(path,doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(doc,ensure_ascii=False,sort_keys=True)+'\n')
def read(path):
    if not path.exists():return []
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('predict');p.add_argument('--model',required=True,choices=['GLT','BTC-GT','GOLD-GT','EQUITY-GT']);p.add_argument('--horizon',required=True,choices=['24h','7d']);p.add_argument('--direction',required=True,choices=DIRECTIONS);p.add_argument('--confidence',type=float,required=True);p.add_argument('--basis',required=True);p.add_argument('--asof',required=True)
    r=sub.add_parser('result');r.add_argument('--id',required=True);r.add_argument('--observed-direction',required=True,choices=DIRECTIONS);r.add_argument('--evidence',required=True);r.add_argument('--evaluated-at',required=True)
    args=ap.parse_args();root=Path(args.root);fl=root/'logs/forecasts.jsonl';ol=root/'logs/outcomes.jsonl'
    if args.command=='predict':
        if not 0<=args.confidence<=1:ap.error('Confidence must be 0..1')
        dt=datetime.datetime.fromisoformat(args.asof)
        if dt.tzinfo is None:ap.error('--asof must include timezone offset')
        uid=hashlib.sha256(f'{args.model}|{args.horizon}|{args.asof}'.encode()).hexdigest()[:16]
        if any(x['id']==uid for x in read(fl)):ap.error('Immutable prediction already exists')
        doc={'id':uid,'model':args.model,'horizon':args.horizon,'direction':args.direction,'confidence':args.confidence,'basis':args.basis,'asof':args.asof,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        append_jsonl(fl,doc);print(uid)
    else:
        f=next((x for x in read(fl) if x['id']==args.id),None)
        if f is None:ap.error('No such prediction')
        if any(x['id']==args.id for x in read(ol)):ap.error('Outcome already appended')
        edt=datetime.datetime.fromisoformat(args.evaluated_at);pdt=datetime.datetime.fromisoformat(f['asof'])
        if edt.tzinfo is None or edt < pdt+datetime.timedelta(hours=24 if f['horizon']=='24h' else 168):ap.error('Result before completed horizon / missing timezone')
        append_jsonl(ol,{'id':args.id,'observed_direction':args.observed_direction,'evidence':args.evidence,'evaluated_at':args.evaluated_at,'exact_match':args.observed_direction==f['direction']})
        print('Outcome appended')
if __name__=='__main__':main()
