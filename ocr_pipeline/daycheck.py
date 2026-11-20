import pickle, json, math, sys
from collections import Counter
sys.path.insert(0, 'scripts')
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1); N = 7728; D = N//24
table, itg = pickle.load(open('cands.pkl','rb'))
S = pickle.load(open('sel.pkl','rb')); sel, flag, rday = S['sel'], S['flag'], S['rday']
over = json.load(open('manual.json')) if len(sys.argv) > 1 else {}
KS = [(START+i*H).isoformat() for i in range(N)]
for k, vals in over.get('cells', {}).items():
    i = KS.index(k)
    for c, v in vals.items(): sel[i][int(c)] = v; flag[i][int(c)] = ['manual']
def top(c, n=8): return sorted(c.items(), key=lambda x: -x[1])[:n]
def subs(s):
    out = []
    for i,ch in enumerate(s):
        if ch.isdigit():
            for d in '0123456789':
                if d != ch and not (i == 0 and d == '0' and len(s.lstrip('-')) > 1): out.append(s[:i]+d+s[i+1:])
    return out
def ratio_ok(v, e, r):
    v, e = int(v), int(e)
    if v == 0: return e == 0
    if v < 5: return abs(e - v*r) <= r
    return abs(e/v - r) <= r*(0.004 + 0.6/v)
