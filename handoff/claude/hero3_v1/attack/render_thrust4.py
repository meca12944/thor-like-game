# 이어 붙인 공격 가안 영상: 왼쪽 그록(분홍 칼) / 가운데 게임 장검·잿빛 망토(시작 옷) / 오른쪽 이단 대검·아라크네 망토
import numpy as np, json, os, shutil, subprocess, importlib.util, sys
from PIL import Image, ImageDraw, ImageFont
D=sys.argv[1].rstrip('/')+'/'
WH='/home/user/thor-like-game/handoff/claude/hero3_v1/weapons_hand/'
OF='/home/user/thor-like-game/handoff/claude/hero3_v1/outfit/outfit2.py'
spec=importlib.util.spec_from_file_location('o2',OF); o2=importlib.util.module_from_spec(spec); spec.loader.exec_module(o2); of=o2.of
J=json.load(open(D+'grip3.json')); FR=J['frames']; S540=54/130
idx={(f['src'],f['k']):i for i,f in enumerate(FR)}
def rng(src,a,b,step=1): return [idx[(src,k)] for k in range(a,b+1,step) if (src,k) in idx]
import numpy as _np
def _tip(i):
    f=FR[i]; a=_np.radians(f['ang']); return _np.array(f['guard'])+_np.array([_np.cos(a),_np.sin(a)])*60
def _pick(ids,n):   # 칼끝이 지나간 길이를 부드러운 가속·감속(smoothstep)으로 나눠 장 고르기
    t=_np.array([_tip(i) for i in ids]); s=_np.concatenate([[0],_np.cumsum(_np.linalg.norm(_np.diff(t,axis=0),axis=1))]); u=_np.linspace(0,1,n); e=u*u*(3-2*u)
    return [ids[int(_np.argmin(_np.abs(s-v*s[-1])))] for v in e]
SEQ=rng('f',57,82)+[idx[('f',k)] for k in (86,91)]+rng('f',95,98)+rng('fj',1,3)+rng('fb',23,41)+rng('fb',42,48,2)   # 찌르기 → 짧은 버팀 → 빼기 시작(v3 95~98) → 이음 중간 3장 → 빼기 23~41 그대로(손 빠르기 이어짐) → 버팀
def hand(n):
    im=Image.open(WH+n+'_hand.png').convert('RGBA'); a=np.array(im); w=(a[...,3]>100).sum(1)
    gy=int(np.argmax(w)); xs=np.nonzero(a[gy,:,3]>100)[0]; return im,(xs.min()+xs.max())/2,gy
def sword(hd,gx,gy,ang,size=300):
    im,hx,hy=hd; R=max(im.size)*2+4; c=Image.new('RGBA',(R,R)); c.paste(im,(int(R/2-hx),int(R/2-hy)),im)
    c=c.rotate(-(ang+90),resample=Image.NEAREST); L=Image.new('RGBA',(size,size)); L.paste(c,(int(round(gx-R/2)),int(round(gy-R/2))),c); return L
def comp(body,fr,hd,R=None):
    b=np.array(body)
    if R is not None: b=o2.recolor2(b,R)
    B=Image.fromarray(b); sw=sword(hd,fr['guard'][0],fr['guard'][1],fr['ang']); out=Image.new('RGBA',B.size)
    if fr['behind']: out.alpha_composite(sw); out.alpha_composite(B)
    else:
        out.alpha_composite(B); out.alpha_composite(sw)
        a=np.array(B); r,g,bb=[a[...,i].astype(int) for i in range(3)]; skin=(a[...,3]>100)&(r>110)&(r>bb+30)&(g>70)
        yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]; m=skin&((xx-fr['guard'][0])**2+(yy-fr['guard'][1])**2<81); o=np.array(out); o[m]=a[m]; out=Image.fromarray(o)
    return out
def orig(fr):
    res=960; S=S540*540/res
    a=np.asarray(Image.open(f"{D}{fr['src']}/{fr['k']:04d}.png").convert('RGB')).astype(np.float32); r,g,b=a[...,0],a[...,1],a[...,2]
    al=np.clip(1-(g-np.maximum(r,b)-40)/60,0,1); im=Image.fromarray(np.dstack([a,al*255]).astype(np.uint8)); return im.resize((round(res*S),round(res*S)),Image.LANCZOS)
F1=ImageFont.truetype(of.FONT,26); F2=ImageFont.truetype(of.FONT,20)
H1,H2=hand('w_loop_long'),hand('w_heretic_great'); RA,RB=o2.bands(1),o2.bands(2)
o0=Image.open(D+'body3/000.png').getbbox(); b0=orig(FR[0]).getbbox()   # 그록 그림을 몸 그림과 같은 발 자리에
ox,oy=o0[0]-b0[0],o0[3]-b0[3]
out=D+'vid4/'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
K=3; seq=[]
for j,i in enumerate(SEQ): seq+=[i]*(3 if j%2==0 else 2)   # 24장/초 → 60장/초
seq=seq+[seq[-1]]*30+seq
for n,i in enumerate(seq):
    fr=FR[i]; body=Image.open(f'{D}body3/{i:03d}.png')
    C=Image.new('RGB',(1920,1080),(58,66,52)); d=ImageDraw.Draw(C); d.rectangle([0,858,1920,1080],fill=(84,74,58))
    og=Image.new('RGBA',(300,300)); im=orig(fr); og.paste(im,(ox,oy),im)
    for j,(im,name) in enumerate([(og,'그록 찌르기+빼기 (분홍 임시 칼)'),(comp(body,fr,H1,RA),'게임: 장검 · 01 잿빛 망토(시작 옷)'),(comp(body,fr,H2,RB),'게임: 이단 대검 · 02 아라크네 망토')]):
        z=im.resize((900,900),Image.NEAREST); C.paste(z,(640*j+320-450,858-J['foot']*K),z); d.text((640*j+36,28),name,font=F1,fill=(255,235,150))
    d.text((36,1010),f"{('칼 들고 달리기' if fr['k']<76 else '찌르기') if fr['src']=='f' else '이음 중간(그린 장)' if fr['src']=='fj' else '빼기(이어 찍기)'} {fr['k']}장 · 칼 {'몸 뒤' if fr['behind'] else '몸 앞'}",font=F2,fill=(235,235,235))
    C.save(out+f'{n:04d}.jpg',quality=92)
subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',out+'%04d.jpg','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',D+'달리다찌르기_빼기_이음.mp4'],check=True)
print('ok',len(seq),'장(60/초)')
