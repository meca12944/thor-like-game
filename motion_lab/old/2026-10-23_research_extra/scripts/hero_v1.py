import json,os,numpy as np
from PIL import Image
from fix import *
from render2 import grid
C=json.load(open(R+'hero8/clips.json'));NEW={}
fr=load('hero8','idle_right');NEW['idle_right']=([breathe(a,y) for a,y in zip(fr,[0,-1,-1,0])],C['idle_right']['ticks'])
fr=load('hero8','run_right');d=track(fr);t0=C['run_right']['ticks'];t1=retime(d,sum(t0));NEW['run_right']=(fr,t1)
print('run_right',d,t0,'->',t1,'미끄럼',round(slipscore(d,t0),1),'->',round(slipscore(d,t1),1))
sp=np.mean([x for x in d if x])*len(d)/sum(t0);print('speed',sp)
for k,(f,t) in NEW.items():
    os.makedirs(f'out/hero8/{k}',exist_ok=True)
    for i,a in enumerate(f):Image.fromarray(a).save(f'out/hero8/{k}/{i:03d}.png')
rows=[('서기',[dict(frames=load('hero8','idle_right'),ticks=t0i,label='전'),dict(frames=NEW['idle_right'][0],ticks=t0i,label='후')]) for t0i in [C['idle_right']['ticks']]]
rows+=[('옆 달리기',[dict(frames=load('hero8','run_right'),ticks=t0,vx=sp,label='전'),dict(frames=fr,ticks=t1,vx=sp,label='후')])]
grid('hero_v1.mp4',rows,secs=6,title='주인공: 왼쪽=전, 오른쪽=후')
