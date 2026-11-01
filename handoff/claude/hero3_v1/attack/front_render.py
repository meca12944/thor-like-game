# 정면 콤보 가안 영상 (그록 11-01 「정면 콤보 넘김」: 2타를 천천히 감았다가 한 번에 지나가는 진짜 베기로, 칼 길이·먼지 색·이음새 고치기)
# 2타 비교 영상: 원래 빠르기 / 부드럽게 판(모든 장 + 빠르기 곡선 → 사장님 「베는 게 아니라 칼이 움직이는 거 같다」) / 베기 판(감기 → 3장에 휙 + 코드로 그린 검기 → 끝 자세 멈춤)
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
    gy=int(np.argmax(w)); xs=np.nonzero(a[gy,:,3]>100)[0]; top=int(np.nonzero(w)[0][0]); return im,(xs.min()+xs.max())/2,gy,gy-top
def sword(hd,gx,gy,ang,size=300,s=1.0):
    im,hx,hy,_=hd
    if s<.999: im=im.resize((im.width,max(1,round(im.height*s))),Image.NEAREST); hy=hy*s
    R=max(im.size)*2+4; c=Image.new('RGBA',(R,R)); c.paste(im,(int(R/2-hx),int(R/2-hy)),im)
    c=c.rotate(-(ang+90),resample=Image.NEAREST); L=Image.new('RGBA',(size,size)); L.paste(c,(int(round(gx-R/2)),int(round(gy-R/2))),c); return L
def comp(body,fr,hd,R=None):
    b=np.array(body)
    if R is not None: b=of.recolor(b,R)[0]
    # 칼끝이 발 높이 밑으로 가면(땅에 꽂힌 것처럼 보임) 칼을 카메라 쪽으로 기운 것처럼 짧게: 칼끝 = 발 4칸 위 (그록 「검을 땅에 꽂지 않음」)
    dy=np.sin(np.radians(fr['ang']))*hd[3]; lim=FOOT-4; s=1.0
    if dy>0 and fr['guard'][1]+dy>lim: s=max(.5,(lim-fr['guard'][1])/dy)
    B=Image.fromarray(b); sw=sword(hd,fr['guard'][0],fr['guard'][1],fr['ang'],s=s); out=Image.new('RGBA',B.size)
    if fr['behind']: out.alpha_composite(sw); out.alpha_composite(B)
    else:
        out.alpha_composite(B); out.alpha_composite(sw)
        a=np.array(B); r,g,bb=[a[...,i].astype(int) for i in range(3)]; skin=(a[...,3]>100)&(r>110)&(r>bb+30)&(g>70)
        yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]; m=skin&((xx-fr['guard'][0])**2+(yy-fr['guard'][1])**2<81); o=np.array(out); o[m]=a[m]; out=Image.fromarray(o)
    return out
J=json.load(open(D+'grip.json')); FR=J['frames']; S=144/569; FOOT=J['foot']
# 칼이 흐려 거의 안 보이는 장(칼날 40칸 밑)은 칼 자리·각도를 앞뒤 멀쩡한 장 사이로 이어 줌(짧은 쪽으로 돌기) → 칼이 끊기지 않고 지나감
ok=[f['blade']>=40 for f in FR]
for k,f in enumerate(FR):
    if ok[k]: continue
    p=max([i for i in range(k) if ok[i]],default=None); n=min([i for i in range(k+1,len(FR)) if ok[i]],default=None)
    if p is None or n is None: continue
    t=(k-p)/(n-p); a0,a1=FR[p]['ang'],FR[n]['ang']; da=(a1-a0+180)%360-180
    f['ang']=a0+da*t; f['guard']=[FR[p]['guard'][i]*(1-t)+FR[n]['guard'][i]*t for i in range(2)]; f['behind']=False
