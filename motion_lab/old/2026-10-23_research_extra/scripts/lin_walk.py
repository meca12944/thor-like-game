import json,os,numpy as np
from PIL import Image
from fix import *
from render2 import grid
C=json.load(open(R+'linette/clips.json'));NEW={}
def side(k,A=2.6):
    fr=load('linette',k);t0=C[k]['ticks'];d=track(fr);t1=retime(d,sum(t0))
    dy=[round(A*(v-.5)) for v in spread(fr)];NEW[k]=([warp(a,dy=y) for a,y in zip(fr,dy)],t1)
    sp=np.mean([x for x in d if x])*len(d)/sum(t0)
    print(k,'박자',t1,'미끄럼',round(slipscore(d,t0),1),'->',round(slipscore(d,t1),1),'speed',round(sp,2))
for k in ['walk_right','walk_down','walk_up']:side(k)
for k,tc in [('walk_south',True),('walk_north',False)]:
    fr=load('linette',k);nf,dx,dy=front_walk(fr,tc);NEW[k]=(nf,C[k]['ticks'])
fr=load('linette','idle_down');NEW['idle_down']=([breathe(a,y) for a,y in zip(fr,[0,-1,-1,-1,0,0])],C['idle_down']['ticks'])
os.makedirs('out/linette',exist_ok=True)
for k,(f,t) in NEW.items():
    os.makedirs(f'out/linette/{k}',exist_ok=True)
    for i,a in enumerate(f):Image.fromarray(a).save(f'out/linette/{k}/{i:03d}.png')
json.dump({k:{'frames':len(f),'ticks':t} for k,(f,t) in NEW.items()},open('out/linette/clips_new.json','w'))
for k,(f,t) in NEW.items():
    s0,s1=stats(load('linette',k)),stats(f);print(f'{k:11s} 머리 오르내림 {np.ptp(s0[:,0]):.0f}->{np.ptp(s1[:,0]):.0f}  몸 좌우 {np.ptp(s0[:,2]):.1f}->{np.ptp(s1[:,2]):.1f}')
V={'walk_right':(1.9,0),'walk_down':(1.34,1.07),'walk_up':(1.34,-1.07),'walk_south':(0,1.52),'walk_north':(0,-1.52),'idle_down':(0,0)}
NM={'walk_right':'옆 걷기','walk_down':'대각선 아래 걷기','walk_up':'대각선 위 걷기','walk_south':'정면 걷기','walk_north':'뒷면 걷기','idle_down':'대각선 서기'}
rows=[(NM[k],[dict(frames=load('linette',k),ticks=C[k]['ticks'],vx=V[k][0],vy=V[k][1],label='전'),dict(frames=NEW[k][0],ticks=NEW[k][1],vx=V[k][0],vy=V[k][1],label='후')]) for k in NEW]
grid('linette_walk_v1.mp4',rows[:3],secs=6,title='리네트 걷기: 왼쪽=전, 오른쪽=후');grid('linette_walk_v1b.mp4',rows[3:],secs=6,title='리네트 정면·뒷면 걷기, 서기: 왼쪽=전, 오른쪽=후')
