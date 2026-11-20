#!/usr/bin/env python3
"""Download FRED graph CSV into staging ONLY. Dates do not establish release vintages.
Fix 2026-11-21 (local, v0.2.0): direct download from this VM timed out twice
(urllib 25s, curl 40s, 0 bytes) on 2026-11-21; timeout raised to 60s with
3 attempts and exponential backoff. VIXCLS added: indicators.csv lists the
vix source as VIX_CBOE, whose FRED series is VIXCLS (CBOE Volatility Index
close). Staging files present here were fetched via browser on 2026-11-21
00:27 CST (windowed 2025-11-01 to 2026-11-20) because the direct path stayed
unreachable; see run log glt-engineering-v020-run-2026-11-21.md."""
import argparse,urllib.request,urllib.parse,pathlib,datetime as dt,json,csv,io,time
ALLOWED={'WRESBAL','RRPONTSYD','WALCL','DFII10','DGS10','BAMLH0A0HYM2','VIXCLS'}
TIMEOUT=60
ATTEMPTS=3
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);p.add_argument('--series',choices=sorted(ALLOWED),required=True);a=p.parse_args()
 url='https://fred.stlouisfed.org/graph/fredgraph.csv?'+urllib.parse.urlencode({'id':a.series})
 req=urllib.request.Request(url,headers={'User-Agent':'GLT-data-staging/0.2'})
 last=None
 for attempt in range(1,ATTEMPTS+1):
  try:
   with urllib.request.urlopen(req,timeout=TIMEOUT) as r:body=r.read()
   break
  except Exception as e:
   last=e
   if attempt<ATTEMPTS:time.sleep(5*attempt)
 else:
  raise RuntimeError(f'FRED download failed after {ATTEMPTS} attempts (timeout {TIMEOUT}s): {last}')
 rows=list(csv.reader(io.StringIO(body.decode('utf-8-sig'))))
 if not rows or len(rows[0])<2:raise ValueError('Unexpected CSV')
 dest=a.root/'staging';dest.mkdir(exist_ok=True,parents=True);(dest/(a.series+'.csv')).write_bytes(body)
 meta={'series':a.series,'retrieved_at':dt.datetime.now(dt.timezone.utc).isoformat(),'url':url,'attempts':attempt,'note':'For historical analysis only; DO NOT promote to observations.csv without original release timestamp, unit, transformation, and revision-vintage verification.'}
 (dest/(a.series+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':main()
