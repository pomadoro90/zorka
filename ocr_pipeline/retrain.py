import pickle, numpy as np
from sklearn.neighbors import KNeighborsClassifier
hl = "9 9 8 8 8 4 0 6 1 0 0 5 0 5 6 1 0 9 6 6 6 0 0 1 0 8 7 X 1 9 0 6 6 X X 6 X X 6 5 X 6 6 X 2 X X X X 3 X X X X X X X X X X".split()
pca, knn = pickle.load(open('model.pkl','rb'))
H = pickle.load(open('hard.pkl','rb')); X2 = np.load('X2.npy')
Z0 = knn._fit_X; y0 = knn._y; cls0 = knn.classes_
y0 = cls0[y0]
Zh = pca.transform(X2[H['hard']])
addZ, addy = [], []
for j,k in enumerate(H['order']):
    if hl[j] == 'X': continue
    idx = np.where(H['lab']==k)[0]
    c = Zh[idx].mean(0); d = np.linalg.norm(Zh[idx]-c,axis=1)
    sel = idx[d <= np.percentile(d,60)]
    addZ.append(Zh[sel]); addy += [hl[j]]*len(sel)
Z = np.vstack([Z0]+addZ); y = np.concatenate([y0, np.array(addy)])
knn2 = KNeighborsClassifier(7, n_jobs=4).fit(Z, y)
pickle.dump((pca, knn2), open('model.pkl','wb'))
print(len(y0), len(addy))
