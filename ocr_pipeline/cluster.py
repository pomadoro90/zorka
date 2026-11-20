import pickle, glob, numpy as np, cv2
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans
X=[]; meta=[]
for f in sorted(glob.glob('gl/*.pkl')):
    d=pickle.load(open(f,'rb'))
    for li,L in enumerate(d['lines']):
        for ii,it in enumerate(L['items']):
            X.append(np.concatenate([it['g'].ravel(), [it['ar']*2]])); meta.append((f,li,ii))
X=np.array(X,dtype=np.float32); print(X.shape)
pca=PCA(40, random_state=0).fit(X); Z=pca.transform(X)
km=MiniBatchKMeans(160, random_state=0, n_init=3, batch_size=4096).fit(Z)
lab=km.labels_
np.save('X.npy',X); pickle.dump(meta,open('meta.pkl','wb')); np.save('km_lab.npy',lab)
# montage: each cluster row shows 14 samples nearest center + 4 farthest
rows=[]
order=np.argsort(-np.bincount(lab,minlength=160))
pickle.dump(order,open('km_order.pkl','wb'))
S=2
for k in order:
    idx=np.where(lab==k)[0]
    d=np.linalg.norm(Z[idx]-km.cluster_centers_[k],axis=1)
    o=idx[np.argsort(d)]
    pick=list(o[:10])+list(o[-6:])
    tiles=[(1-X[i][:384].reshape(24,16))*255 for i in pick]
    while len(tiles)<16: tiles.append(np.full((24,16),128))
    row=np.hstack([np.pad(t,1,constant_values=128) for t in tiles]).astype(np.uint8)
    rows.append(row)
for p in range(0,160,40):
    blk=rows[p:p+40]
    canvas=[]
    for j,r in enumerate(blk):
        lbl=np.full((26,40),255,np.uint8); cv2.putText(lbl,str(p+j),(1,19),cv2.FONT_HERSHEY_SIMPLEX,0.55,0,1)
        canvas.append(np.hstack([lbl,r]))
    img=np.vstack(canvas); img=cv2.resize(img,None,fx=S,fy=S,interpolation=cv2.INTER_NEAREST)
    cv2.imwrite(f'mont_{p}.png',img)
print(np.bincount(lab)[order][:160])
