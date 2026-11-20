import json, pickle
from collections import Counter, defaultdict
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1)
M = json.load(open('manual.json')); LOC = json.load(open('loc.json')); R = json.load(open('r2.json'))
err = Counter(); tot = Counter(); rows = defaultdict(set)
for k, v in LOC.items():
    for img, *_ in v: rows[img].add(k)
for k, vals in M['cells'].items():
    for img, rv, _ in R['readings'].get(k, []):
        tot[img] += 1
        if any(rv[int(c)] != x for c, x in vals.items()): err[img] += 1
for img in sorted(rows):
    n = len(rows[img]); rev = sum(1 for k in rows[img] if k in M['cells'])
    if err[img] >= 3: print(img, 'rows', n, 'reviewed', rev, 'errors', err[img])
