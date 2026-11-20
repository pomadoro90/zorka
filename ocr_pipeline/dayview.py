import json, sys, cv2, numpy as np, pickle
from collections import defaultdict
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1)
F = pickle.load(open('final.pkl','rb')); sel = F['sel']
LOC = json.load(open('loc.json'))
ds = sys.argv[1]; cols = [int(c) for c in sys.argv[2].split(',')]
d0 = datetime.fromisoformat(ds + 'T10:00:00'); d = int((d0-START)/H)//24
g = defaultdict(list)
for i in range(d*24, d*24+24):
    k = (START+i*H).isoformat()
    print(k[5:13], ' '.join(str(sel[i][c]) for c in cols))
    if k in LOC:
        img, y, *_ = LOC[k][0]; g[img].append(y)
print('itogo', F['itog'][d])
tiles = []
for img, ys in sorted(g.items()):
    im = cv2.imread('/home/user/zorka/%s.jpg' % img, cv2.IMREAD_GRAYSCALE)
    a, b = int(max(0, min(ys)-70)), int(min(im.shape[0], max(ys)+220))
    c = im[a:b]; s = 1100/c.shape[1]; tiles.append(cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
    tiles.append(np.zeros((6,1100),np.uint8))
cv2.imwrite('t/day.png', np.vstack(tiles))
