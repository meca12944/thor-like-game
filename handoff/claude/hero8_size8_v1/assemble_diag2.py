"""대각선 보폭 넓게 다시 (사장님 10-23 "둘다 실행해라"): ↘ 걷기·달리기, ↗ 달리기. 교본 9: 크기 그대로(같은 서기에서 편집), 동작 하나에 한 번만 옮김,
 땅 = 190, 달리기 공중 4칸까지(↗ 뒷모습 달리기는 먼 발이 화면에서 위라 공중 제한 안 함 — 하면 머리가 15칸 출렁). ↗ 달리기는 그림 도구가 다리를 길게(발 +15) 그려서 허리 아래만 줄임. ↘ 는 서기 얼굴 도장."""
import json,os,sys,numpy as np
from PIL import Image
from fix import boot_bot
from measure import stats
from facefix import ref_head,place2
sys.path.insert(0,'/home/user/thor-like-game/handoff/claude/hero8_north_v1')
OUT='/home/user/thor-like-game/motion_lab/research_v1/hero8/frames'
def squash(a,h0,f):
    im=Image.fromarray(a);top=im.crop((0,0,256,h0));bot=im.crop((0,h0,256,256));nb=bot.resize((256,max(1,round((256-h0)*f))),Image.BOX)
    o=Image.new('RGBA',(256,256));o.paste(top,(0,0));o.paste(nb,(0,h0),nb);b=np.array(o)
    pal=np.unique(a[a[...,3]>200][:,:3],axis=0).astype(int);m=b[...,3]>110;px=b[m][:,:3].astype(int)
    idx=np.argmin(((px[:,None,:]-pal[None,:,:])**2).sum(2),1);b[m,:3]=pal[idx];b[...,3]=np.where(m,255,0);return b
L=lambda d:[np.array(Image.open(f'pl/{d}/{i:03d}.png').convert('RGBA')) for i in range(8)]
ref_dr=[np.array(Image.open(f'{OUT}/idle_dr/{f}').convert('RGBA')) for f in sorted(os.listdir(f'{OUT}/idle_dr'))]
ref_up=np.array(Image.open('pl/src_idle_up_now.png').convert('RGBA'))
C={}
def place(fr,ref,run):
    dy=190-max(boot_bot(a) for a in fr);dx=int(round(np.median(stats(ref)[:,2])-np.median(stats(fr)[:,2])))
    out=[np.roll(np.roll(a,dy,0),dx,1) for a in fr]
    if run:out=[np.roll(a,max(0,186-boot_bot(a)),0) for a in out]
    return out,dx,dy
for src,k,ref,run in [('cyc_walk_dr2','walk_dr',ref_dr,0),('cyc_run_dr3','run_dr',ref_dr,1),('cyc_run_up2','run_up',[ref_up],0)]:
    fr=L(src)
    if k=='run_up':
        bots=[int(np.nonzero(a[...,3]>40)[0].max()) for a in fr];f=(191-100)/(np.median(bots)-100);fr=[squash(a,100,f) for a in fr];print(k,'다리 배율',round(f,3))
    out,dx,dy=place(fr,ref,run)
    if k=='run_up':   # 몸통 기준으로 옮기면 휘날리는 망토 때문에 머리가 28칸 앞 -> ↘ 달리기처럼 머리 +14
        sys.path.insert(0,'/home/user/thor-like-game/motion_lab/research_v2/tools');from headx import headx
        sh=int(round(142-np.mean([headx(a)[0] for a in out])));out=[np.roll(a,sh,1) for a in out];dx+=sh
    C[k]=out;print(k,'옮김',dx,dy,'발',[boot_bot(a) for a in out],'머리위',[int(np.nonzero(a[...,3]>40)[0].min()) for a in out])
P,M=ref_head(ref_dr[0])
for k in ('walk_dr','run_dr'):
    o=[];n=0
    for a in C[k]:
        b,sc=place2(a,P,M,thr=0.3);n+=sc is not None and sc>=0.3;o.append(b)
    C[k]=o;print(k,'얼굴 도장',n,'/',len(o))
T={'walk_dr':[3,4,4,4,4,4,4,4],'run_dr':[3,3,3,4,3,3,3,4],'run_up':[3,3,3,4,3,3,3,4]}
CJ='/home/user/thor-like-game/motion_lab/research_v1/hero8/clips.json';J=json.load(open(CJ))
for k,fr in C.items():
    os.makedirs(f'{OUT}/{k}',exist_ok=True)
    for f in os.listdir(f'{OUT}/{k}'):os.remove(f'{OUT}/{k}/{f}')
    for i,a in enumerate(fr):Image.fromarray(a).save(f'{OUT}/{k}/{i:03d}.png')
    J[k]={'frames':len(fr),'ticks':T[k]}
json.dump(J,open(CJ,'w'),ensure_ascii=False,indent=1)
