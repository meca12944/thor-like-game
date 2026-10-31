# 가안 영상: 왼쪽 = 그록 영상(같은 크기), 가운데 = 게임(장검·원래 옷), 오른쪽 = 게임(대검·아라크네 망토 옷)
import numpy as np, json, os, shutil, subprocess, importlib.util
from PIL import Image, ImageDraw, ImageFont
D=os.path.dirname(os.path.abspath(__file__))+'/'
WH='/home/user/thor-like-game/handoff/claude/hero3_v1/weapons_hand/'
OF='/home/user/thor-like-game/handoff/claude/hero3_v1/outfit/outfit.py'
spec=importlib.util.spec_from_file_location('of',OF); of=importlib.util.module_from_spec(spec); spec.loader.exec_module(of)
J=json.load(open(D+'grip.json')); FRS=J['frames']
def hand(n):
    im=Image.open(WH+n+'_hand.png').convert('RGBA'); a=np.array(im); w=(a[...,3]>100).sum(1)
    gy=int(np.argmax(w)); xs=np.nonzero(a[gy,:,3]>100)[0]; gx=(xs.min()+xs.max())/2
    return im,gx,gy
def sword_layer(hd,gx,gy,ang,size=300):
    # 칼끝이 위(0,-1)인 그림을 각도 ang(화면, 0=오른쪽, 90=아래)로 돌려 코등이를 (gx,gy)에
    im,hx,hy=hd; R=max(im.size)*2+4
    c=Image.new('RGBA',(R,R)); c.paste(im,(int(R/2-hx),int(R/2-hy)),im)
    rot=ang+90   # 위쪽(−90°) → ang
    c=c.rotate(-rot,resample=Image.NEAREST)
    L=Image.new('RGBA',(size,size)); L.paste(c,(int(round(gx-R/2)),int(round(gy-R/2))),c); return L
def compose(body,fr,hd,recolorR=None):
    b=np.array(body)
    if recolorR is not None: b=of.recolor(b,recolorR)[0]
    B=Image.fromarray(b); gx,gy=fr['guard']; sw=sword_layer(hd,gx,gy,fr['ang'])
    out=Image.new('RGBA',B.size)
    if fr['behind']:
        out.alpha_composite(sw); out.alpha_composite(B)
    else:
        out.alpha_composite(B); out.alpha_composite(sw)
        # 손가락: 코등이 둘레 몸의 살색 칸은 칼 위로 다시
        a=np.array(B); r,g,bb=a[...,0].astype(int),a[...,1].astype(int),a[...,2].astype(int)
        skin=(a[...,3]>100)&(r>110)&(r>bb+30)&(g>70)
        yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]; near=(xx-gx)**2+(yy-gy)**2<9**2
        m=skin&near; o=np.array(out); o[m]=a[m]; out=Image.fromarray(o)
    return out
FONT=ImageFont.truetype(of.FONT,26); F2=ImageFont.truetype(of.FONT,20)
H1=hand('w_loop_long'); H2=hand('w_heretic_great'); R2=of.ramp('c_ara_silk')
out=D+'vid/'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
# 그록 원본도 같은 크기로(분홍 칼 그대로)
def orig(k):
    a=np.asarray(Image.open(f'{D}f/{k:04d}.png').convert('RGB')).astype(np.float32)
    r,g,b=a[...,0],a[...,1],a[...,2]; green=g-np.maximum(r,b); al=np.clip(1-(green-40)/60,0,1)
    im=Image.fromarray(np.dstack([a,al*255]).astype(np.uint8)); s=J['scale']
    return im.resize((round(540*s),round(540*s)),Image.LANCZOS)
b0=Image.open(D+'body/000.png').getbbox()
K=3; W,H=1920,1080; N=len(FRS); rep=[3,2]  # 24장/초 → 60장/초 (3,2,3,2…)
t=0; seq=[]
for i in range(N): seq+=[i]*rep[i%2]
seq=seq+seq   # 두 번
for f_i,i in enumerate(seq):
    fr=FRS[i]; body=Image.open(f'{D}body/{i:03d}.png')
    C=Image.new('RGB',(W,H),(58,66,52)); d=ImageDraw.Draw(C)
    d.rectangle([0,860,W,H],fill=(72,64,50))
    panels=[(orig(fr['k']),'그록 시안 (분홍 임시 칼)'),(compose(body,fr,H1),'게임: 장검 · 지금 옷'),(compose(body,fr,H2,R2),'게임: 이단 대검 · 아라크네 망토 옷')]
    for j,(im,name) in enumerate(panels):
        if j==0:
            # 같은 발 자리에 맞춤
            z=im.resize((im.width*K,im.height*K),Image.NEAREST); fx=640*j+320-int(J['scale']*270*K); fy=860-int(J['scale']*463*K)
            C.paste(z,(fx,fy),z)
        else:
            z=im.resize((im.width*K,im.height*K),Image.NEAREST); C.paste(z,(640*j+320-150*K,860-J['foot']*K),z)
        d.text((640*j+40,30),name,font=FONT,fill=(255,235,150))
    d.text((40,1000),f'영상 {fr["k"]}장 · 칼 {"몸 뒤" if fr["behind"] else "몸 앞"} · 각도 {round(fr["ang"])}°',font=F2,fill=(230,230,230))
    C.save(out+f'{f_i:04d}.png')
subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',out+'%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',D+'공격4타_옆_시안_게임가안.mp4'],check=True)
print('ok',len(seq))
