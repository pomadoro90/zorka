import sys,cv2,subprocess,numpy as np,os
p=sys.argv[1]
img=cv2.imread(p); gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
def run(im,name):
    cv2.imwrite('t/'+name+'.png',im)
    out=subprocess.run(['tesseract','t/'+name+'.png','-','--psm','6'],capture_output=True,text=True,env=dict(os.environ,OMP_THREAD_LIMIT='1')).stdout
    lines=[l for l in out.splitlines() if l.strip()]
    print('==',name); print('\n'.join(lines[:12]))
for k in [5,9]:
    g=cv2.GaussianBlur(gray,(k,k),0)
    bg=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((41,41),np.uint8))
    n=cv2.divide(g,bg,scale=255)
    _,th=cv2.threshold(n,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    run(th,'blur%d'%k)
    run(n,'norm%d'%k)
