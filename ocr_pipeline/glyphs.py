import cv2, numpy as np, sys, os, glob, pickle
sys.path.insert(0, os.path.dirname(__file__))
from seg import binarize
GW, GH = 16, 24
def norm_glyph(mask):
    g = cv2.resize(mask.astype(np.float32), (GW, GH), interpolation=cv2.INTER_AREA)
    return g
def extract(path):
    th, _ = binarize(path)
    nl, lab, st, cen = cv2.connectedComponentsWithStats(th, connectivity=8)
    comps = [(i, *st[i]) for i in range(1, nl)]
    hs = np.array([c[4] for c in comps])
    # character height: mode of heights in range 15..80
    cand = hs[(hs > 15) & (hs < 90)]
    hist = np.bincount(cand)
    Hc = int(np.argmax(np.convolve(hist, np.ones(3), 'same')))
    big, small, minus = [], [], []
    for (i, x, y, w, h, a) in comps:
        if 0.7*Hc <= h <= 1.6*Hc and 0.15*Hc <= w <= 4.5*Hc:
            big.append([x, y, w, h, i])
        elif h <= 0.3*Hc and 0.3*Hc <= w <= 0.9*Hc and w >= 2*h:
            minus.append([x, y, w, h, i])
        elif 0.08*Hc <= h <= 0.35*Hc and 0.08*Hc <= w <= 0.35*Hc and a >= 0.01*Hc*Hc:
            small.append([x, y, w, h, i])
    big = sorted(big)
    narrow = [b for b in big if b[2] <= 1.1*Hc]
    pitches = []
    nb = sorted(narrow)
    for a, b in zip(nb, nb[1:]):
        d = b[0]-a[0]
        if 0.7*Hc < d < 1.4*Hc and abs((b[1]+b[3])-(a[1]+a[3])) < 0.2*Hc: pitches.append(d)
    pitch = float(np.median(pitches)) if pitches else 1.0*Hc
    nbig = []
    for (x, y, w, h, i) in big:
        if w <= 1.15*pitch: nbig.append([x, y, w, h, i, None]); continue
        k = int(round((w + 0.2*pitch) / pitch))
        if k < 2: nbig.append([x, y, w, h, i, None]); continue
        m = (lab[y:y+h, x:x+w] == i); col = m.sum(0)
        cuts = [0]
        for j in range(1, k):
            e = int(j*w/k); r = int(0.2*pitch)
            lo, hi = max(1, e-r), min(w-1, e+r)
            cuts.append(lo + int(np.argmin(col[lo:hi])) if hi > lo else e)
        cuts.append(w)
        for a, b in zip(cuts, cuts[1:]):
            sub = m[:, a:b]
            rr = np.where(sub.any(1))[0]; cc = np.where(sub.any(0))[0]
            if len(rr) == 0 or len(cc) == 0: continue
            nbig.append([x+a+cc[0], y+rr[0], cc[-1]-cc[0]+1, rr[-1]-rr[0]+1, i, sub[rr[0]:rr[-1]+1, cc[0]:cc[-1]+1]])
    big = sorted(nbig, key=lambda b: b[0])
    # link glyphs into lines
    n = len(big); parent = list(range(n))
    def f(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    cx = np.array([b[0]+b[2]/2 for b in big]); cyb = np.array([b[1]+b[3] for b in big])
    def link(skew, maxdx):
        for a in range(n):
            best = None
            for b in range(a+1, n):
                dx = big[b][0] - (big[a][0]+big[a][2])
                if dx > maxdx: break
                if dx < -0.3*Hc: continue
                dy = abs((cyb[b]-skew*cx[b])-(cyb[a]-skew*cx[a]))
                if dy < 0.35*Hc and (best is None or dx < best[0]): best = (dx, b)
            if best: parent[f(a)] = f(best[1])
    link(0.0, 3*Hc)
    # estimate skew from first-pass lines
    gr = {}
    for a in range(n): gr.setdefault(f(a), []).append(a)
    slopes, wts = [], []
    for g in gr.values():
        if len(g) >= 6:
            xs = cx[g]; ys = cyb[g]
            if xs.max()-xs.min() > 5*Hc:
                slopes.append(np.polyfit(xs, ys, 1)[0]); wts.append(len(g))
    skew = float(np.median(slopes)) if slopes else 0.0
    link(skew, 40*Hc)
    groups = {}
    for a in range(n): groups.setdefault(f(a), []).append(a)
    lines = []
    for g in groups.values():
        g = sorted(g, key=lambda a: big[a][0])
        if len(g) < 3: continue
        items = []
        for a in g:
            x, y, w, h, i, sub = big[a]
            crop = sub if sub is not None else (lab[y:y+h, x:x+w] == i)
            items.append(dict(x=x, y=y, w=w, h=h, g=norm_glyph(crop), ar=w/h))
        # small comps lying between glyphs (dots/colons)
        ys = np.array([it['y']+it['h'] for it in items]); 
        lines.append(dict(items=items, y=float(np.median(ys)), x0=items[0]['x']))
    # attach small comps (dots/minus) to lines
    for (x, y, w, h, i) in small:
        pass
    for (x, y, w, h, i) in small:
        for L in lines:
            xs = [it['x'] for it in L['items']]
            if not (xs[0]-Hc < x < L['items'][-1]['x']+L['items'][-1]['w']+Hc): continue
            # baseline at that x: nearest item
            k = int(np.argmin([abs(it['x']-x) for it in L['items']]))
            it = L['items'][k]
            base = it['y']+it['h']; top = it['y']
            if top - 0.2*Hc <= y and y+h <= base + 0.2*Hc:
                L.setdefault('small', []).append(dict(x=x, y=y, w=w, h=h, rel=(y+h/2-top)/it['h']))
                break
    for (x, y, w, h, i) in minus:
        for L in lines:
            its = L['items']
            k = int(np.argmin([abs(it['x']-(x+w)) for it in its]))
            it = its[k]
            if it['x'] >= x+w-0.1*Hc and it['x'] - (x+w) < 0.8*Hc and it['y'] + 0.25*it['h'] < y+h/2 < it['y'] + 0.75*it['h']:
                L.setdefault('minus', []).append(dict(x=x, y=y, w=w, h=h, before=k))
                break
    lines.sort(key=lambda L: L['y'])
    return dict(Hc=Hc, pitch=pitch, skew=skew, lines=lines)
if __name__ == '__main__':
    out = sys.argv[1]
    for p in sys.argv[2:]:
        o = os.path.join(out, os.path.basename(p)[:-4] + '.pkl')
        if os.path.exists(o): continue
        pickle.dump(extract(p), open(o, 'wb'))