# 원래 빠르기: 24장/초 → 60장/초 (3,2,3,2…)
ORIG=[(k,3 if j%2==0 else 2) for j,k in enumerate(range(len(FR)))]
SKIP={197}|set(range(184,192))   # 184~191: 칼이 머리 뒤로 숨었다 뒤집힘 → 182장에서 잠깐 멈췄다 내려찍기
def rest(lo): return [x for x in ORIG if lo<x[0]<182 and x[0] not in SKIP]+[(182,8)]+[x for x in ORIG if x[0]>182 and x[0] not in SKIP]
# 먼저 고친 판(끊김): 2장씩 건너뛰고 80장에서 6칸 멈췄다 4장을 1칸씩
H2_OLD=[(72,3),(74,3),(76,3),(78,4),(80,6),(82,1),(84,1),(88,1),(90,2),(92,2),(94,2),(96,3),(98,3),(100,4),(102,5),(104,5),(106,4),(108,4)]
# 새로 고친 판: 72~108장을 한 장도 안 빼고, 빠르기가 매끄럽게 바뀌는 곡선(틱 → 장)으로. 감기(원래 빠르기) → 80~90장을 6칸에 휙 → 천천히 멈춤
from scipy.interpolate import PchipInterpolator
KN=PchipInterpolator([-5,0,20,26,50,55],[70,72,80,90,108,110])
def smooth2():
    L=[]; last=None
    for t in range(0,51):
        k=int(round(float(KN(t))))
        if L and L[-1][0]==k: L[-1]=(k,L[-1][1]+1)
        else: L.append((k,1))
    return L
H2_NEW=smooth2()
OLD=[x for x in ORIG if x[0]<72]+H2_OLD+[x for x in ORIG if 108<x[0]<182 and x[0] not in SKIP|{130}]+[(182,8)]+[x for x in ORIG if x[0]>182 and x[0] not in SKIP]
NEW=[x for x in ORIG if x[0]<72]+H2_NEW+rest(108)
def expand(L): return [k for k,n in L for _ in range(n)]
from functools import lru_cache
@lru_cache(None)
def orig(k):
    a=np.asarray(Image.open(f"{D}w/{k:04d}.png").convert('RGB')).astype(np.float32); r,g,b=a[...,0],a[...,1],a[...,2]
    al=np.clip(1-(g-np.maximum(r,b)-40)/60,0,1); im=Image.fromarray(np.dstack([a,al*255]).astype(np.uint8)); return im.resize((round(960*S),round(960*S)),Image.LANCZOS)
o0=Image.open(D+'body/000.png').getbbox(); b0=orig(0).getbbox(); ox,oy=o0[0]-b0[0],o0[3]-b0[3]
F1=ImageFont.truetype(of.FONT,26); F2=ImageFont.truetype(of.FONT,22)
H1=hand('w_loop_long'); RA=of.ramp('c_ash_cloak')
cache={}
import cv2
def clean(im,k):
    """몸 덩어리와 떨어진 조각 = 그록 분홍 칼이 흐려 남은 흙색 자국 → 지움 (내려찍기 흙먼지가 나는 198장부터는 그대로)"""
    if k>=198: return im
    a=np.array(im); n_,lab,st,_=cv2.connectedComponentsWithStats((a[...,3]>0).astype(np.uint8),connectivity=8)
    if n_>2: main=1+int(np.argmax(st[1:,4])); a[(lab!=main)&(lab>0),3]=0
    return Image.fromarray(a)
def game(k):
    if k not in cache: cache[k]=comp(clean(Image.open(f'{D}body/{k:03d}.png'),k),FR[k],H1,RA)
    return cache[k]
def grok(k):
    og=Image.new('RGBA',(300,300)); im=orig(k); og.paste(im,(ox,oy),im); return og
