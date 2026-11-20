#!/usr/bin/env python3
"""Audit GLT original 19-indicator weights and scoring-data readiness."""
import json,argparse
from pathlib import Path
from glt import calculate,timestamp
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--asof',required=True);a=p.parse_args()
 r=calculate(a.root,timestamp(a.asof));print(json.dumps({'asof':r['asof'],'coverage':r['coverage'],'publishable':r['publishable'],'unavailable':{x['indicator_id']:x['status'] for x in r['indicators'] if x['status']!='valid'}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
