import pickle, json, statistics, sys
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1); N = 7728
table, itg = pickle.load(open('cands.pkl','rb'))
def best(c): return max(c, key=c.get) if c else None
def num(s): return float(s) if s is not None else None
def day_keys(d): return [(START+(d*24+j)*H).isoformat() for j in range(24)]
def check_day(rows, I):
    """rows: list of 24 lists of 6 strings; I: 5 strings. returns dict of col->(ok, computed, itogo)"""
    res = {}
    if any(r[c] is None for r in rows for c in range(5)): return None
    V = sum(int(r[0]) for r in rows); E = sum(int(r[1]) for r in rows)
    F = sum(int(r[2]) for r in rows)/24; P = sum(float(r[3]) for r in rows)/24; T = sum(float(r[4]) for r in rows)/24
    res['V'] = (I[0] is not None and V == int(I[0]), V, I[0])
    if I[0] == '0':
        res['E'] = (E == 0, E, '0'); res['F'] = (F == 0, F, '0'); res['P'] = (None, P, None); res['T'] = (None, T, None)
    else:
        res['E'] = (I[1] is not None and E == int(I[1]), E, I[1])
        res['F'] = (I[2] is not None and abs(F-int(I[2])) < 1, F, I[2])
        res['P'] = (I[3] is not None and abs(P-float(I[3])) < 0.006, P, I[3])
        res['T'] = (I[4] is not None and abs(T-float(I[4])) < 0.006, T, I[4])
    return res
if __name__ == '__main__':
    from collections import Counter
    st = Counter(); bad = []
    for d in range(N//24):
        ks = day_keys(d)
        rows = [[best(table[k][c]) for c in range(6)] for k in ks]
        I = [best(itg[ks[-1]][c]) for c in range(5)]
        r = check_day(rows, I)
        if r is None: st['incomplete'] += 1; bad.append((ks[0][:10], 'incomplete')); continue
        for key, v in r.items(): st[key + ('_ok' if v[0] else ('_na' if v[0] is None else '_bad'))] += 1
        if not all(v[0] in (True, None) for v in r.values()): bad.append((ks[0][:10], {k:v for k,v in r.items() if v[0] is False}))
    print(st)
    for b in bad[:int(sys.argv[1]) if len(sys.argv)>1 else 30]: print(b)
