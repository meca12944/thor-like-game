"""모션 연구 v1: 그림은 그대로, 코드로만 — 박자(발 미끄럼), 몸 오르내림, 좌우 몸무게 옮김, 숨쉬기, 달리기 높이 튐"""
import json,os,shutil,numpy as np
from PIL import Image
from fix import *
LOG=[]
def side_walk(fr,t0,A=2.6):
    d=track(fr);t1=retime(d,sum(t0)) or list(t0);nf,o,nd=footlock(fr,d,t1,lim=2)
    dy=[round(A*(v-.5)) for v in spread(fr)];nf=[warp(a,dy=y) for a,y in zip(nf,dy)]
    return nf,t1,dict(slip=(slipscore(d,t0),slipscore(nd,t1)))
def run(fr,t0,flatten=False,lim=3):
    d=track(fr);t1=retime(d,sum(t0)) or list(t0);nf,o,nd=footlock(fr,d,t1,lim)
    if flatten:
        hy=head_y(fr).astype(float);m=hy.mean();dy=[int(round(.4*(h-m)+m-h)) for h in hy];nf=[warp(a,dy=y) for a,y in zip(nf,dy)]
    return nf,t1,dict(slip=(slipscore(d,t0),slipscore(nd,t1)))
PLAN={'linette':{
  'walk_right':side_walk,'walk_left':side_walk,'walk_down':side_walk,'walk_downl':side_walk,'walk_up':side_walk,'walk_upl':side_walk,
  'walk_south':lambda f,t:(front_walk(f,True)[0],t,{}),'walk_north':lambda f,t:(front_walk(f,False)[0],t,{}),
  'run_right':run,'run_left':run,'run_down':run,'run_downl':run,
  'run_up':lambda f,t:run(f,t,True),'run_upl':lambda f,t:run(f,t,True),
  'idle_down':lambda f,t:([breathe(a,y) for a,y in zip(f,[0,-1,-1,-1,0,0])],t,{}),
  'idle_downl':lambda f,t:([breathe(a,y) for a,y in zip(f,[0,-1,-1,-1,0,0])],t,{})},
 'hero8':{'run_right':lambda f,t:run(f,t,lim=2),'idle_right':lambda f,t:([breathe(a,y) for a,y in zip(f,[0,-1,-1,0])],t,{})}}
shutil.rmtree('out',ignore_errors=True)
for ch,P in PLAN.items():
    C=json.load(open(R+ch+'/clips.json'));NEWC={}
    for k,fn in P.items():
        fr=load(ch,k);t0=C[k]['ticks'];L=k.endswith(('left','downl','upl'))
        nf,t1,info=fn([a[:,::-1].copy() for a in fr] if L else fr,t0)
        if L:nf=[a[:,::-1].copy() for a in nf]
        os.makedirs(f'out/{ch}/{k}',exist_ok=True)
        for i,a in enumerate(nf):Image.fromarray(a).save(f'out/{ch}/{k}/{i:03d}.png')
        NEWC[k]={'frames':len(nf),'ticks':[int(x) for x in t1]}
        s0,s1=stats(fr),stats(nf);h0,h1=head_y(fr),head_y(nf)
        LOG.append(f"{ch:7s} {k:11s} 박자 {t0}->{NEWC[k]['ticks']} 머리 {np.ptp(h0)}->{np.ptp(h1)} 좌우 {np.ptp(s0[:,2]):.1f}->{np.ptp(s1[:,2]):.1f}"+(f" 미끄럼 {info['slip'][0]:.0f}->{info['slip'][1]:.0f}" if 'slip' in info else ''))
    json.dump(NEWC,open(f'out/{ch}/clips_changed.json','w'),indent=1)
open('out/log.txt','w').write('\n'.join(LOG));print('\n'.join(LOG))
