import json, sys, cv2, numpy as np, pickle
sys.path.insert(0, 'scripts')
from datetime import datetime, timedelta
from review import locate
START = datetime(2026,1,1,10); H = timedelta(hours=1)
F = pickle.load(open('final.pkl','rb')); sel = F['sel']
days = sys.argv[2:]
tiles = []
for ds in days:
    d0 = datetime.fromisoformat(ds + 'T10:00:00'); d = int((d0-START)/H)//24
    ids = range(d*24, d*24+24)
    try:
        V = sum(int(sel[i][0]) for i in ids); E = sum(int(sel[i][1]) for i in ids)
        Fm = sum(int(sel[i][2]) for i in ids)/24; P = sum(float(sel[i][3]) for i in ids)/24; T = sum(float(sel[i][4]) for i in ids)/24
        calc = '%d %d %.2f %.3f %.3f' % (V, E, Fm, P, T)
    except Exception as e: calc = 'ERR'
    lab = np.full((24, 1500), 255, np.uint8)
    cv2.putText(lab, '%s calc %s | itogo %s' % (ds, calc, F['itog'][d]), (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, 0, 1)
    tiles.append(lab)
    k9 = (START + (d*24+23)*H).isoformat()
    l = locate(k9)
    if l:
        img, y, xm = l
        im = cv2.imread('/home/user/zorka/%s.jpg' % img, cv2.IMREAD_GRAYSCALE)
        a, b = int(max(0, y - 60)), int(min(im.shape[0], y + 200))
        c = im[a:b]; c = cv2.resize(c, None, fx=1500/c.shape[1], fy=1500/c.shape[1], interpolation=cv2.INTER_AREA)
        tiles.append(c)
    tiles.append(np.full((4,1500),0,np.uint8))
cv2.imwrite(sys.argv[1], np.vstack(tiles))
