import json,sys,numpy as np
from fix import *
from render import video
C=json.load(open(R+'linette/clips.json'))
def walk_side(clip,A=2.6):
    fr=load('linette',clip);t0=C[clip]['ticks'];d=track(fr)
    t1=retime(d,sum(t0));s=spread(fr);dy=[round(A*(v-.5)) for v in s]
    nf=[warp(a,dy=y) for a,y in zip(fr,dy)]
    s0,s1=stats(fr),stats(nf)
    print(clip,'ticks',t0,'->',t1,'slip',round(slipscore(d,t0),1),'->',round(slipscore(d,t1),1),'dy',dy,'head',np.ptp(s0[:,0]),'->',np.ptp(s1[:,0]))
    return fr,t0,nf,t1,np.nanmean([x for x in d if x])*len(d)/sum(t0)
fr,t0,nf,t1,sp=walk_side(sys.argv[1])
video(sys.argv[1]+'.mp4',[dict(frames=fr,ticks=t0,speed=sp,label='전'),dict(frames=nf,ticks=t1,speed=sp,label='후')])
