import json, sys, statistics
from datetime import datetime, timedelta
H = timedelta(hours=1); START = datetime(2026,1,1,10); N = 7728
m = json.load(open(sys.argv[1]))
def top(c):
    return max(c, key=c.get) if c else None
rows = {}
for i in range(N):
    dt = START + i*H; k = dt.isoformat()
    r = [top(c) for c in m["cells"][k]] if k in m["cells"] else None
    rows[dt] = r if r and None not in r else None
stats = dict(days=0, nod=0, missing_rows=0, vol_ok=0, en_ok=0, fl_ok=0, pr_ok=0, te_ok=0, itog_missing=0)
bad = []
for d in range(N//24):
    t0 = START + d*24*H; ks = [t0 + j*H for j in range(24)]
    stats['days'] += 1
    rr = [rows[k] for k in ks]
    miss = sum(r is None for r in rr); stats['missing_rows'] += miss
    it = m['itog'].get(ks[-1].isoformat())
    if not it: stats['itog_missing'] += 1; bad.append((t0.date(),'no itogo', miss)); continue
    I = [top(c) for c in it]
    if miss: bad.append((t0.date(),'missing rows', miss)); continue
    V = sum(int(r[0]) for r in rr); E = sum(int(r[1]) for r in rr)
    F = sum(int(r[2]) for r in rr)/24; P = sum(float(r[3]) for r in rr)/24; T = sum(float(r[4]) for r in rr)/24
    res = []
    res.append(I[0] is not None and V == int(I[0]))
    if I[0] == '0' and V == 0:
        res += [E==0, F==0, True, True]
    else:
        res.append(I[1] is not None and E == int(I[1]))
        res.append(I[2] is not None and abs(F-int(I[2])) < 1)
        try: res.append(abs(P-float(I[3])) < 0.0051)
        except: res.append(False)
        try: res.append(abs(T-float(I[4])) < 0.0051)
        except: res.append(False)
    for key, ok in zip(['vol_ok','en_ok','fl_ok','pr_ok','te_ok'], res): stats[key] += ok
    if not all(res): bad.append((t0.date(), res, V, I[0], E, I[1], round(F,2), I[2], round(P,3), I[3], round(T,3), I[4]))
print(stats)
for b in bad[:int(sys.argv[2]) if len(sys.argv)>2 else 40]: print(b)
