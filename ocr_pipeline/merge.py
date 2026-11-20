import re, glob, os, json, sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from parse import parse_file
OCR = sys.argv[1]
START = datetime(2026,1,1,10); END = datetime(2026,11,19,9)
H = timedelta(hours=1)
FMT = [r'\d+', r'\d+', r'\d+', r'\d{4}\.\d\d', r'-?\d{1,2}\.\d\d', r'\d+']
def to_dt(d):
    dd, mm, yy, hh = d
    if yy != 26 or not (0 <= hh <= 23): return None
    try: dt = datetime(2000+yy, mm, dd, hh)
    except ValueError: return None
    return dt if START <= dt <= END else None
def assign(rows):
    """rows: list of parsed items (row/itogo) in order. assign datetimes to row items."""
    idx = [i for i,r in enumerate(rows) if r['kind']=='row']
    dts = [to_dt(rows[i]['date']) for i in idx]
    good = [False]*len(idx)
    for k,dt in enumerate(dts):
        if dt is None: continue
        ok = False
        for j in range(max(0,k-3), min(len(idx),k+4)):
            if j!=k and dts[j] is not None and dts[j]-dt == (j-k)*H: ok = True
        good[k] = ok
    res = [None]*len(idx)
    for k in range(len(idx)):
        if good[k]: res[k] = dts[k]
    # fill gaps between good anchors when count matches
    gk = [k for k in range(len(idx)) if good[k]]
    for a,b in zip(gk, gk[1:]):
        if b-a > 1 and dts[b]-dts[a] == (b-a)*H:
            for k in range(a+1,b): res[k] = dts[a] + (k-a)*H
    if gk:
        a = gk[0]
        for k in range(a): res[k] = dts[a] - (a-k)*H
        b = gk[-1]
        for k in range(b+1, len(idx)): res[k] = dts[b] + (k-b)*H
    for k,i in enumerate(idx): rows[i]['dt'] = res[k]
    last = None
    for r in rows:
        if r['kind']=='row': last = r.get('dt')
        else:
            r['after'] = last
            last = None
    return rows
cells = defaultdict(lambda: [Counter() for _ in range(6)])
itog = defaultdict(lambda: [Counter() for _ in range(5)])
seen = defaultdict(set)
src = defaultdict(set)
for f in sorted(glob.glob(os.path.join(OCR, '*.txt'))):
    img = os.path.basename(f).split('.')[0]
    rows = assign(parse_file(f))
    for r in rows:
        if r['kind']=='row' and r.get('dt'):
            dt = r['dt']; src[dt].add(img); v = r['vals']
            if len(v)==6:
                for c in range(6):
                    if re.fullmatch(FMT[c], v[c]): cells[dt][c][v[c]] += 1
            seen[dt].add(img)
        elif r['kind'] in ('itogo','other') and r.get('after'):
            dt = r['after']; v = r['vals']
            if dt.hour != 9: continue
            if not (len(v) in (1,5) or r['kind']=='itogo'): continue
            for c in range(min(5,len(v))): itog[dt][c][v[c]] += 1
out = {'cells': {k.isoformat(): [dict(c) for c in v] for k,v in cells.items()},
       'itog': {k.isoformat(): [dict(c) for c in v] for k,v in itog.items()},
       'src': {k.isoformat(): sorted(v) for k,v in src.items()}}
json.dump(out, open(sys.argv[2],'w'))
n = int((END-START)/H)+1
missing = [START+i*H for i in range(n) if (START+i*H) not in cells]
print('rows found', len(cells), 'expected', n, 'missing', len(missing), 'itogo days', len(itog))
