import pickle, json, sys
from datetime import datetime, timedelta
S=datetime(2026,1,1,10); H=timedelta(hours=1)
F=pickle.load(open('final.pkl','rb')); sel=F['sel']
M=json.load(open('manual.json'))
tT=float(sys.argv[1]); tP=float(sys.argv[2])
out=[]
for i in range(1,len(sel)-1):
    k=(S+i*H).isoformat()
    for c,t in ((4,tT),(3,tP)):
        a,b,d=float(sel[i-1][c]),float(sel[i][c]),float(sel[i+1][c])
        dev=abs(b-(a+d)/2)
        # deviation not explained by a trend change: require b outside [min,max] of neighbors by margin
        if dev>t and (b>max(a,d)+t/2 or b<min(a,d)-t/2):
            if M['cells'].get(k,{}).get(str(c)) is None and k not in M.get('reviewed_anom',[]):
                out.append(k)
out=sorted(set(out)); print(len(out)); json.dump(out,open('anom.json','w'))
