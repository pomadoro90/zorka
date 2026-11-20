import json, sys, cv2, numpy as np, pickle
sys.path.insert(0, 'scripts')
from datetime import datetime, timedelta
from review import locate
START = datetime(2026,1,1,10); H = timedelta(hours=1)
F = pickle.load(open('final.pkl','rb'))
R = json.load(open('r2.json'))
B = json.load(open('rv/batches.json'))[sys.argv[1]]
tiles = []
for n, k in enumerate(B):
    i = int((datetime.fromisoformat(k)-START)/H)
    lab = np.full((24, 1500), 255, np.uint8)
    ocr = [r[1][3:5] for r in R['readings'].get(k, [])]
    cv2.putText(lab, '#%d %s | %s | ocr %s' % (n, k[5:13], '  '.join(str(v) for v in F['sel'][i]), ocr), (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, 0, 1)
    tiles.append(lab)
    l = locate(k)
    if l:
        img, y, xm = l
        im = cv2.imread('/home/user/zorka/%s.jpg' % img, cv2.IMREAD_GRAYSCALE)
        a, b = int(max(0, y - 80)), int(min(im.shape[0], y + 45))
        c = im[a:b]; c = cv2.resize(c, None, fx=1500/c.shape[1], fy=1500/c.shape[1], interpolation=cv2.INTER_AREA)
        tiles.append(c)
    tiles.append(np.full((4,1500),0,np.uint8))
cv2.imwrite('rv/s%s.png' % sys.argv[1], np.vstack(tiles))
