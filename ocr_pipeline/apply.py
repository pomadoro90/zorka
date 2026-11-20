import pickle, glob, numpy as np, sys
from collections import defaultdict
model = sys.argv[1] if len(sys.argv)>1 else 'model.pkl'
pca, knn = pickle.load(open(model,'rb'))
X=[]; meta=[]
for f in sorted(glob.glob('gl/*.pkl')):
    d=pickle.load(open(f,'rb'))
    for li,L in enumerate(d['lines']):
        for ii,it in enumerate(L['items']):
            X.append(np.concatenate([it['g'].ravel(), [it['ar']*2]])); meta.append((f,li,ii))
X=np.array(X,dtype=np.float32); Z=pca.transform(X)
P=knn.predict_proba(Z); cls=knn.classes_
# within-image smoothing
byf = defaultdict(list)
for i,(f,li,ii) in enumerate(meta): byf[f].append(i)
P2 = P.copy()
for f, idx in byf.items():
    idx = np.array(idx); A = X[idx]
    D = ((A[:,None,:]-A[None,:,:])**2).sum(-1)
    np.fill_diagonal(D, np.inf)
    nn = np.argsort(D, axis=1)[:, :6]
    for r, i in enumerate(idx):
        P2[i] = P[i] + 0.5*P[idx[nn[r]]].mean(0)
    P2[idx] /= 1.5
pred=cls[P2.argmax(1)]; conf=P2.max(1)
np.save('X2.npy', X)
print(len(X), 'low conf', (conf<0.72).sum())
pickle.dump(dict(pred=pred, conf=conf, meta=meta, P=P2, cls=cls), open('pred.pkl','wb'))
