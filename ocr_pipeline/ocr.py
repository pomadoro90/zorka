import sys, os, cv2, numpy as np, subprocess
def prep(path, scale=1.0):
    img = cv2.imread(path)
    b,g,r = [img[:,:,i].astype(int) for i in range(3)]
    blue = (b - r > 60) & (b > 120)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # invert highlighted rows: use red channel there (text white, bg dark) -> invert
    rows = blue.mean(axis=1) > 0.25
    if rows.any():
        k = np.ones(15, bool)
        rows = np.convolve(rows, k, 'same') > 0
        gray[rows] = 255 - img[:,:,2][rows]
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    # background normalize
    bg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((25,25),np.uint8))
    norm = cv2.divide(gray, bg, scale=255)
    _, th = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th
def ocr(path, out, variant):
    th = prep(path, 1.0)
    tmp = out + '.png'
    cv2.imwrite(tmp, th)
    cfg = ['--psm', '6']
    if variant == 'w':
        cfg += ['-c', 'tessedit_char_whitelist=0123456789.:-Итого']
    txt = subprocess.run(['tesseract', tmp, '-', '-l', 'eng'] + cfg, capture_output=True, text=True).stdout
    os.remove(tmp)
    open(out, 'w').write(txt)
if __name__ == '__main__':
    variant = sys.argv[1]; outdir = sys.argv[2]
    for p in sys.argv[3:]:
        o = os.path.join(outdir, os.path.basename(p) + '.' + variant + '.txt')
        if not os.path.exists(o): ocr(p, o, variant)
