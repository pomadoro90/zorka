import sys, os, cv2, numpy as np, subprocess, glob
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from ocr import prep
OUT = sys.argv[1]; SRC = sys.argv[2]
VARS = [('b10',1.0,True),('b15',1.5,True),('b20',2.0,True),('g15',1.5,False),('k5b',5,'b'),('k5n',5,'n'),('k9b',9,'b'),('k9n',9,'n')]
def prep_gray(path, sc):
    img = cv2.imread(path)
    b,g,r = [img[:,:,i].astype(int) for i in range(3)]
    blue = (b-r>60)&(b>120)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows = blue.mean(axis=1) > 0.25
    if rows.any():
        rows = np.convolve(rows, np.ones(15,bool), 'same') > 0
        gray[rows] = 255 - img[:,:,2][rows]
    gray = cv2.resize(gray, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    bg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((31,31),np.uint8))
    return cv2.divide(gray, bg, scale=255)
def prep_blur(path, k, mode):
    img = cv2.imread(path)
    b,g,r = [img[:,:,i].astype(int) for i in range(3)]
    blue = (b-r>60)&(b>120)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows = blue.mean(axis=1) > 0.25
    if rows.any():
        rows = np.convolve(rows, np.ones(15,bool), 'same') > 0
        gray[rows] = 255 - img[:,:,2][rows]
    g = cv2.GaussianBlur(gray,(k,k),0)
    bg = cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((41,41),np.uint8))
    n = cv2.divide(g,bg,scale=255)
    if mode == 'n': return n
    _,th = cv2.threshold(n,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return th
def job(a):
    p, (name, sc, binar) = a
    o = os.path.join(OUT, os.path.basename(p)[:-4] + '.' + name + '.txt')
    if os.path.exists(o): return
    if binar in ('b','n'): im = prep_blur(p, sc, binar)
    else: im = prep(p, sc) if binar else prep_gray(p, sc)
    tmp = o + '.png'; cv2.imwrite(tmp, im)
    try:
        txt = subprocess.run(['tesseract', tmp, '-', '--psm', '6'], capture_output=True, text=True, timeout=60, env=dict(os.environ, OMP_THREAD_LIMIT='1')).stdout
    except subprocess.TimeoutExpired:
        txt = 'TIMEOUT'
    os.remove(tmp); open(o, 'w').write(txt)
if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SRC, 'IMG_*.jpg')))
    jobs = [(f, v) for f in files for v in VARS]
    with Pool(4) as pool:
        for i, _ in enumerate(pool.imap_unordered(job, jobs)):
            if i % 100 == 0: print(i, len(jobs), flush=True)
