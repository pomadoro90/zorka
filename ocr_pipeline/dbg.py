import cv2, pickle, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from seg import binarize
p, pk, out = sys.argv[1:4]
th,_ = binarize(p); im = cv2.cvtColor(255-th, cv2.COLOR_GRAY2BGR)
d = pickle.load(open(pk,'rb'))
for L in d['lines']:
    for it in L['items']: cv2.rectangle(im, (int(it['x']),int(it['y'])), (int(it['x']+it['w']),int(it['y']+it['h'])), (0,0,255), 2)
    for s in L.get('small',[]): cv2.rectangle(im, (int(s['x']),int(s['y'])), (int(s['x']+s['w']),int(s['y']+s['h'])), (0,180,0), 2)
y0,y1 = map(int, sys.argv[4:6]) if len(sys.argv)>5 else (0, im.shape[0])
im = im[y0:y1]
cv2.imwrite(out, cv2.resize(im, None, fx=0.6, fy=0.6))
