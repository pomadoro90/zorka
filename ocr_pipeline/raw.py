import json, cv2, sys, numpy as np
sys.path.insert(0, 'scripts'); sys.argv_bak = sys.argv; 
from review import locate
def rawcrop(k, rows=3, W=1500):
    l = locate(k)
    if not l: return None
    img, y, xm = l
    im = cv2.imread('/home/user/zorka/%s.jpg' % img, cv2.IMREAD_GRAYSCALE)
    a, b = int(max(0, y - rows*60)), int(min(im.shape[0], y + rows*60))
    c = im[a:b]; s = W / c.shape[1]
    c = cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    lab = np.full((24, W), 255, np.uint8)
    cv2.putText(lab, k + ' ' + img, (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
    return np.vstack([lab, c, np.full((4, W), 0, np.uint8)])
if __name__ == '__main__':
    out = sys.argv_bak[1]; rows = float(sys.argv_bak[2])
    tiles = [t for t in (rawcrop(k, rows) for k in sys.argv_bak[3:]) if t is not None]
    cv2.imwrite(out, np.vstack(tiles))
