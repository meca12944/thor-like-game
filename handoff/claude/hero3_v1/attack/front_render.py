# 정면 콤보 가안 영상 (그록 11-01 「정면 콤보 넘김」: 2타를 천천히 감았다가 한 번에 지나가는 진짜 베기로, 칼 길이·먼지 색·이음새 고치기)
# 왼쪽 = 그록 원본(분홍 칼, 원래 빠르기) / 가운데 = 게임 장검·잿빛 망토, 원래 빠르기 / 오른쪽 = 게임 장검·잿빛 망토, 고친 판(2타 빠르기 + 튀는 장 뺌)
# 칼 길이: 분홍 칼을 지우고 게임 칼 그림을 손 자리·각도에 그려서 늘 같은 길이. 먼지: 초록빛 먼지를 흙색으로(front_proc.py).
# 쓰는 법: python3 front_render.py <작업 폴더(body/, grip.json, w/)>
import numpy as np, json, os, shutil, subprocess, importlib.util, sys
from PIL import Image, ImageDraw, ImageFont
D=sys.argv[1].rstrip('/')+'/'
# 칼 그리기·몸 합치기는 atk_render2.py 와 같음
WH='/home/user/thor-like-game/handoff/claude/hero3_v1/weapons_hand/'
OF='/home/user/thor-like-game/handoff/claude/hero3_v1/outfit/outfit.py'
spec=importlib.util.spec_from_file_location('of',OF); of=importlib.util.module_from_spec(spec); spec.loader.exec_module(of)
def hand(n):
    im=Image.open(WH+n+'_hand.png').convert('RGBA'); a=np.array(im); w=(a[...,3]>100).sum(1)
    gy=int(np.argmax(w)); xs=np.nonzero(a[gy,:,3]>100)[0]; return im,(xs.min()+xs.max())/2,gy
def sword(hd,gx,gy,ang,size=300):
    im,hx,hy=hd; R=max(im.size)*2+4; c=Image.new('RGBA',(R,R)); c.paste(im,(int(R/2-hx),int(R/2-hy)),im)
    c=c.rotate(-(ang+90),resample=Image.NEAREST); L=Image.new('RGBA',(size,size)); L.paste(c,(int(round(gx-R/2)),int(round(gy-R/2))),c); return L
def comp(body,fr,hd,R=None):
    b=np.array(body)
    if R is not None: b=of.recolor(b,R)[0]
    B=Image.fromarray(b); sw=sword(hd,fr['guard'][0],fr['guard'][1],fr['ang']); out=Image.new('RGBA',B.size)
    if fr['behind']: out.alpha_composite(sw); out.alpha_composite(B)
    else:
        out.alpha_composite(B); out.alpha_composite(sw)
        a=np.array(B); r,g,bb=[a[...,i].astype(int) for i in range(3)]; skin=(a[...,3]>100)&(r>110)&(r>bb+30)&(g>70)
        yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]; m=skin&((xx-fr['guard'][0])**2+(yy-fr['guard'][1])**2<81); o=np.array(out); o[m]=a[m]; out=Image.fromarray(o)
    return out
J=json.load(open(D+'grip.json')); FR=J['frames']; S=144/569
# 원래 빠르기: 24장/초 → 60장/초 (3,2,3,2…)
ORIG=[(k,3 if j%2==0 else 2) for j,k in enumerate(range(len(FR)))]
# 2타(72~108장) 고친 빠르기 (60장/초 칸 수): 천천히 감기 → 80장에서 잠깐 멈춤 → 한 번에 지나감(5칸) → 천천히 멈춤
H2=[(72,3),(74,3),(76,3),(78,4),(80,6), (82,1),(84,1),(88,1),(90,2), (92,2),(94,2),(96,3),(98,3),(100,4),(102,5),(104,5),(106,4),(108,4)]
# 튀는 장 빼기: 130장(되돌려베기 중 칼끝 방향을 잘못 잡음), 184~191장(칼이 머리 뒤로 숨었다가 위로 뒤집힘), 197장(칼이 거의 안 보임)
SKIP={130,197}|set(range(184,192))
NEW=[x for x in ORIG if x[0]<72]+H2+[x for x in ORIG if 108<x[0]<182 and x[0] not in SKIP]+[(182,8)]+[x for x in ORIG if x[0]>182 and x[0] not in SKIP]   # 182장(머리 위로 든 장)에서 잠깐 멈췄다 내려찍기
def expand(L): return [k for k,n in L for _ in range(n)]
A,B=expand(ORIG),expand(NEW); B=B+[B[-1]]*(len(A)-len(B))
from functools import lru_cache
@lru_cache(None)
def orig(k):
    a=np.asarray(Image.open(f"{D}w/{k:04d}.png").convert('RGB')).astype(np.float32); r,g,b=a[...,0],a[...,1],a[...,2]
    al=np.clip(1-(g-np.maximum(r,b)-40)/60,0,1); im=Image.fromarray(np.dstack([a,al*255]).astype(np.uint8)); return im.resize((round(960*S),round(960*S)),Image.LANCZOS)
o0=Image.open(D+'body/000.png').getbbox(); b0=orig(0).getbbox(); ox,oy=o0[0]-b0[0],o0[3]-b0[3]
F1=ImageFont.truetype(of.FONT,26); F2=ImageFont.truetype(of.FONT,22)
H1=hand('w_loop_long'); RA=of.ramp('c_ash_cloak')
cache={}
def game(k):
    if k not in cache: cache[k]=comp(Image.open(f'{D}body/{k:03d}.png'),FR[k],H1,RA)
    return cache[k]
def part(k): return '1타 내려베기' if k<72 else ('2타 가로베기' if k<=108 else ('되돌려베기' if k<168 else '내려찍기'))
out=D+'vid/'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
K=3; seq=list(zip(A,B)); seq=seq+[seq[-1]]*30+seq
for n,(ka,kb) in enumerate(seq):
    C=Image.new('RGB',(1920,1080),(58,66,52)); d=ImageDraw.Draw(C); d.rectangle([0,858,1920,1080],fill=(84,74,58))
    og=Image.new('RGBA',(300,300)); im=orig(ka); og.paste(im,(ox,oy),im)
    for j,(im,name,k) in enumerate([(og,'그록 원본 (분홍 칼 · 원래 빠르기)',ka),(game(ka),'게임 칼 · 원래 빠르기',ka),(game(kb),'게임 칼 · 고친 판 (2타 빠르게 · 튀는 장 뺌)',kb)]):
        z=im.resize((900,900),Image.NEAREST); C.paste(z,(640*j+320-450,858-J['foot']*K),z)
        d.text((640*j+36,28),name,font=F1,fill=(255,235,150)); d.text((640*j+36,1010),f'{part(k)} · {k}장',font=F2,fill=(235,235,235))
    C.save(out+f'{n:04d}.jpg',quality=92)
subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',out+'%04d.jpg','-c:v','libx264','-pix_fmt','yuv420p','-crf','20',D+'정면콤보_2타가속_가안.mp4'],check=True)
print('ok',len(seq),'장(60/초)','원래',len(expand(ORIG)),'고친',len(expand(NEW)))
