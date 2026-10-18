# combo3_arc: combo3_final(저장본 복사) 몸 그대로, 스미어/타격/팔로1 프레임 칼만 다시 그림 + 깃발형 검기(어깨 중심 3D 원 → 탑다운 투영)
import sys,os,json,glob,shutil,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import combo3_final as F, kp_pose as K
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
PP=F.PP; VID=F.VID; V3=F.V3; PV=V3+'/preview'; CW,CH=F.CW,F.CH
SAVED=V3+'/_saved_combo3_final_20261018_1634'; J0=json.load(open(SAVED+'/combo3_final.json'))['combos']
# 경로 정의: (rx, ry, 회전°, 시작°, 끝°, 중심 y 오프셋(키 비율)), 화면 각도(y 아래, -90=위)
PATH={'right':{1:(.55,1.0,0,-115,75,0),2:(1.0,.32,0,200,-20,.12),3:(1.0,.6,-35,-80,10,.05)},
      'down': {1:(.10,1.0,0,-90,90,0),2:(1.1,.38,0,180,0,.10),3:(1.0,.55,30,165,75,.05)},
      'up':   {1:(.10,1.0,0,-90,90,0),2:(1.1,.38,0,180,360,.05),3:(1.0,.6,-30,-160,-70,0)}}
HEADF={'s':.55,'h':1.0,'f':1.1}  # 팔로1 = 약간 지나침(오버슈트)
PAL=dict(white=(236,255,255),lite=(150,236,255),cyan=(60,196,238),dark=(30,118,168),deep=(18,72,112))
def body_mask(o):
    st=ndi.binary_dilation(PP.steel(o)&(o[...,3]>0),iterations=2); m=(o[...,3]>0)&~st
    lab,n=ndi.label(m,np.ones((3,3))); sz=ndi.sum(m,lab,range(1,n+1)); return lab==np.argmax(sz)+1
def shoulder(o):
    m=body_mask(o); ys=np.where(m.any(1))[0]; c,s=ys[0],ys[-1]; H=s-c; y=int(c+.30*H); xs=np.where(m[y])[0]
    return np.array([(xs[0]+xs[-1])/2,y],float),H
def P(d,hit,S,R,H,f):
    rx,ry,rot,a0,a1,oy=PATH[d][hit]; th=np.radians(a0+(a1-a0)*f); r=np.radians(rot)
    x,y=rx*R*np.cos(th),ry*R*np.sin(th); return S+[x*np.cos(r)-y*np.sin(r),x*np.sin(r)+y*np.cos(r)+oy*H]
def flag(d,hit,S,R,H,f0,f1,head,Wmax,age):
    """세련된 반투명 검기: 안쪽 가장자리(칼끝 경로)에 가는 흰-청록 심, 바깥으로 넓고 부드러운 반투명 청록 몸통, 바깥 테두리 가는 밝은 선.
    알파: 머리(칼끝) 0.85 -> 꼬리 0.15. 사라짐 = 알파만 낮춤(조각내지 않음)."""
    sh=head-P(d,hit,S,R,H,f1); acc=np.zeros((CH,CW,4),float)
    fade=[1,.35/.55,.18/.55,.06/.55][age]; N=220
    from PIL import ImageDraw as _D
    layers=[]
    for (b0,b1,col,am) in [(0,.0,(236,255,255),1.0),(.0,.85,(70,200,245),.55),(.85,1.,(180,245,255),.75)]:
        im=Image.new('L',(CW,CH)); dr=_D.Draw(im); a=np.zeros((CH,CW))
        for i in range(N+1):
            t=i/N; p=P(d,hit,S,R,H,f0+(f1-f0)*t)+sh; n=p-(S+sh); n/=np.linalg.norm(n)+1e-6
            w=1.+(Wmax-1.)*t**1.2; al=(.05+.50*t)*am*fade
            if b1==0: dr.point(tuple(np.round(p)),fill=int(min(1,al*1.6)*255)); continue  # 1px 흰 심
            dr.line([tuple(p+n*w*b0),tuple(p+n*w*b1+n*.6)],fill=int(al*255),width=1 if b0>=.85 else 2)
        layers.append((np.array(im)/255.,col))
    out=np.zeros((CH,CW,4),float)
    for a,col in layers:  # 'over' 합성
        for c in range(3): out[...,c]=out[...,c]*(1-a)+col[c]*a*1.0
        out[...,3]=out[...,3]+a*(1-out[...,3])
    rgb=np.where(out[...,3:]>0,out[...,:3]/np.maximum(out[...,3:],1e-6),0)
    L=np.dstack([np.clip(rgb,0,255),np.clip(out[...,3]*255,0,255)]).astype(np.uint8); L[L[...,3]<6]=0
    return L
