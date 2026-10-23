import json,numpy as np
from measure import load,R
from slip import stance
from render import video
def retime(d,total):
    d=np.array(d,float);w=d/d.sum()*total;t=np.floor(w).astype(int)
    for j in np.argsort(-(w-t))[:total-t.sum()]:t[j]+=1
    return list(np.maximum(t,2))
def slipscore(d,ticks,sp):return sum(abs(x-sp*t) for x,t in zip(d,ticks) if x is not None)
C=json.load(open(R+'linette/clips.json'))
fr=load('linette','walk_right');d=[x[1] for x in stance(fr)];t0=C['walk_right']['ticks'];tot=sum(t0)
sp=sum(d)/tot;t1=retime(d,tot)
print('disp',d,'old',t0,slipscore(d,t0,sp),'new',t1,slipscore(d,t1,sp))
video('walk_retime.mp4',[dict(frames=fr,ticks=t0,speed=sp,label='전: 같은 박자'),dict(frames=fr,ticks=t1,speed=sp,label='후: 발 움직인 만큼 박자')])
