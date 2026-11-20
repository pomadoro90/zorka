import pickle, numpy as np, os, sys, json
from collections import defaultdict
R = pickle.load(open('pred.pkl','rb'))
P, cls = R['P'], list(R['cls'])
TH = float(sys.argv[1]) if len(sys.argv)>1 else 0.6
by = defaultdict(dict)
for i,(f,li,ii) in enumerate(R['meta']): by[f][(li,ii)] = i
def chars(f, mp, li, its):
    res = []
    for ii, it in enumerate(its):
        i = mp[(li,ii)]; p = P[i]; o = np.argsort(-p)
        top = cls[o[0]]; c = p[o[0]]
        ch = top if (top != 'X' and c >= TH) else ('x' if top == 'X' and c >= TH else '#')
        alts = [(cls[j], round(max(float(p[j]),0.02),3)) for j in o if cls[j] != 'X'][:3]
        res.append(dict(ch=ch, alts=alts, x=float(it['x']), r=float(it['x']+it['w']), y=float(it['y']+it['h'])))
    return res
out = {}
for f, mp in sorted(by.items()):
    d = pickle.load(open(f,'rb')); Hc = d['Hc']; pitch = d.get('pitch', Hc)
    L2 = []
    for li, L in enumerate(d['lines']):
        cs = chars(f, mp, li, L['items'])
        groups = [[cs[0]]]
        for a, b in zip(cs, cs[1:]):
            if b['x'] - a['r'] > 1.8*pitch: groups.append([])
            groups[-1].append(b)
        L2.append(dict(y=L['y'], cs=cs, groups=groups, minus=[m['before'] for m in L.get('minus', [])]))
    # fit right edges of 7 columns from good lines
    pts = [[] for _ in range(7)]
    for L in L2:
        g = L['groups']
        if len(g) == 7 and len(g[0]) == 10 and len(g[4]) in (5,6) and len(g[5]) in (3,4):
            for c in range(7): pts[c].append((L['y'], g[c][-1]['r'], g[c][0]['x']))
    if min(len(p) for p in pts) < 3:
        out[os.path.basename(f)[:-4]] = dict(lines=[], note='few good lines %d' % min(len(p) for p in pts)); continue
    fits = []
    for c in range(7):
        a = np.array(pts[c]); 
        A = np.polyfit(a[:,0], a[:,1], 1) if len(set(a[:,0])) > 1 else [0, a[0,1]]
        fits.append(A)
    lines = []
    for L in L2:
        y = L['y']; R_ = [np.polyval(fits[c], y) for c in range(7)]
        cols = [[] for _ in range(7)]
        for k, ch in enumerate(L['cs']):
            cx = (ch['x']+ch['r'])/2
            if cx < R_[0] + 0.6*pitch: c = 0
            else:
                c = None
                for j in range(1, 7):
                    if R_[j-1] + 0.6*pitch < cx <= R_[j] + 0.6*pitch: c = j; break
                if c is None: continue
                if cx < R_[c] - 7.5*pitch: continue
            cols[c].append((k, ch))
        neg = [False]*7
        for b in L['minus']:
            for c in range(1,7):
                if cols[c] and cols[c][0][0] == b: neg[c] = True
        lines.append(dict(y=y, x0=L['cs'][0]['x'], x1=L['cs'][-1]['r'], cols=[(('-' if neg[c] else '') + ''.join(ch['ch'] for _,ch in cols[c]), [ch['alts'] for _,ch in cols[c]]) for c in range(7)]))
    out[os.path.basename(f)[:-4]] = dict(lines=lines)
json.dump(out, open('cols.json','w'))
bad = [k for k,v in out.items() if not v['lines']]
print('images without fit', len(bad), bad[:10])
k = sorted(out)[100]
for L in out[k]['lines'][:14]: print([c[0] for c in L['cols']])