def run(d0):
    src='right' if d0=='left' else d0; F.B.OUTL=F.outl(src); info=J0[src]['frames']; srcdir=f'{VID}/px_combo3final_{src}'
    work=f'{V3}/_work_arc_src_{src}'; shutil.copytree(srcdir,work,dirs_exist_ok=True)  # 저장본 기준 복사본에서 작업
    fr=[np.array(Image.open(f'{work}/{k:03d}.png').convert('RGBA')) for k in range(len(info))]
    out=[o.copy() for o in fr]; fx=[np.zeros((CH,CW,4),np.uint8) for _ in fr]; rep=[]
    R2=None
    for hit in (1,2,3):
        ks=[k for k,f in enumerate(info) if f['hit']==hit]; s,h=[k for k in ks if info[k]['phase']=='smear'][0],[k for k in ks if info[k]['phase']=='hitstop'][0]
        fol=[k for k in ks if info[k]['phase']=='follow']; S,H=shoulder(fr[h]); b=F.O.blade(fr[h]); L=int(round(b[4])) if b is not None else 63
        R=L+0.28*H
        if hit==3: R=1.3*R2  # 피니시: 2타 대비 1.3배
        if hit==2: R2=R
        Wmax={1:(8. if src in ('down','up') else 11.),2:13.,3:16.}[hit]; tipF=None
        for k,ph,age,f0 in [(s,'s',0,0.),(h,'h',0,0.),(fol[0],'f',1,.4)]:
            bb=F.O.blade(fr[k]); grip=bb[1] if bb is not None else S
            tgt=P(src,hit,S,R,H,HEADF[ph]); u=tgt-S; a=np.degrees(np.arctan2(u[1],u[0]))  # 어깨→경로점 반지름 방향
            o,g,tip=F.repose_blade(fr[k],grip,a,L); out[k]=o
            fx[k]=flag(src,hit,S,R,H,f0,HEADF[ph],tip,Wmax,age); tipF=tip
            fx[k][body_mask(o)]=0  # 몸·얼굴 위는 덮지 않음(뒤 1타는 몸 뒤로 가림)
            rep.append(dict(frame=k,hit=hit,phase=info[k]['phase'],tip=[round(float(v),1) for v in tip],blade_angle=round(float(a),1)))
        for k,age in zip(fol[1:3],(2,3)):
            bb=F.O.blade(out[k]); tk=np.array(bb[2],float) if bb is not None else tipF  # 원래 프레임의 실제 칼끝에 고정
            fx[k]=flag(src,hit,S,R,H,.55,HEADF['f'],tk,Wmax,age)
            rep.append(dict(frame=k,hit=hit,phase='follow_fade',tip=[round(float(v),1) for v in tk],blade_angle=None))
            fx[k][body_mask(out[k])]=0
    # 검사: 칼 영역 밖 몸 diff, 검기 머리-칼끝 거리
    md=0; mt=0
    for k in range(len(fr)):
        bl=ndi.binary_dilation((PP.steel(fr[k])|PP.steel(out[k]))&((fr[k][...,3]>0)|(out[k][...,3]>0)),iterations=5)
        hc=np.array([K.HILT_H,K.HILT_G,K.HILT_D]); hilt=np.zeros_like(bl)
        for c in hc: hilt|=(out[k][...,:3]==c).all(-1)
        bl|=ndi.binary_dilation(hilt,iterations=1)  # 칼 영역 = 칼날+손잡이(재작화)
        for r in rep:
            if r['frame']==k: pass
        diff=(fr[k]!=out[k]).any(-1)&~bl; md=max(md,int(diff.sum()))
    for r in rep:
        k=r['frame']; m=fx[k][...,3]>0
        if src=='up' and r['hit']==1: m=m|ndi.binary_dilation(m,iterations=0) 
        yy,xx=np.where(m); dist=float(np.min(np.hypot(xx-r['tip'][0],yy-r['tip'][1]))) if len(xx) else 99; r['head_dist']=round(dist,2); mt=max(mt,dist)
    for k in range(len(fx)): fx[k][ndi.binary_dilation(PP.steel(out[k])&(out[k][...,3]>0))]=0  # 칼날 위는 비움
    if d0=='left': out=[o[:,::-1].copy() for o in out]; fx=[f[:,::-1].copy() for f in fx]; fr=[o[:,::-1].copy() for o in fr]
    od=f'{VID}/px_combo3thinraw_{d0}'; os.makedirs(od,exist_ok=True)
    for p in glob.glob(od+'/*.png'): os.remove(p)
    for k,(o,f2) in enumerate(zip(out,fx)): Image.fromarray(o).save(f'{od}/{k:03d}.png'); Image.fromarray(f2).save(f'{od}/fx_{k:03d}.png')
    return out,fx,rep,md,mt
def comp(o,f2):
    im=Image.new('RGBA',(CW,CH),(150,170,140,255)); im.alpha_composite(Image.fromarray(o)); im.alpha_composite(Image.fromarray(f2)); return im.convert('RGB')
if __name__=='__main__':
    for d in ['right','left','down','up']: out,fx,rep,md,mt=run(d); print(d,'body_diff',md,'head_dist',round(mt,2))
