import sys,numpy as np
from measure import load,stats
for ch,clip in [a.split(':') for a in sys.argv[1:]]:
    fr=load(ch,clip);s=stats(fr)
    out=[]
    for a,(top,bot,bx,h) in zip(fr,s):
        m=a[...,3]>40;rows=m[int(bot-h*.18):int(bot)+1];xs=np.nonzero(rows.any(0))[0]
        out.append(f"{int(np.ptp(xs)):3d}/{int(top)}")
    print(f"{ch[:3]} {clip:12s} spread/top:",' '.join(out))