report = []; stat = Counter()
itog_final = {}
for d in range(D):
    ids = list(range(d*24, d*24+24)); k9 = KS[ids[-1]]
    I = [max(c, key=c.get) if c else None for c in itg[k9]]
    if k9 in over.get('itog', {}): I = over['itog'][k9]
    # residual fill for V/E
    if I[0] not in (None,) and I[1] is not None or (I[0] == '0'):
        sus = {c: [i for i in ids if sel[i][c] is None or 'ratio?' in flag[i][c]] for c in (0,1)}
        res = {}
        for c in (0,1):
            if I[c] is None: continue
            if len(sus[c]) == 1:
                i = sus[c][0]
                others = [int(sel[j][c]) for j in ids if j != i and sel[j][c] is not None]
                if len(others) == 23: res[c] = (i, str(int(I[c]) - sum(others)))
        if 0 in res and 1 in res and res[0][0] == res[1][0]:
            i = res[0][0]; v, e = res[0][1], res[1][1]
            if int(v) >= 0 and int(e) >= 0 and ratio_ok(v, e, rday[d]):
                sel[i][0], sel[i][1] = v, e; flag[i][0] = ['residual']; flag[i][1] = ['residual']; stat['resid2'] += 1
        else:
            for c, (i, val) in res.items():
                oc = sel[i][1-c]
                if oc is not None and int(val) >= 0 and 'ratio?' not in flag[i][1-c] or (oc is not None and int(val) >= 0 and len(sus[1-c]) != 1):
                    v, e = (val, oc) if c == 0 else (oc, val)
                    if ratio_ok(v, e, rday[d]):
                        sel[i][c] = val; flag[i][c] = ['residual']; stat['resid%d'%c] += 1
                        if 'ratio?' in flag[i][1-c]: flag[i][1-c].remove('ratio?')
    rows = [sel[i] for i in ids]
    if any(r[c] is None for r in rows for c in range(5)):
        miss = [(KS[i], c) for i in ids for c in range(5) if sel[i][c] is None]
        report.append((d, 'incomplete', miss)); stat['incomplete'] += 1; itog_final[d] = I; continue
    zero = all(int(r[0]) == 0 for r in rows)
    if zero and (I[0] in (None, '0') or (len(I[0]) <= 2 and all(x is None for x in I[1:]))):
        if I[0] not in (None, '0'): stat['zero-itogo-misread'] += 1
        I = ['0', None, None, None, None]
    itog_final[d] = I
    probs = []
    # ---- V ----
    def sumc(c, f=int): return sum(f(sel[i][c]) for i in ids)
    for c, f in ((0, int), (1, int)):
        if I[c] is None:
            if not zero: probs.append((c, 'no itogo'))
            continue
        diff = int(I[c]) - sumc(c)
        if diff == 0: continue
        oc = 1 - c; fixes = []
        for i in ids:
            cur = sel[i][c]
            alts = set(x for x,_ in top(table[KS[i]][c], 12)) | set(subs(cur))
            for a in alts:
                if int(a) - int(cur) == diff:
                    v, e = (a, sel[i][1]) if c == 0 else (sel[i][0], a)
                    if ratio_ok(v, e, rday[d]): fixes.append((i, a))
        if len(fixes) == 1:
            i, a = fixes[0]; sel[i][c] = a; flag[i][c].append('sum-fix'); stat['fix%d'%c] += 1
        else:
            # maybe itogo misread: if all rows ratio-consistent, check itogo variants
            probs.append((c, 'sum mismatch %d (fixes %d)' % (diff, len(fixes))))
    zero = all(int(sel[i][0]) == 0 for i in ids)
    if zero:
        probs = [p for p in probs if p[1] != 'no itogo']
        stat['zero-day'] += 1
    else:
        aids = [i for i in ids if int(sel[i][0]) > 0] or ids; n = len(aids)
        def sumA(c): return sum(int(sel[i][c]) for i in aids)
        # ---- F ----
        if I[2] is not None:
            F = sumA(2)/n
            if abs(F - int(I[2])) >= max(1.5, 0.0025*int(I[2])):
                lo, hi = (int(I[2]) - 0.5)*n - sumA(2), (int(I[2]) + 1)*n - sumA(2)
                fixes = []
                for i in aids:
                    cur = sel[i][2]; V = int(sel[i][0])
                    for a in set(x for x,_ in top(table[KS[i]][2], 12)) | set(subs(cur)):
                        dlt = int(a) - int(cur)
                        if lo <= dlt < hi and (V == 0 and int(a) == 0 or V > 0 and abs(int(a)/max(V,1)-1) < 0.06): fixes.append((i, a))
                if len(fixes) == 1:
                    i, a = fixes[0]; sel[i][2] = a; flag[i][2].append('avg-fix'); stat['fixF'] += 1
                else: probs.append((2, 'avg mismatch %.2f vs %s (fixes %d)' % (F, I[2], len(fixes))))
        else: probs.append((2, 'no itogo'))
        # ---- P, T ----
        for c, unit in ((3, 0.01), (4, 0.01)):
            if I[c] is None: probs.append((c, 'no itogo')); continue
            tot = sum(float(sel[i][c]) for i in aids)
            if abs(tot/n - float(I[c])) < 0.0111:
                if abs(tot/n - float(I[c])) >= 0.0051: stat['round-tol%d'%c] += 1
                continue
            lo, hi = (float(I[c]) - 0.005)*n - tot, (float(I[c]) + 0.005)*n - tot
            fixes = []
            for j, i in enumerate(aids):
                cur = sel[i][c]
                nb = [float(sel[x][c]) for x in range(max(0,i-2), min(N,i+3)) if x != i and sel[x][c] is not None] or [float(cur)]
                med = sorted(nb)[len(nb)//2]
                for a in set(x for x,_ in top(table[KS[i]][c], 12)) | set(subs(cur)):
                    dlt = float(a) - float(cur)
                    if lo - 1e-9 <= dlt <= hi + 1e-9 and abs(float(a) - med) <= abs(float(cur) - med) + (30 if c == 3 else 0.3):
                        fixes.append((i, a))
            if len(fixes) == 1:
                i, a = fixes[0]; sel[i][c] = a; flag[i][c].append('avg-fix'); stat['fix%d'%c] += 1
            else: probs.append((c, 'avg mismatch %.4f vs %s (fixes %d)' % (tot/n, I[c], len(fixes))))
    if probs: report.append((d, 'problems', probs)); stat['days_with_problems'] += 1
    else: stat['days_ok'] += 1
pickle.dump(dict(sel=sel, flag=flag, itog=itog_final, report=report), open('final.pkl','wb'))
print(stat)
for r in report[:int(sys.argv[2]) if len(sys.argv)>2 else 25]:
    print((START+r[0]*24*H).date(), r[1], r[2][:6])
