import cv2, numpy as np, sys
def binarize(path, k=5):
    img = cv2.imread(path)
    b,g,r = [img[:,:,i].astype(int) for i in range(3)]
    blue = (b-r>60)&(b>120)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # in highlighted areas, use inverted red channel (local, per pixel region)
    bm = cv2.dilate(blue.astype(np.uint8), np.ones((9,9),np.uint8)) > 0
    # fill region rows: close horizontally to cover white text
    bm = cv2.morphologyEx(bm.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25,61),np.uint8)) > 0
    gray = np.where(bm, 255 - img[:,:,2], gray).astype(np.uint8)
    g = cv2.GaussianBlur(gray,(k,k),0)
    bg = cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((41,41),np.uint8))
    n = cv2.divide(g,bg,scale=255)
    o,_ = cv2.threshold(n,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    t = min(o+30, 205)
    th = np.where(n < t, 255, 0).astype(np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((1,4),np.uint8))
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((3,1),np.uint8))
    return th, n
if __name__ == '__main__':
    th, n = binarize(sys.argv[1])
    cv2.imwrite(sys.argv[2], 255-th)
    nl, lab, st, cen = cv2.connectedComponentsWithStats(th)
    hs = st[1:,3]; print(nl, np.percentile(hs,[50,75,90,95]))
