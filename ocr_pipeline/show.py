import pickle, sys, json
from datetime import datetime, timedelta
START = datetime(2026,1,1,10); H = timedelta(hours=1)
F = pickle.load(open('final.pkl','rb')); table, itg = pickle.load(open('cands.pkl','rb'))
R = json.load(open('r2.json'))
day = datetime.fromisoformat(sys.argv[1]); d = int((day.replace(hour=10)-START)/H)//24
for i in range(d*24, d*24+24):
    k = (START+i*H).isoformat(); s = F['sel'][i]
    rat = int(s[1])/int(s[0]) if s[0] and s[1] and int(s[0]) else 0
    print(k[5:16], s, round(rat,3), [f for f in F['flag'][i] if f], [img[-6:] for img,_,_ in R['readings'].get(k,[])])
    if len(sys.argv) > 2: print('     ', [dict(sorted(c.items(), key=lambda x:-x[1])[:3]) for c in table[k]])
print('itogo', F['itog'][d], [dict(c) for c in itg[(START+(d*24+23)*H).isoformat()]])
