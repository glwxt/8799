#!/usr/bin/env python3
"""Download FRED graph CSV into staging ONLY. Dates do not establish release vintages."""
import argparse,urllib.request,urllib.parse,pathlib,datetime as dt,json,csv,io
ALLOWED={'WRESBAL','RRPONTSYD','WALCL','DFII10','DGS10','BAMLH0A0HYM2'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);p.add_argument('--series',choices=sorted(ALLOWED),required=True);a=p.parse_args()
 url='https://fred.stlouisfed.org/graph/fredgraph.csv?'+urllib.parse.urlencode({'id':a.series})
 req=urllib.request.Request(url,headers={'User-Agent':'GLT-data-staging/0.2'})
 with urllib.request.urlopen(req,timeout=25) as r:body=r.read()
 rows=list(csv.reader(io.StringIO(body.decode('utf-8-sig'))))
 if not rows or len(rows[0])<2:raise ValueError('Unexpected CSV')
 dest=a.root/'staging';dest.mkdir(exist_ok=True,parents=True);(dest/(a.series+'.csv')).write_bytes(body)
 meta={'series':a.series,'retrieved_at':dt.datetime.now(dt.timezone.utc).isoformat(),'url':url,'note':'For historical analysis only; DO NOT promote to observations.csv without original release timestamp, unit, transformation, and revision-vintage verification.'}
 (dest/(a.series+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':main()
