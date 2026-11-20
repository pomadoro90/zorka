import json, re
from datetime import datetime, timedelta
H = timedelta(hours=1)
M = json.load(open('manual.json')); R = json.load(open('r2.json'))
def sim(a, b):
    if a is None or b is None: return 0
    a2 = re.sub(r'[^0-9]', '', a); b2 = re.sub(r'[^0-9#x]', '', b)
    if len(a2) != len(b2): return 0
    return sum(1 for x, y in zip(a2, b2) if x == y) / len(a2)
bad = []
for k, vals in sorted(M['cells'].items()):
    t = datetime.fromisoformat(k)
    for c in ('3', '4'):
        if c not in vals: continue
        v = vals[c]
        own = max([sim(v, r[1][int(c)]) for r in R['readings'].get(k, [])] or [None], key=lambda x: x or 0)
        nb = []
        for d in (-1, 1):
            k2 = (t + d*H).isoformat()
            s = max([sim(v, r[1][int(c)]) for r in R['readings'].get(k2, [])] or [0])
            nb.append(s)
        if own is not None and max(nb) > own and max(nb) >= 0.8:
            bad.append((k, c, v, own, nb))
for b in bad: print(b)
print(len(bad))
