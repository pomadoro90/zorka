import json, sys
L = json.load(open('loc.json')); R = json.load(open('r2.json'))
for a in sys.argv[1:]:
    k = '2026-' + a[:5] + 'T' + a[6:8] + ':00:00'
    print(a, [(r[0][-6:], r[1]) for r in R['readings'].get(k, [])], [round(x[1]) for x in L.get(k, [])])
