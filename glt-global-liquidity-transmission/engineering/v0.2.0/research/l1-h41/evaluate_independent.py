import csv
import sys

import numpy as np

with open(sys.argv[1], newline="", encoding="utf-8") as source:
    rows=list(csv.DictReader(source))
actual=np.array([float(r["reserves_change"]) for r in rows[13:]])
results={}
for name in ("baseline","mbs_change","on_rrp_weekly_mean_change"):
    columns=["reserves_change","tga_change"]
    if name!="baseline":
        columns.append(name)
    X=np.array([[float(r[k]) for k in columns] for r in rows[:-1]])
    y=np.array([float(r["reserves_change"]) for r in rows[1:]])
    preds=[]
    for ix in range(12,len(y)):
        train=X[:ix]
        mean,sd=train.mean(0),train.std(0)
        sd[sd==0]=1
        design=np.column_stack((np.ones(ix),(train-mean)/sd))
        coeff=np.linalg.solve(design.T@design+np.diag([0]+[1]*len(columns)),design.T@y[:ix])
        preds.append(np.r_[1,(X[ix]-mean)/sd]@coeff)
    errors=np.abs(actual-preds)
    results[name]=errors
    print(name, errors.mean(),np.sum(np.sign(actual)==np.sign(preds)))
    if name!="baseline":
        diff=results["baseline"]-errors
        print("better weeks",sum(diff>0),"average gain excluding largest gain",np.delete(diff,np.argmax(diff)).mean())
