import pickle, json
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1)
F = pickle.load(open('final.pkl','rb')); M = json.load(open('manual.json'))
done = set(M.get('cells', {}).keys()) | set(M.get('reviewed', []))
lst = []
for i, row in enumerate(F['sel']):
    k = (START+i*H).isoformat()
    if k in done: continue
    fl = [f for c in F['flag'][i] for f in c]
    if any(v is None for v in row) or any(f in ('ratio?','F/V?','Vru?','jump?') for f in fl): lst.append(k)
sel = F['sel']
for i in range(len(sel)):
    for j in (i+1, i+2):
        if j < len(sel) and sel[i][3] and sel[i][3] == sel[j][3] and sel[i][4] == sel[j][4]:
            for x in (i, j):
                k = (START+x*H).isoformat()
                if k not in done and k not in lst: lst.append(k)
lst.sort()
json.dump(lst, open('review_list.json','w'))
print(len(lst))
