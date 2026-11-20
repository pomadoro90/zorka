import pickle, numpy as np, os, sys
TH = float(sys.argv[1]) if len(sys.argv)>1 else 0.72
from collections import defaultdict
R = pickle.load(open('pred.pkl','rb'))
by = defaultdict(dict)
for (f,li,ii), p, c in zip(R['meta'], R['pred'], R['conf']):
    by[f][(li,ii)] = p if (p != 'X' and c >= TH) else ('#' if p != 'X' or c < TH else 'X')
os.makedirs('kt', exist_ok=True)
for f, mp in by.items():
    d = pickle.load(open(f,'rb')); Hc = d['Hc']; out = []
    for li, L in enumerate(d['lines']):
        its = L['items']; sm = L.get('small', [])
        s = ''
        for ii, it in enumerate(its):
            ch = mp[(li,ii)]
            if ch == 'X': ch = 'x'
            s += ch
            if ii+1 < len(its):
                r = it['x']+it['w']; nx = its[ii+1]['x']; gap = nx - r
                dots = [q for q in sm if r - 0.15*Hc <= q['x'] + q['w']/2 <= nx + 0.15*Hc]
                if dots: s += '.' if gap < 1.6*Hc else ' . '
                elif gap > 0.45*Hc: s += ' '
        out.append(s)
    open(os.path.join('kt', os.path.basename(f)[:-4] + '.knn.txt'), 'w').write('\n'.join(out))
