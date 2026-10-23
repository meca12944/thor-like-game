"""주인공 곧장 위(↑) 똑바른 뒷모습: 서기·걷기·달리기 (교본 0부 3·4·9). 크기 그대로(같은 서기 그림에서 편집), 동작 하나에 한 번만 옮김: 머리 가운데 = 발 기준점(좌우 대칭이라), 발 = 땅(190), 달리기 공중 4칸까지."""
import json,os,sys,numpy as np
from PIL import Image
from scipy import ndimage
from fix import boot_bot
OUT='/home/user/thor-like-game/motion_lab/research_v1/hero8/frames'
def crown(a):
    col=a[...,:3].astype(int);m=(a[...,3]>40)&~ndimage.binary_dilation((col.min(2)>150)&(col.max(2)-col.min(2)<40))
    t=np.nonzero(m.any(1))[0].min();return np.nonzero(m[t:t+10])[1].mean()
L=lambda d,n:[np.array(Image.open(f'pl/{d}/{i:03d}.png').convert('RGBA')) for i in range(n)]
C={'idle_n':([L('cyc_idle_n',4)[i] for i in (0,1,2,3,2,1)],[8]*6),'walk_n':(L('cyc_walk_n',8),[3,4,4,4,4,4,4,4]),'run_n':(L('cyc_run_n',8),[3,3,3,4,3,3,3,4])}
ref=crown(np.array(Image.open('pl/key_idle_n.png').convert('RGBA')))
def squash(a,h0,f):   # 다리만 줄임(머리·몸통 그대로): 뒷모습 걷기·달리기를 그림 도구가 다리를 길게(키 +20) 그려서
    im=Image.fromarray(a);top=im.crop((0,0,256,h0));bot=im.crop((0,h0,256,256));nb=bot.resize((256,max(1,round((256-h0)*f))),Image.BOX)
    o=Image.new('RGBA',(256,256));o.paste(top,(0,0));o.paste(nb,(0,h0),nb);b=np.array(o)
    pal=np.unique(a[a[...,3]>200][:,:3],axis=0).astype(int);m=b[...,3]>110;px=b[m][:,:3].astype(int)
    idx=np.argmin(((px[:,None,:]-pal[None,:,:])**2).sum(2),1);b[m,:3]=pal[idx];b[...,3]=np.where(m,255,0);return b
for k in ('walk_n','run_n'):
    fr,t=C[k];bots=[int(np.nonzero(a[...,3]>40)[0].max()) for a in fr];f=(192-100)/(np.median(bots)-100);C[k]=([squash(a,100,f) for a in fr],t);print(k,'다리 배율',round(f,3))
for k,(fr,t) in C.items():
    dx=int(round(128-np.mean([crown(a) for a in fr])));dy=0
    out=[np.roll(np.roll(a,dy,0),dx,1) for a in fr]
    os.makedirs(f'{OUT}/{k}',exist_ok=True)
    for f in os.listdir(f'{OUT}/{k}'):os.remove(f'{OUT}/{k}/{f}')
    for i,a in enumerate(out):Image.fromarray(a).save(f'{OUT}/{k}/{i:03d}.png')
    print(k,'옮김',dx,dy,'발',[boot_bot(a) for a in out],'머리위',[int(np.nonzero(a[...,3]>40)[0].min()) for a in out])
CJ='/home/user/thor-like-game/motion_lab/research_v1/hero8/clips.json';J=json.load(open(CJ))
for k,(fr,t) in C.items():J[k]={'frames':len(fr),'ticks':t}
json.dump(J,open(CJ,'w'),ensure_ascii=False,indent=1)
