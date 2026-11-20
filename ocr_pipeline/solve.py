import json, re, itertools, statistics, sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1); N = 7728
R = json.load(open('r2.json')); T = json.load(open('m.json'))
FMT = [r'\d+', r'\d+', r'\d+', r'\d{4}\.\d\d', r'-?\d{1,2}\.\d\d', r'\d+']
def expand(s, alts, maxn=40):
    """expand uncertain chars using alts; returns list of (string, prob)"""
    if s is None: return []
    neg = s.startswith('-'); body = s.lstrip('-')
    digits = [ch for ch in body if ch != '.']
    if len(digits) != len(alts): return [(s, 0.3)] if '#' not in s and 'x' not in s else []
    opts = []
    for ch, al in zip(digits, alts):
        if ch.isdigit(): opts.append([(ch, 1.0)])
        else:
            o = [(a, p) for a, p in al][:3]
            if not o: return []
            opts.append(o)
    out = []
    for combo in itertools.product(*opts):
        st = ''.join(c for c,_ in combo); p = 1.0
        for _,q in combo: p *= q
        if '.' in body: st = st[:-2] + '.' + st[-2:]
        out.append((('-' if neg else '') + st, p))
        if len(out) >= maxn: break
    return out
def cands(k, c):
    sc = Counter()
    for img, vals, alts in R['readings'].get(k, []):
        for s, p in expand(vals[c], alts[c]):
            if re.fullmatch(FMT[c], s): sc[s] += p
    tv = T['cells'].get(k)
    if tv:
        for s, n in tv[c].items():
            if re.fullmatch(FMT[c], s): sc[s] += 0.25*n
    return sc
def icands(k, c):
    sc = Counter()
    for img, vals, alts in R['itog'].get(k, []):
        if c < len(vals):
            for s, p in expand(vals[c], alts[c]):
                if re.fullmatch(FMT[c], s): sc[s] += p
    tv = T['itog'].get(k)
    if tv and c < len(tv):
        for s, n in tv[c].items():
            if re.fullmatch(FMT[c], s): sc[s] += 0.25*n
    return sc
if __name__ == '__main__':
    table = {}
    for i in range(N):
        k = (START+i*H).isoformat()
        table[k] = [cands(k, c) for c in range(6)]
    itg = {}
    for d in range(N//24):
        k = (START+(d*24+23)*H).isoformat()
        itg[k] = [icands(k, c) for c in range(5)]
    import pickle; pickle.dump((table, itg), open('cands.pkl','wb'))
    nocand = sum(1 for k in table for c in range(6) if not table[k][c])
    amb = sum(1 for k in table for c in range(6) if len(table[k][c])>1)
    print('cells without candidates', nocand, 'ambiguous', amb)
    print('itogo days with V cand', sum(1 for k in itg if itg[k][0]))
