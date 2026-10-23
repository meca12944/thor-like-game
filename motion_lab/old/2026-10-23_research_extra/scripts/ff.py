import sys,numpy as np
from measure import load,stats
for arg in sys.argv[1:]:
    c,k=arg.split(':');fr=load(c,k);s=stats(fr);o=[]
    for a,(top,bot,bx,h) in zip(fr,s):
        m=a[...,3]>40;cx=int(bx);y0=int(bot-h*.12)
        L=np.nonzero(m[y0:,:cx].any(1))[0];Rr=np.nonzero(m[y0:,cx:].any(1))[0]
        o.append((y0+L.max() if len(L) else -1)-(y0+Rr.max() if len(Rr) else -1))
    print(k,'Lbot-Rbot',o,'top',list(s[:,0].astype(int)))