def part(k): return '1타 내려베기' if k<72 else ('2타 가로베기' if k<=108 else ('되돌려베기' if k<168 else '내려찍기'))
def render(panels,seq,name,K=3,note=''):
    out=D+'vid/'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
    for n,ks in enumerate(seq):
        C=Image.new('RGB',(1920,1080),(58,66,52)); d=ImageDraw.Draw(C); d.rectangle([0,858,1920,1080],fill=(84,74,58))
        PW=1920//len(panels)
        for j,((fn,title),k) in enumerate(zip(panels,ks)):
            z=fn(k).resize((300*K,300*K),Image.NEAREST); C.paste(z,(PW*j+PW//2-150*K,858-J['foot']*K),z)
            d.text((PW*j+36,28),title,font=F1,fill=(255,235,150)); kk=k[0] if isinstance(k,tuple) else k; d.text((PW*j+36,1010),f'{part(kk)} · {kk}장',font=F2,fill=(235,235,235))
        if note: d.text((36,70),note(n) if callable(note) else note,font=F2,fill=(200,220,255))
        C.save(out+f'{n:04d}.jpg',quality=92)
    subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',out+'%04d.jpg','-c:v','libx264','-pix_fmt','yuv420p','-crf','20',D+name],check=True)
def pad(*L):
    m=max(len(x) for x in L); return [x+[x[-1]]*(m-len(x)) for x in L]
# 베기 판 (사장님 11-01 「2타는 아직 끊긴다 · 베는 게 아니라 칼이 움직이는 거 같다」): 도트 게임식 — 감기(살짝 멈춤) → 3장에 휙 + 코드로 그린 검기 부채꼴 → 끝 자세에서 멈춤
H2_SLASH=[(72,3),(73,2),(74,3),(75,2),(76,3),(77,3),(78,3),(79,3),(80,4), (83,1),(86,1),(90,2),(91,2), (92,3),(94,2),(97,2),(100,2),(103,2),(106,2),(108,10)]
SLASH=[x for x in ORIG if x[0]<72]+H2_SLASH+rest(108)
from PIL import ImageDraw as _ID
def trails(seq):
    """틱마다 그릴 검기: 장이 바뀔 때 칼 각도가 12° 넘게 돌면 '휙' — 휙 시작 각도부터 지금 각도까지 이은 부채꼴 하나. 휙이 멈추면 6틱 동안 옅어짐"""
    out=[]; act=None; last=None   # act=[시작각, 돈 각, 손 자리, 끝난 틱 or None]
    for n,k in enumerate(seq):
        if n and seq[n-1]!=k:
            a0,a1=FR[seq[n-1]]['ang'],FR[k]['ang']; da=(a1-a0+180)%360-180
            if abs(da)>12:
                if act and act[3] is None and np.sign(da)==np.sign(act[1]): act[1]+=da; act[2]=tuple(FR[k]['guard'])
                else: act=[a0,da,tuple(FR[k]['guard']),None]
            elif act and act[3] is None: act[3]=n
        if act and act[3] is not None and n-act[3]>=len(FADE): act=None
        out.append(None if act is None else (act[0],act[1],act[2],0 if act[3] is None else n-act[3]))
    return out
FADE=[1,.75,.5,.32,.18,.08]
def draw_trail(im,seg,L):
    if seg is None: return im
    a0,da,(gx,gy),age=seg; f=FADE[min(age,len(FADE)-1)]
    lay=Image.new('RGBA',im.size); d=_ID.Draw(lay); st=max(3,int(abs(da)/8)); angs=[a0+da*i/st for i in range(st+1)]
    for r0,r1,col,al in [(.34,.80,(160,200,255),95),(.80,1.04,(235,245,255),210)]:   # 안쪽 옅은 파랑 · 칼끝 길은 밝게
        pts=[(gx+np.cos(np.radians(t))*L*r1,gy+np.sin(np.radians(t))*L*r1) for t in angs]+[(gx+np.cos(np.radians(t))*L*r0,gy+np.sin(np.radians(t))*L*r0) for t in reversed(angs)]
        d.polygon(pts,fill=col+(int(al*f),))
    out=im.copy(); out.alpha_composite(lay); return out
# A안 (사장님 11-01 「베기 길이도 짧고 앞으로 베는 느낌이 아니네」 → 「추천대로 하자」): 몸 앞 땅 위에 크게 눕힌 반원 검흔
#  감기(원래 빠르기) → 휙 8틱(칼끝이 지나는 만큼 검흔이 왼쪽→앞→오른쪽으로 자람) → 팔로스루 동안 10틱에 걸쳐 옅어짐. 몸은 그록 2타 그대로(흐림 자국 붙은 84·85·87·88·89장은 안 씀)
H2_A=[(72,3),(73,2),(74,3),(75,2),(76,3),(77,2),(78,3),(79,2),(80,3), (81,1),(83,2),(86,2),(90,2),(91,1), (92,2),(93,2),(94,2),(96,2),(98,2),(100,2),(102,2),(104,2),(106,2),(108,8)]
GA=[x for x in ORIG if x[0]<72]+H2_A+rest(108)
GR=dict(cx=150,cy=FOOT-16,rx=122,ry=50,a0=200,a1=-20)   # 땅 위 타원(게임칸): 몸 가운데 발밑, 몸 앞 = 화면 아래(90°)
def ground_plan(seq):
    """틱마다 (자란 정도 0~1, 옅어짐 0~1): 81장에서 시작해 8틱 동안 자라고(빨리 → 천천히), 다 자란 뒤 10틱 동안 옅어짐"""
    out=[]; t0=None
    for n,k in enumerate(seq):
        if t0 is None and k==81: t0=n
        if t0 is None or n-t0>=18: out.append(None); continue
        t=n-t0; g=1-(1-min(t+1,8)/8)**2; f=1.0 if t<8 else 1-(t-8)/10
        out.append((g,f))
    return out
def draw_ground(im,st):
    if st is None: return im
    g,f=st; a0,a1=GR['a0'],GR['a0']+(GR['a1']-GR['a0'])*g; n=max(4,int(abs(a1-a0)/5))
    lay=Image.new('RGBA',im.size); d=_ID.Draw(lay)
    for i in range(n):                       # 앞쪽(칼끝 가까운 쪽)일수록 밝게
        t0,t1=a0+(a1-a0)*i/n,a0+(a1-a0)*(i+1)/n; w=(i+1)/n
        for r0,r1,col,al in [(.58,.86,(150,195,255),70+60*w),(.86,1.0,(235,245,255),120+120*w)]:
            pts=[(GR['cx']+np.cos(np.radians(t))*GR['rx']*r,GR['cy']+np.sin(np.radians(t))*GR['ry']*r) for t,r in [(t0,r1),(t1,r1),(t1,r0),(t0,r0)]]
            d.polygon(pts,fill=col+(int(al*f),))
    out=Image.new('RGBA',im.size); out.alpha_composite(lay); out.alpha_composite(im); return out   # 땅에 그림 → 몸이 위
if __name__=='__main__':
    # 영상: 2타만 (60~120장) — 원래 빠르기 / A안(땅 위 큰 검흔) · 제 빠르기 두 번, 반 빠르기 한 번
    cut=lambda L:[k for k in expand(L) if 60<=k<=120]
    a,c=pad(cut(ORIG),cut(GA)); GP=ground_plan(c)
    one=list(range(len(a))); slow=[x for x in one for _ in range(2)]
    idx=one+[one[-1]]*20+one+[one[-1]]*20+slow
    seq=[(a[i],(c[i],i)) for i in idx]
    aan=lambda kc: draw_ground(game(kc[0]),GP[kc[1]])
    lab=lambda n:'제 빠르기' if n<2*(len(one)+20) else '반 빠르기(천천히 보기)'
    render([(game,'원래 빠르기 (그록 그대로)'),(aan,'A안: 몸 앞 땅 위에 큰 검흔')],seq,'정면콤보_2타_A안_땅검흔.mp4',note=lab)
    print('ok')
