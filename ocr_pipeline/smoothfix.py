import pickle, json, statistics
from datetime import datetime, timedelta
S=datetime(2026,1,1,10); H=timedelta(hours=1)
F=pickle.load(open('final.pkl','rb')); sel=F['sel']
pairs={'3':'8','8':'3','5':'6','6':'5','1':'7','7':'1','0':'8','9':'8','6':'8'}
out=[]
for c,thr,ok in ((4,0.25,0.08),(3,40,12)):
    for i in range(len(sel)):
        v=sel[i][c]
        if v is None: continue
        nb=[float(sel[j][c]) for j in (i-2,i-1,i+1,i+2) if 0<=j<len(sel) and sel[j][c] is not None]
        if len(nb)<3: continue
        med=statistics.median(nb)
        if abs(float(v)-med)<=thr: continue
        best=None
        for p,ch in enumerate(v):
            for d in '0123456789':
                if d==ch or not ch.isdigit(): continue
                w=v[:p]+d+v[p+1:]
                e=abs(float(w)-med)
                if e<=ok and (best is None or e<best[0]): best=(e,w)
        out.append(((S+i*H).isoformat()[5:13],c,v,round(med,2),best and best[1]))
for o in out: print(o)
print(len(out))
