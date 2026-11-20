import json, re, sys
from collections import defaultdict
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); END = datetime(2026,11,19,9); H = timedelta(hours=1)
C = json.load(open('cols.json'))
def to_dt(s):
    if not re.fullmatch(r'\d{10}', s): return None
    dd, mm, yy, hh, mi = int(s[:2]), int(s[2:4]), int(s[4:6]), int(s[6:8]), s[8:]
    if yy != 26 or hh > 23 or mi != '00': return None
    try: dt = datetime(2026, mm, dd, hh)
    except ValueError: return None
    return dt if START <= dt <= END else None
def fmt(c, s):
    neg = s.startswith('-'); s = s.lstrip('-')
    if c in (3,4):
        if len(s) < 3: return None
        s = s[:-2] + '.' + s[-2:]
    return ('-' if neg else '') + s
readings = defaultdict(list)   # dt -> list of (img, [6 strings], [6 alts])
itog = defaultdict(list)
loc = defaultdict(list)
for img, D in sorted(C.items()):
    items = []
    for L in D['lines']:
        cols = [c[0] for c in L['cols']]; alts = [c[1] for c in L['cols']]
        nonempty = [bool(c.strip('-')) for c in cols]
        dig0 = sum(ch.isdigit() for ch in cols[0])
        joined = ''.join(cols)
        if '2011260903' in joined or '1126090303' in joined:
            items.append(dict(kind='other')); continue
        if sum(nonempty[1:]) >= 3 and dig0 >= 4 and cols[0].count('x') <= 4:
            items.append(dict(kind='row', date=to_dt(cols[0]), cols=cols, alts=alts, y=L['y'], x0=L['x0'], x1=L['x1']))
        elif nonempty[1] and not nonempty[6] and dig0 < 6:
            items.append(dict(kind='itogo', cols=cols, alts=alts))
        elif any(nonempty):
            items.append(dict(kind='other'))
    idx = [i for i,r in enumerate(items) if r['kind']=='row']
    dts = [items[i]['date'] for i in idx]
    good = [False]*len(idx)
    for k,dt in enumerate(dts):
        if dt is None: continue
        good[k] = any(j!=k and dts[j] is not None and dts[j]-dt == (j-k)*H for j in range(max(0,k-3), min(len(idx),k+4)))
    res = [dts[k] if good[k] else None for k in range(len(idx))]
    # accept unconfirmed parsed dates that fit the ordering between confirmed ones
    for k in range(len(idx)):
        if res[k] is None and dts[k] is not None:
            prev = next((res[j] for j in range(k-1, -1, -1) if res[j] is not None), None)
            nxt = next((dts[j] for j in range(k+1, len(idx)) if good[j]), None)
            if (prev is None or dts[k] > prev) and (nxt is None or dts[k] < nxt) and \
               (prev is None or dts[k] - prev <= 4*H) and (nxt is None or nxt - dts[k] <= 4*H):
                res[k] = dts[k]
    gk = [k for k in range(len(idx)) if res[k] is not None]
    for a,b in zip(gk, gk[1:]):
        if b-a > 1 and res[b]-res[a] == (b-a)*H:
            for k in range(a+1,b): res[k] = res[a] + (k-a)*H
    if gk:
        for k in range(gk[0]): res[k] = res[gk[0]] - (gk[0]-k)*H
        for k in range(gk[-1]+1, len(idx)): res[k] = res[gk[-1]] + (k-gk[-1])*H
    for k,i in enumerate(idx): items[i]['dt'] = res[k]
    prev = None
    for r in items:
        if r['kind']=='row':
            if r['dt'] and START <= r['dt'] <= END:
                readings[r['dt'].isoformat()].append((img, [fmt(c, r['cols'][c+1]) for c in range(6)], r['alts'][1:]))
                loc[r['dt'].isoformat()].append((img, r['y'], r['x0'], r['x1']))
            prev = r
        else:
            if r['kind']=='itogo' and prev and prev.get('dt') and prev['dt'].hour == 9:
                itog[prev['dt'].isoformat()].append((img, [fmt(c, r['cols'][c+1]) for c in range(5)], r['alts'][1:6]))
            prev = None
json.dump(dict(readings=readings, itog=itog), open('r2.json','w'))
json.dump(loc, open('loc.json','w'))
n = int((END-START)/H)+1
miss = [START+i*H for i in range(n) if (START+i*H).isoformat() not in readings]
print('hours with readings', len(readings), 'missing', len(miss), 'itogo days', len(itog))
r=[]
for t in miss:
    if r and t-r[-1][1]==H: r[-1][1]=t
    else: r.append([t,t])
print([(str(a),int((b-a)/H)+1) for a,b in r][:60])
