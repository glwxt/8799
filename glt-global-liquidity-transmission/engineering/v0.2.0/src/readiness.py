#!/usr/bin/env python3
"""GLT read-only input readiness report, distinct from scoring coverage.

Input presence is NOT source verification, and neither is an official score.
"""
import argparse
import json
from pathlib import Path
from glt import calculate,timestamp

INPUT_READY = {"valid","uncalibrated","requires_context_review","calibration_leakage","transform_mismatch"}
SCORE_READY = {"valid"}
def assess(root,asof,method_version="V1.0"):
    r=calculate(Path(root),timestamp(asof),method_version=method_version)
    result={}
    totals={"raw_input_points":0,"scorable_points":0,"total_points":0}
    for key in ("L1","L2","L3","L4"):
        rows=[x for x in r["indicators"] if x["layer"]==key]
        total=sum(x["points"] for x in rows)
        raw=sum(x["points"] for x in rows if x["status"] in INPUT_READY)
        scored=sum(x["points"] for x in rows if x["status"] in SCORE_READY)
        result[key]={"raw_input_points":raw,"scorable_points":scored,
                     "total_points":total,
                     "raw_input_coverage":round(raw/total,4),
                     "score_coverage":round(scored/total,4),
                     "publication_qualified":r["layers"][key]["qualified"],
                     "issues":[{"indicator":x["indicator_id"],"weight":x["points"],
                                "status":x["status"]} for x in rows if x["status"]!="valid"]}
        totals["raw_input_points"]+=raw
        totals["scorable_points"]+=scored
        totals["total_points"]+=total
    return {"method_version":method_version,"asof":r["asof"],
            "raw_input_coverage":round(totals["raw_input_points"]/totals["total_points"],4),
            "score_coverage":round(totals["scorable_points"]/totals["total_points"],4),
            "official_publishable":r["publishable"],"layers":result,
            "notes":["Raw input coverage means dated source entries are present within engineering freshness limits; it is not official source verification.",
                     "Score coverage requires calibration or approved context rules and cannot be substituted for raw coverage.",
                     "Official V1.0 context-dependent signals stay qualitative only; V1.1-proposal cannot publish formal scores."]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--asof",required=True)
    p.add_argument("--method-version",choices=("V1.0","V1.1-proposal"),default="V1.0")
    a=p.parse_args()
    print(json.dumps(assess(a.root,a.asof,a.method_version),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
