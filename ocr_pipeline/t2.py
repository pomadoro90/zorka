import sys,cv2,subprocess,time
sys.path.insert(0,'scripts')
from ocr import prep
p=sys.argv[1]
for sc in [1.5,2.0]:
    th=prep(p,sc); cv2.imwrite('t/x.png',th)
    t=time.time()
    out=subprocess.run(['tesseract','t/x.png','-','--psm','6'],capture_output=True,text=True).stdout
    print(sc, time.time()-t); print('\n'.join(out.splitlines()[:30]))
