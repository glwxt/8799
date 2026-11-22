#!/usr/bin/env python3
"""Append-only forecast ledger; separate append-only outcome log."""
import argparse,datetime,hashlib,json
from pathlib import Path
from price_review import PROTOCOL, calculate_outcome, lock_benchmark, number, required_text
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
    r=sub.add_parser('result');r.add_argument('--id',required=True);r.add_argument('--evaluated-at',required=True)
    p.add_argument('--benchmark',type=Path,help='JSON price benchmark for the locked review protocol')
    r.add_argument('--quote',type=Path,help='JSON observation for a locked price forecast')
    r.add_argument('--observed-direction',choices=DIRECTIONS)
    r.add_argument('--evidence')
    args=ap.parse_args();root=Path(args.root);fl=root/'logs/forecasts.jsonl';ol=root/'logs/outcomes.jsonl'
    if args.command=='predict':
        if not 0<=args.confidence<=1:ap.error('Confidence must be 0..1')
        dt=datetime.datetime.fromisoformat(args.asof)
        if dt.tzinfo is None:ap.error('--asof must include timezone offset')
        uid=hashlib.sha256(f'{args.model}|{args.horizon}|{args.asof}'.encode()).hexdigest()[:16]
        doc={'id':uid,'model':args.model,'horizon':args.horizon,'direction':args.direction,'confidence':args.confidence,'basis':args.basis,'asof':args.asof,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        if args.benchmark:
            try:
                data = json.loads(args.benchmark.read_text(encoding='utf-8'))
                issued_at = datetime.datetime.now(datetime.timezone.utc)
                score = data.get('score')
                if score is None:
                    doc['score_missing_reason'] = required_text(data, 'score_missing_reason')
                elif not 0 <= number(score) <= 100:
                    raise ValueError("Score must be between 0 and 100")
                else:
                    doc['score'] = str(number(score))
                doc.update(
                    protocol=PROTOCOL, method_version='V1.0',
                    report_id=required_text(data, 'report_id'), issued_at=issued_at.isoformat(),
                    benchmark=lock_benchmark(data, args.asof, args.horizon, issued_at),
                )
            except (OSError, KeyError, TypeError, ValueError) as exc:
                ap.error(str(exc))
        if args.benchmark:
            identity = [args.model, args.horizon, dt.astimezone(datetime.timezone.utc).isoformat(),
                        doc['benchmark']['series_id'], doc['benchmark']['instrument'], PROTOCOL]
            uid = hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:16]
            doc['id'] = uid
        if any(x['id'] == uid for x in read(fl)):
            ap.error('Immutable prediction already exists')
        append_jsonl(fl,doc);print(uid)
    else:
        f=next((x for x in read(fl) if x['id']==args.id),None)
        if f is None:ap.error('No such prediction')
        if any(x['id']==args.id for x in read(ol)):ap.error('Outcome already appended')
        if f.get('protocol') == PROTOCOL:
            if args.quote is None or args.observed_direction is not None or args.evidence is not None:
                ap.error('Locked forecasts require --quote and calculate their own direction')
            try:
                quote = json.loads(args.quote.read_text(encoding='utf-8'))
                outcome = calculate_outcome(f, quote, args.evaluated_at)
            except (OSError, KeyError, TypeError, ValueError) as exc:
                ap.error(str(exc))
            append_jsonl(ol, outcome)
            print('Outcome appended')
            return
        if args.quote is not None or args.observed_direction is None or not args.evidence:
            ap.error('Legacy forecasts require --observed-direction and --evidence')
        edt=datetime.datetime.fromisoformat(args.evaluated_at);pdt=datetime.datetime.fromisoformat(f['asof'])
        if edt.tzinfo is None or edt < pdt+datetime.timedelta(hours=24 if f['horizon']=='24h' else 168):ap.error('Result before completed horizon / missing timezone')
        append_jsonl(ol,{'id':args.id,'observed_direction':args.observed_direction,'evidence':args.evidence,'evaluated_at':args.evaluated_at,'exact_match':args.observed_direction==f['direction']})
        print('Outcome appended')
if __name__=='__main__':main()
