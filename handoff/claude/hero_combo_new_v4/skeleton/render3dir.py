# → ↘ ↗ showcase of the new combo with fast links + Linette FX (hit 1, hit 3), real speed x2 then 1/3 slow
import sys,random,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
sys.path.insert(0,'newatk');import linette_fx as LF
OUT=sys.argv[1]
def blade(im):
    a=np.array(im.convert('RGBA')).astype(int);r,g,b,al=[a[...,i] for i in range(4)];mn=np.minimum(np.minimum(r,g),b);mx=np.maximum(np.maximum(r,g),b)
    st=(al>0)&(mn>115)&(mx-mn<60);lab,n=ndimage.label(st,structure=np.ones((3,3)));sz=ndimage.sum(st,lab,range(1,n+1));i=int(np.argmax(sz))+1;ys,xs=np.nonzero(lab==i)
    c=np.array([128,130]);d=np.hypot(xs-c[0],ys-c[1]);tip=np.array([xs[d.argmax()],ys[d.argmax()]]);hilt=np.array([xs[d.argmin()],ys[d.argmin()]]);v=tip-hilt;return tuple(tip.tolist()),tuple((v/np.linalg.norm(v)).tolist())
PLAN={'hit1':[(i,1) for i in range(9)]+[(9,2),(10,1),(12,1),(14,1)],'hit2':[(0,1),(2,1),(4,1),(5,1),(6,1),(7,1),(8,1),(10,1),(12,1),(14,2)],
      'hit3':[(0,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,2),(11,2),(12,2),(13,2),(14,3)]}
SF={'hit1':9,'hit3':10};HIT={'hit1':(4,1.5,False,False),'hit3':(9,4,True,True)}
def frame(v,c,i):return Image.open(f'newatk/clean/{c}_{i:02d}.png' if v=='side' else f'newatk/clean34/{c}_{v}_{i:02d}.png').convert('RGBA')
IDLE={'side':'/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/east/000.png','se':'q34/rot_south-east.png','ne':'q34/rot_north-east.png'}
def timeline(v):
    out=[];idle=Image.open(IDLE[v]).convert('RGBA');active=[];shake=0;waves=[];flash=0;rnd=random.Random(2)
    for _ in range(14):out.append((idle,[],(0,0,0),[],0))
    for c in ('hit1','hit2','hit3'):
        for f,t in PLAN[c]:
            im=frame(v,c,f);strike=(c in SF and f==SF[c]);stop=HIT[c][0] if strike else 0
            if strike:
                tip,dr=blade(im);big,heavy=HIT[c][2],HIT[c][3];active.append({'tip':tip,'dr':dr,'big':big,'heavy':heavy,'age':0});shake=max(shake,HIT[c][1])
                if heavy:waves.append({'x':tip[0]+dr[0]*50,'y':183,'a':0});flash=4
            for k in range(t+stop):
                out.append((im,[dict(a) for a in active],(shake,rnd.random(),rnd.random()),[dict(w) for w in waves],flash))
                if not (strike and k<stop):
                    for a in active:a['age']+=1
                for w in waves:w['a']+=1
                waves=[w for w in waves if w['a']<16];active=[a for a in active if a['age']<20];shake=shake*.82 if shake>.3 else 0;flash=max(0,flash-1)
    for _ in range(24):out.append((idle,[],(0,0,0),[],0))
    return out
if __name__=='__main__':
    import os;os.makedirs(OUT,exist_ok=True)
    TL={k:timeline(k) for k in ('side','se','ne')};L=max(len(t) for t in TL.values());n=0
    LAB={'side':'→ (← 반전)','se':'↘ (↙ 반전)','ne':'↗ (↖ 반전)'}
    for slow in (1,1,3):
        for i in range(L):
            fr=Image.new('RGB',(1440,380),(20,20,20))
            for j,k in enumerate(('side','se','ne')):
                s=TL[k][min(i,len(TL[k])-1)];f=LF.render(s,lab='새 공격 '+LAB[k]+(' · 1/3 슬로우' if slow>1 else ''));fr.paste(f.convert('RGB'),(j*480,0))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
