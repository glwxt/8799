#!/usr/bin/env python3
"""GLT V1.0 strict point-in-time scoring engine. Engineering v0.2.0."""
import argparse, csv, datetime as dt, json, math
from pathlib import Path
LAYERS={'L1':30,'L2':25,'L3':20,'L4':25}
REQUIRED_FIELDS=('indicator_id','observation_date','published_at','value','unit','source_url','retrieved_at','revision','transform')
def readcsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def timestamp(s):
    v=dt.datetime.fromisoformat(s.replace('Z','+00:00'))
    if v.tzinfo is None:raise ValueError('Timezone required: '+s)
    return v
def qualified_state(score):
    if score is None:return None
    if score>=80:return '强势宽松'
    if score>=65:return '温和宽松'
    if score>=45:return '中性震荡'
    if score>=30:return '温和收紧'
    return '强势收紧'
def calculate(root,asof):
    if isinstance(asof,dt.date) and not isinstance(asof,dt.datetime):raise ValueError('Datetime with timezone required')
    if asof.tzinfo is None:raise ValueError('Timezone-aware asof required')
    root=Path(root);cfg=readcsv(root/'config/indicators.csv');obs=readcsv(root/'data/observations.csv');cal=readcsv(root/'data/calibration.csv')
    if len(cfg)!=19 or len({x['indicator_id'] for x in cfg})!=len(cfg):raise ValueError('Expected 19 unique indicators')
    for layer,total in LAYERS.items():
        if sum(int(x['points']) for x in cfg if x['layer']==layer)!=total:raise ValueError('Invalid layer weights '+layer)
    if len({x['indicator_id'] for x in cal})!=len(cal):raise ValueError('Duplicate calibration')
    bycal={x['indicator_id']:x for x in cal};known={x['indicator_id'] for x in cfg};latest={}
    for x in obs:
        if not all(k in x for k in REQUIRED_FIELDS):raise ValueError('Observation columns incomplete')
        k=x['indicator_id']
        if k not in known:raise ValueError('Unknown indicator '+k)
        if not x['source_url'] or not x['unit']:continue
        date=dt.date.fromisoformat(x['observation_date']);pub=timestamp(x['published_at']);retr=timestamp(x['retrieved_at'])
        if pub>retr or pub>asof or retr>asof or date>asof.date():continue
        pair=(date,pub,retr)
        if k not in latest or pair>latest[k][0]:latest[k]=(pair,x)
    indicators=[];layers={};valid_points=0
    for layer,total in LAYERS.items():
        earned=0.;points=0
        for c in (x for x in cfg if x['layer']==layer):
            k=c['indicator_id'];w=int(c['points']);status='missing';score=None;ob=latest.get(k);data=ob[1] if ob else None
            if data is not None:
                date=dt.date.fromisoformat(data['observation_date']);age=(asof.date()-date).days
                if age>int(c['max_age_days']):status='stale'
                elif data['unit']!=c['unit']:status='unit_mismatch'
                elif c['direction']=='context':status='requires_context_review'
                else:
                    ca=bycal.get(k)
                    if not ca or not all(ca.get(z) for z in ('p05','p95','lookback_start','lookback_end','version','transform')):status='uncalibrated'
                    elif ca['transform']!=data['transform']:status='transform_mismatch'
                    elif dt.date.fromisoformat(ca['lookback_end'])>=date:status='calibration_leakage'
                    else:
                        try:
                            lo=float(ca['p05']);hi=float(ca['p95']);v=float(data['value'])
                            if not all(map(math.isfinite,(lo,hi,v))) or hi<=lo:raise ValueError()
                        except (ValueError,TypeError) as e:raise ValueError('Invalid numeric input '+k) from e
                        score=max(0.,min(100.,100*(v-lo)/(hi-lo)))
                        if c['direction']=='negative':score=100-score
                        score=round(score,3);status='valid'
                if status=='valid':points+=w;earned+=w*score
            indicators.append(dict(indicator_id=k,layer=layer,points=w,status=status,score=score,observation_date=data['observation_date'] if data else None,published_at=data['published_at'] if data else None,source_url=data['source_url'] if data else None,unit=data['unit'] if data else None))
        valid_points+=points
        coverage=points/total
        layers[layer]=dict(coverage=round(coverage,4),covered_points=points,total_points=total,qualified=coverage>=.8,score=round(earned/points,3) if points and coverage>=.8 else None)
    publishable=valid_points>=80 and all(x['qualified'] for x in layers.values())
    composite=round(sum(layers[k]['score']*v/100 for k,v in LAYERS.items()),3) if publishable else None
    return dict(asof=asof.isoformat(),method='GLT V1.0 fixed 19-indicator methodology; engineering implementation',coverage=round(valid_points/100,4),covered_points=valid_points,publishable=publishable,quality='部分数据/降低置信度' if 80<=valid_points<90 else ('未达发布门槛' if valid_points<80 else '须进一步核验关键指标'),composite_score=composite,state=qualified_state(composite),layers=layers,indicators=indicators,asset_models={'BTC-GT':None,'GOLD-GT':None,'EQUITY-GT':None},prediction_24h=None,prediction_7d=None,notes=['No imputation. Score is not an upside probability.','Context indicators not auto-scored.','Asset models pending approved weights and calibration.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--asof',required=True);a=p.parse_args()
    result=calculate(a.root,timestamp(a.asof));out=a.root/'reports'/('glt_'+a.asof[:10]+'.json');out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(file=str(out),coverage=result['coverage'],publishable=result['publishable'],composite=result['composite_score']),ensure_ascii=False))
if __name__=='__main__':main()
