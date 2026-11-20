import json, pickle, cv2, numpy as np, sys, os
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1)
LOC = json.load(open('loc.json'))
F = pickle.load(open('final.pkl','rb'))
_cache = {}
def deskewed(img):
    if img in _cache: return _cache[img]
    im = cv2.imread('/home/user/zorka/%s.jpg' % img, cv2.IMREAD_GRAYSCALE)
    d = pickle.load(open('gl/%s.pkl' % img, 'rb'))
    sk = d.get('skew', 0.0); xc = im.shape[1]/2
    M = np.float32([[1,0,0],[-sk,1,sk*xc]])
    out = cv2.warpAffine(im, M, (im.shape[1], im.shape[0]), borderValue=255)
    _cache.clear(); _cache[img] = (out, d['Hc'], sk, xc)
    return _cache[img]
def locate(k):
    if k in LOC: 
        img, y, x0, x1 = LOC[k][0]; return img, y, (x0+x1)/2
    t = datetime.fromisoformat(k)
    for off in (1, -1, 2, -2, 3, -3):
        k2 = (t - off*H).isoformat()
        if k2 in LOC:
            img, y, x0, x1 = LOC[k2][0]
            d = pickle.load(open('gl/%s.pkl' % img, 'rb')); ys = sorted(L['y'] for L in d['lines'])
            gaps = [b-a for a,b in zip(ys, ys[1:]) if 0.8*d['Hc'] < b-a < 2.5*d['Hc']]
            sp = float(np.median(gaps)) if gaps else 1.8*d['Hc']
            return img, y + off*sp, (x0+x1)/2
    return None
def crop(k, W=1500, up=1.5, dn=0.6):
    l = locate(k)
    if not l: return None
    img, y, xm = l
    im, Hc, sk, xc = deskewed(img)
    yd = y - sk*(xm - xc)
    a, b = int(max(0, yd - up*Hc)), int(min(im.shape[0], yd + dn*Hc))
    c = im[a:b]
    s = W / c.shape[1]
    return cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), img
def crop_at(img, y, xm, up, dn, W=1500):
    im, Hc, sk, xc = deskewed(img)
    yd = y - sk*(xm - xc)
    a, b = int(max(0, yd - up*Hc)), int(min(im.shape[0], yd + dn*Hc))
    c = im[a:b]; s = W / c.shape[1]
    return cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
def sheet(keys, out, up=1.5, dn=0.6):
    tiles = []
    for n, k in enumerate(keys):
        r = crop(k, up=up, dn=dn)
        i = int((datetime.fromisoformat(k)-START)/H)
        lab = np.full((24, 1500), 255, np.uint8)
        txt = '#%d %s | %s' % (n, k[5:13], '  '.join(str(v) for v in F['sel'][i]))
        cv2.putText(lab, txt, (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
        tiles.append(lab)
        if r is not None: tiles.append(r[0])
        if k in LOC and len(LOC[k]) > 1:
            img2 = LOC[k][1]
            r2 = crop_at(img2[0], img2[1], (img2[2]+img2[3])/2, up, dn)
            if r2 is not None: tiles.append(np.full((3,1500),0,np.uint8)); tiles.append(r2)
        tiles.append(np.full((4,1500),128,np.uint8))
    cv2.imwrite(out, np.vstack(tiles))
if __name__ == '__main__':
    keys = sys.argv[2:]; sheet(keys, sys.argv[1])
