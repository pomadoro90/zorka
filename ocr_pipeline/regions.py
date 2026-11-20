import json, cv2, sys
from collections import defaultdict
from datetime import datetime, timedelta
sys.path.insert(0,'scripts')
from review import locate
H = timedelta(hours=1)
L = json.load(open('review_list.json'))
g = defaultdict(list)
for k in L:
    l = locate(k)
    if l: g[l[0]].append((k, l[1]))
    else: print('noloc', k)
out = []
for n, (img, ks) in enumerate(sorted(g.items())):
    ys = [y for _, y in ks]
    im = cv2.imread('/home/user/zorka/%s.jpg' % img)
    a = int(max(0, min(ys) - 200)); b = int(min(im.shape[0], max(ys) + 200))
    c = cv2.resize(im[a:b], None, fx=0.5, fy=0.5)
    cv2.imwrite('rg/%02d.png' % n, c)
    out.append((n, img, [k[5:13] for k, _ in ks]))
for o in out: print(o)
