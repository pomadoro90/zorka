import json, sys
from datetime import datetime
M = json.load(open('manual.json')); M.setdefault('cells', {}); M.setdefault('itog', {}); M.setdefault('reviewed', [])
for line in sys.stdin:
    p = line.split()
    if not p: continue
    k = p[0]
    if len(k) == 8: k = '2026-' + k[:5] + 'T' + k[6:8] + ':00:00'   # MM-DDTHH
    datetime.fromisoformat(k)
    vals = p[1:]
    if vals[0] == 'ITOGO':
        M['itog'][k] = [None if v == '-' else v for v in vals[1:]]; continue
    assert len(vals) == 6, line
    M['cells'].setdefault(k, {}).update({str(c): v for c, v in enumerate(vals) if v != '?'})
json.dump(M, open('manual.json','w'), indent=0)
print(len(M['cells']), 'manual rows')
