import pickle, numpy as np, glob, os
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
L = {}
lab0 = "0 0 0 0 1 1 9 1 0 4 4 0 4 4 0 0 0 6 7 7 4 6 3 1 3 9 1 6 0 6 7 6 6 0 1 0 5 0 5 3".split()
lab1 = "7 5 0 1 6 0 4 2 3 9 3 0 0 0 3 2 3 1 9 5 6 0 3 5 2 2 0 0 2 1 2 3 2 2 1 5 7 3 9 0".split()
lab2 = "1 X 0 3 2 2 2 2 5 2 2 2 0 1 6 3 7 8 1 2 X 6 2 2 8 7 8 0 8 8 8 8 8 8 8 8 1 X 8 X".split()
lab3 = "X X X X 0 X X X X X X X X X X X X X X X X X X 9 X X X X X 2 X X X X X X X X X X".split()
labs = lab0+lab1+lab2+lab3
order = pickle.load(open('km_order.pkl','rb'))
cl2lab = {int(order[i]): labs[i] for i in range(160)}
X = np.load('X.npy'); km = np.load('km_lab.npy'); meta = pickle.load(open('meta.pkl','rb'))
pca = PCA(40, random_state=0).fit(X); Z = pca.transform(X)
y = np.array([cl2lab[int(k)] for k in km])
# training: per cluster take the 50% closest to cluster centroid
tr = []
for k in range(160):
    idx = np.where(km == k)[0]
    c = Z[idx].mean(0); d = np.linalg.norm(Z[idx]-c, axis=1)
    tr += list(idx[d <= np.percentile(d, 50)])
tr = np.array(tr)
knn = KNeighborsClassifier(7, n_jobs=4).fit(Z[tr], y[tr])
pickle.dump((pca,knn), open('model.pkl','wb'))
P = knn.predict_proba(Z); cls = knn.classes_
pred = cls[P.argmax(1)]; conf = P.max(1)
print('low conf', (conf < 0.72).sum(), 'of', len(conf))
pickle.dump(dict(pred=pred, conf=conf, meta=meta), open('pred.pkl','wb'))
