"""주인공 달리기 4방향 다시 (사장님 10-24 "달리기 다시 그려", 팀장 기준: 8방향 키 ±3%, 팔은 다리 반대로 장마다 다른 위치).
 교본 9: 배율 1(같은 서기에서 편집), 동작 하나에 한 번만 옮김, 땅 190. 뒷모습(↗·↑)은 그림 도구가 다리를 길게 그려 허리 아래만 줄여 키를 옆 달리기와 맞춤.
 머리(정수리) 위치 = 옆 +18 · 대각 +14 · 뒷모습 0 (몸을 숙인 만큼 앞으로). 옆·↘ 는 서기 얼굴 도장."""
import json,os,sys,numpy as np
from PIL import Image
from fix import boot_bot
from facefix import ref_head,place2
sys.path.insert(0,'/home/user/thor-like-game/motion_lab/research_v2/tools')
from headx import headx
from measure8 import body
OUT='/home/user/thor-like-game/motion_lab/research_v1/hero8/frames';LATEST='/home/user/thor-like-game/motion_lab/hero8/frames'
def squash(a,h0,f):
    im=Image.fromarray(a);top=im.crop((0,0,256,h0));bot=im.crop((0,h0,256,256));nb=bot.resize((256,max(1,round((256-h0)*f))),Image.BOX)
    o=Image.new('RGBA',(256,256));o.paste(top,(0,0));o.paste(nb,(0,h0),nb);b=np.array(o)
    pal=np.unique(a[a[...,3]>200][:,:3],axis=0).astype(int);m=b[...,3]>110;px=b[m][:,:3].astype(int)
    idx=np.argmin(((px[:,None,:]-pal[None,:,:])**2).sum(2),1);b[m,:3]=pal[idx];b[...,3]=np.where(m,255,0);return b
def bodytop(a):m=body(a);return int(np.nonzero(m.any(1))[0].min())
L=lambda k:[np.array(Image.open(f'pl/cyc_run3_{k}/{i:03d}.png').convert('RGBA')) for i in range(8)] if k!='n' else [np.array(Image.open(f'{LATEST}/run_n/{f}').convert('RGBA')) for f in sorted(os.listdir(f'{LATEST}/run_n'))]
# ↑(똑바른 뒷모습)은 새로 그린 한 바퀴가 칼을 머리 위로 치켜드는 장이 섞여 안 씀 -> 지금 게임 그림(10-23)을 다리만 더 줄여 키를 맞춤
H=int(sys.argv[1]) if len(sys.argv)>1 else 114   # 목표 달리기 키(머리 위~발): 옆 달리기 그대로 재서 정함
C={};LEAN={'r':18,'dr':14,'up':14,'n':0}
for k,name in [('r','run_right'),('dr','run_dr'),('up','run_up'),('n','run_n')]:
    fr=L(k)
    if k in('up','n'):   # 뒷모습: 다리가 길게 그려짐 -> 허리 아래만 줄여 (발 중앙값 - 머리 중앙값) = H
        tops=np.median([bodytop(a) for a in fr]);bots=np.median([int(np.nonzero(a[...,3]>40)[0].max()) for a in fr]);f=(tops+H-100)/(bots-100)
        if f<1:fr=[squash(a,100,f) for a in fr]
        print(name,'다리 배율',round(f,3))
    fb=(lambda a:int(np.nonzero(a[...,3]>40)[0].max())) if k=='n' else boot_bot
    dy=190-max(fb(a) for a in fr);out=[np.roll(a,dy,0) for a in fr]
    if k in('r','dr'):out=[np.roll(a,max(0,186-boot_bot(a)),0) for a in out]   # 옆·대각은 공중 4칸까지
    sh=int(round(128+LEAN[k]-np.mean([headx(a)[0] for a in out])));out=[np.roll(a,sh,1) for a in out]
    C[name]=out;print(name,'옮김',sh,dy,'발',[boot_bot(a) for a in out],'머리',[bodytop(a) for a in out])
for name,ref in [('run_right','idle_right'),('run_dr','idle_dr')]:
    r=np.array(Image.open(f'{LATEST}/{ref}/000.png').convert('RGBA'));P,M=ref_head(r);o=[];n=0
    for a in C[name]:
        b,sc=place2(a,P,M,thr=0.3);n+=sc is not None and sc>=0.3;o.append(b)
    C[name]=o;print(name,'얼굴 도장',n)
CJ='/home/user/thor-like-game/motion_lab/research_v1/hero8/clips.json';J=json.load(open(CJ))
for k,fr in C.items():
    os.makedirs(f'{OUT}/{k}',exist_ok=True)
    for f in os.listdir(f'{OUT}/{k}'):os.remove(f'{OUT}/{k}/{f}')
    for i,a in enumerate(fr):Image.fromarray(a).save(f'{OUT}/{k}/{i:03d}.png')
    J[k]={'frames':8,'ticks':[3,3,3,4,3,3,3,4]}
json.dump(J,open(CJ,'w'),ensure_ascii=False,indent=1)
