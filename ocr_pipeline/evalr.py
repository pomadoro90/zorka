import json, sys, statistics
m = json.load(open(sys.argv[1]))
from collections import defaultdict
day = defaultdict(list)
for k, c in m['cells'].items():
    if c[0] and c[1]:
        v = max(c[0], key=c[0].get); e = max(c[1], key=c[1].get)
        if '#' in v+e or 'x' in v+e: continue
        v, e = int(v), int(e)
        if v > 300: day[k[:10]].append(e/v)
ok = bad = 0
for d, rs in day.items():
    med = statistics.median(rs)
    for r in rs:
        if abs(r/med-1) < 0.0025: ok += 1
        else: bad += 1
print('V/E pairs consistent', ok, 'inconsistent', bad)
