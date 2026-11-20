import json, sys
from datetime import datetime, timedelta
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
S = datetime(2026,1,1,10)
cnt = [[0,0,0] for _ in range(6)]
for i in range(7728):
    k = (S+timedelta(hours=i)).isoformat()
    for c in range(6):
        ka = a['cells'].get(k); kb = b['cells'].get(k)
        if ka and ka[c] and not any(ch in max(ka[c],key=ka[c].get) for ch in '#x'): cnt[c][0]+=1
        elif kb and kb[c]: cnt[c][1]+=1
        else: cnt[c][2]+=1
print(cnt)
