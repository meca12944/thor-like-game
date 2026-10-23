"""주인공 ↘(↙는 뒤집기) 비스듬 앞모습 세트: 서기·대시·점프는 예전 그림(10-20) 다시 쓰기, 걷기·달리기는 새 그림(넓은 보폭).
 크기·땅은 동작 하나에 한 번, 땅에 묻힌 장만 올림, 서기 얼굴을 도장."""
import json,os,numpy as np
from PIL import Image
from fix import feet_bot,head_y,boot_bot,stats
from assemble_new import build
from facefix import ref_head,place2
R='/home/user/thor-like-game/test128/sandbox/assets/';A=json.load(open(R+'hero_sbx.json'));SH={}
OUT='/home/user/thor-like-game/motion_lab/research_v1/hero8/frames'
def old(k):
    o=[]
    for e in A['anims'][k]:
        p=A['sheets'][e[0]]
        if p not in SH:SH[p]=Image.open(R+p).convert('RGBA')
        x,y,w,h,ax,ay=A['cells'][e[0]][e[1]][:6];c=Image.new('RGBA',(256,256));t=SH[p].crop((x,y,x+w,y+h));c.paste(t,(128-ax,189-ay),t);o.append(np.array(c))
    return o
idle=old('idle_down')
lift=lambda fr,G=190:[np.roll(a,min(0,G-boot_bot(a)),0) for a in fr]
C={}
C['idle_dr']=(idle,[6]*12)
C['dash_dr']=(lift(old('dash_down')),[1,1,4,4,3,2,2])
C['jump_dr']=(lift(old('jump_down')),[3]*15)
for src,k in [('cyc_walk_dr','walk_dr'),('cyc_run_dr','run_dr')]:
    fr=build(src,idle,190,k+'_tmp')
    C[k]=(fr,[3,4,4,4,4,4,4,4] if 'walk' in k else [3,3,3,4,3,3,3,4])
P,M=ref_head(idle[0]);stamped={}
for k,(fr,t) in C.items():
    if k=='idle_dr':continue
    o=[];n=0
    for a in fr:
        b,sc=place2(a,P,M,thr=0.3)
        if sc is not None and sc>=0.3:n+=1
        o.append(b)
    C[k]=(o,t);stamped[k]=f'{n}/{len(fr)}'
for k,(fr,t) in C.items():
    os.makedirs(f'{OUT}/{k}',exist_ok=True)
    for f in os.listdir(f'{OUT}/{k}'):os.remove(f'{OUT}/{k}/{f}')
    for i,a in enumerate(fr):Image.fromarray(a).save(f'{OUT}/{k}/{i:03d}.png')
CJ='/home/user/thor-like-game/motion_lab/research_v1/hero8/clips.json';J=json.load(open(CJ))
for k,(fr,t) in C.items():J[k]={'frames':len(fr),'ticks':t}
json.dump(J,open(CJ,'w'),ensure_ascii=False,indent=1)
print('얼굴 도장',stamped);print({k:[boot_bot(a) for a in fr] for k,(fr,t) in C.items()})
