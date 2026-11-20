import pickle, numpy as np, re, cv2
from sklearn.cluster import MiniBatchKMeans
R = pickle.load(open('pred.pkl','rb')); X = np.load('X2.npy')
pca, knn = pickle.load(open('model.pkl','rb'))
pred, conf, meta = R['pred'], R['conf'], R['meta']
# group indices by line
from collections import defaultdict
lines = defaultdict(list)
for i,(f,li,ii) in enumerate(meta): lines[(f,li)].append(i)
hard = []
for key, idx in lines.items():
    s = ''.join(pred[i] if conf[i]>=0.72 else '#' for i in idx)
    good = sum(c.isdigit() for c in s)
    if len(idx) >= 20 and good >= 0.6*len(idx):   # looks like a data row
        hard += [i for i in idx if pred[i]=='X' or conf[i]<0.72]
hard = np.array(hard); print(len(hard))
Z = pca.transform(X[hard])
K = 60
km = MiniBatchKMeans(K, random_state=0, n_init=3).fit(Z)
lab = km.labels_; order = np.argsort(-np.bincount(lab, minlength=K))
pickle.dump(dict(hard=hard, lab=lab, order=order), open('hard.pkl','wb'))
rows=[]
for k in order:
    idx = np.where(lab==k)[0]
    d = np.linalg.norm(Z[idx]-km.cluster_centers_[k],axis=1); o = idx[np.argsort(d)]
    pick = list(o[:10]) + list(o[-6:])
    tiles = [(1-X[hard[i]][:384].reshape(24,16))*255 for i in pick]
    while len(tiles)<16: tiles.append(np.full((24,16),128))
    rows.append(np.hstack([np.pad(t,1,constant_values=128) for t in tiles]).astype(np.uint8))
canvas=[]
for j,r in enumerate(rows):
    lbl=np.full((26,40),255,np.uint8); cv2.putText(lbl,str(j),(1,19),cv2.FONT_HERSHEY_SIMPLEX,0.55,0,1)
    canvas.append(np.hstack([lbl,r]))
img=np.vstack(canvas); img=cv2.resize(img,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST)
cv2.imwrite('hard_a.png', img[:img.shape[0]//2]); cv2.imwrite('hard_b.png', img[img.shape[0]//2:])
print(np.bincount(lab)[order])
