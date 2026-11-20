import pickle, json, math, statistics, sys
from datetime import datetime, timedelta
from collections import Counter
START = datetime(2026,1,1,10); H = timedelta(hours=1); N = 7728; D = N//24
table, itg = pickle.load(open('cands.pkl','rb'))
KS = [(START+i*H).isoformat() for i in range(N)]
def top(c, n=8): return sorted(c.items(), key=lambda x: -x[1])[:n]
def best(c): return max(c, key=c.get) if c else None
def subs(s):
    """single-digit substitutions of a numeric string"""
    out = []
    for i,ch in enumerate(s):
        if ch.isdigit():
            for d in '0123456789':
                if d != ch: out.append(s[:i]+d+s[i+1:])
    return out
# ---------- day ratio ----------
def sure(c):
    if not c: return None
    b = best(c); return b if c[b] >= 0.9 and c[b] >= 0.8*sum(c.values()) else None
rday = {}
for d in range(D):
    rs = []
    for i in range(d*24, d*24+24):
        v, e = sure(table[KS[i]][0]), sure(table[KS[i]][1])
        if v and e and int(v) > 300: rs.append(int(e)/int(v))
    rday[d] = statistics.median(rs) if len(rs) >= 3 else None
glob = [r for r in rday.values() if r]
for d in range(D):
    if rday[d] is None:
        near = [rday[x] for x in range(max(0,d-5), min(D,d+6)) if rday.get(x)]
        rday[d] = statistics.median(near) if near else statistics.median(glob)
def ratio_ok(v, e, r):
    v, e = int(v), int(e)
    if v == 0: return e == 0
    if v < 5: return abs(e - v*r) <= r
    return abs(e/v - r) <= r*(0.004 + 0.6/v)
# ---------- choose V,E per row ----------
sel = [[None]*6 for _ in range(N)]
flag = [[[] for _ in range(6)] for _ in range(N)]
for i in range(N):
    d = i//24; r = rday[d]; cv, ce = table[KS[i]][0], table[KS[i]][1]
    bestpair = None
    for v, sv in top(cv):
        for e, se in top(ce):
            s = math.log(sv+1e-3) + math.log(se+1e-3) + (0 if ratio_ok(v, e, r) else -6)
            if bestpair is None or s > bestpair[0]: bestpair = (s, v, e)
    if bestpair and bestpair[0] < -5:
        # try repairing one of them via substitution consistent with ratio
        v0, e0 = best(cv), best(ce); fixes = []
        if v0 and e0:
            fixes += [(v, e0, 'V') for v in subs(v0) if ratio_ok(v, e0, r)]
            fixes += [(v0, e, 'E') for e in subs(e0) if ratio_ok(v0, e, r)]
        if len(fixes) == 1:
            bestpair = (0, fixes[0][0], fixes[0][1]); flag[i][0 if fixes[0][2]=='V' else 1].append('ratio-fix')
        else:
            flag[i][0].append('ratio?'); flag[i][1].append('ratio?')
    if bestpair: sel[i][0], sel[i][1] = bestpair[1], bestpair[2]
    else:
        sel[i][0], sel[i][1] = best(cv), best(ce)
        if sel[i][0] is None: flag[i][0].append('missing')
        if sel[i][1] is None: flag[i][1].append('missing')
# ---------- F and Vru by priors ----------
for i in range(N):
    v = sel[i][0]
    cf = table[KS[i]][2]
    if v is not None:
        V = int(v)
        def pf(f):
            F = int(f)
            if V == 0: return 0 if F == 0 else -3
            dv = abs(F-V); tol = 0.03*V + 25
            return -(dv/tol)**2 if dv < 4*tol else -8
        cs = top(cf)
        if cs:
            sel[i][2] = max(cs, key=lambda x: math.log(x[1]+1e-3) + pf(x[0]))[0]
            if pf(sel[i][2]) < -4: flag[i][2].append('F/V?')
        else: flag[i][2].append('missing')
    else:
        sel[i][2] = best(cf)
    cr = table[KS[i]][5]
    if v is not None and cr:
        V = int(v)
        def pr(x):
            X = int(x)
            if V == 0: return 0 if X == 0 else -3
            if V < 300: return 0 if X <= 0.04*V+2 else -4
            q = X/V; return -((q-0.0237)/0.002)**2 if 0.015 < q < 0.035 else -8
        sel[i][5] = max(top(cr), key=lambda x: math.log(x[1]+1e-3) + pr(x[0]))[0]
        if pr(sel[i][5]) < -4: flag[i][5].append('Vru?')
    else:
        sel[i][5] = best(cr)
        if sel[i][5] is None: flag[i][5].append('missing')
# Vru second pass using local ratio
for i in range(N):
    if 'Vru?' in flag[i][5]: flag[i][5].remove('Vru?')
for i in range(N):
    v = sel[i][0]; cr = table[KS[i]][5]
    if v is None or not cr or int(v) < 50: continue
    qs = [int(sel[j][5])/int(sel[j][0]) for j in range(max(0,i-4), min(N,i+5)) if j != i and sel[j][0] and sel[j][5] and int(sel[j][0]) >= 50]
    if len(qs) < 3: continue
    q = statistics.median(qs); V = int(v)
    def pr2(x):
        dv = abs(int(x) - q*V); tol = 0.03*q*V + 1.5
        return -(dv/tol)**2 if dv < 4*tol else -8
    sel[i][5] = max(top(cr), key=lambda x: math.log(x[1]+1e-3) + pr2(x[0]))[0]
    if pr2(sel[i][5]) < -1.0: flag[i][5].append('Vru?')
# ---------- P and T by smoothness (2 passes) ----------
for c, sig, cap in ((3, 25.0, 300.0), (4, 0.6, 6.0)):
    for i in range(N): sel[i][c] = best(table[KS[i]][c])
    for _ in range(2):
        for i in range(N):
            nb = [float(sel[j][c]) for j in range(max(0,i-3), min(N,i+4)) if j != i and sel[j][c] is not None]
            cs = top(table[KS[i]][c])
            if not cs:
                if 'missing' not in flag[i][c]: flag[i][c].append('missing')
                continue
            if len(nb) < 2: continue
            med = statistics.median(nb)
            def pp(x):
                dv = abs(float(x)-med)
                return -(dv/sig)**2 if dv < cap else -20
            sel[i][c] = max(cs, key=lambda x: math.log(x[1]+1e-3) + 0.3*pp(x[0]))[0]
    for i in range(N):
        nb = [float(sel[j][c]) for j in range(max(0,i-3), min(N,i+4)) if j != i and sel[j][c] is not None]
        if sel[i][c] is not None and len(nb) >= 2 and abs(float(sel[i][c]) - statistics.median(nb)) > cap/3:
            flag[i][c].append('jump?')
pickle.dump(dict(sel=sel, flag=flag, rday=rday), open('sel.pkl','wb'))
print('flags', Counter(f for row in flag for fl in row for f in fl))
