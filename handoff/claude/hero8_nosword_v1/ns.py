# 칼 지우기 (C안): 밝은 회색 칼날 -> 직선 맞추기 -> 칼날 띠(테두리 포함) + 날밑 지움, 몸과 겹친 자리는 주변 색으로 메움. 손(칼자루 쥔 주먹)은 남김.
import numpy as np
from PIL import Image
from scipy import ndimage
def blade_core(a,thr=105):
    r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    m=(al>40)&(r>thr)&(abs(r-b)<40)&(abs(g-b)<40)&(abs(r-g)<30)
    lab,n=ndimage.label(m,np.ones((3,3)))
    if not n:return None
    sz=ndimage.sum(m,lab,range(1,n+1))
    best=None
    for i in np.argsort(-sz)[:4]:
        ys,xs=np.nonzero(lab==i+1)
        if len(xs)<8:continue
        P=np.c_[xs,ys].astype(float);c=P.mean(0);U,S,V=np.linalg.svd(P-c,full_matrices=False);el=S[0]/max(S[1],.5)
        if el>3 and (best is None or len(xs)>best[0]):best=(len(xs),lab==i+1,c,V[0])
    return best
def fill_median(a,holes):
    # 바깥에서 안쪽으로 한 겹씩: 이웃 8칸 중 아는 칸 색의 가운데값(테두리 검은 줄이 번지지 않게)
    a=a.copy();known=(a[...,3]>40)&~holes;todo=holes.copy();H,W=holes.shape
    while todo.any():
        ys,xs=np.nonzero(todo&ndimage.binary_dilation(known,np.ones((3,3))))
        if not len(ys):break
        new=[]
        for y,x in zip(ys,xs):
            y0,y1,x0,x1=max(0,y-1),min(H,y+2),max(0,x-1),min(W,x+2);k=known[y0:y1,x0:x1]
            c=a[y0:y1,x0:x1][k][:,:3];lum=c.sum(1);o=np.argsort(lum);new.append(c[o[len(o)//2]])
        for (y,x),c in zip(zip(ys,xs),new):a[y,x,:3]=c;a[y,x,3]=255;known[y,x]=True;todo[y,x]=False
    return a
def remove(a,w=2.6,guard=6,ext=3,ovr=2,gthr=85,back=6,axial=0,patch=()):
    a=a.copy();B=blade_core(a)
    if B is None:return a,None,0
    _,core,c,u=B;ys,xs=np.nonzero(core);P=np.c_[xs,ys]-c;t=P@u;t0,t1=t.min(),t.max()
    by,bx=np.nonzero(a[...,3]>40);body=np.array([bx.mean(),by.mean()])
    # 손 쪽 끝 = 몸 중심(알파)에 가까운 끝
    e0,e1=c+u*t0,c+u*t1
    if np.hypot(*(e1-body))<np.hypot(*(e0-body)):u=-u;t0,t1=-t1,-t0   # t0 = 손 쪽
    H,W=a.shape[:2];Y,X=np.mgrid[:H,:W];Q=np.dstack([X-c[0],Y-c[1]]);T=Q@u;D=np.abs(Q@np.array([-u[1],u[0]]))
    wc=np.abs(P@np.array([-u[1],u[0]])).max() if False else np.percentile(np.abs(P@np.array([-u[1],u[0]])),95);w=max(w,wc+2.2)
    r0,g0,b0=[a[...,k].astype(int) for k in range(3)]
    gray=(a[...,3]>40)&(r0>gthr)&(abs(r0-b0)<40)&(abs(g0-b0)<40)&(abs(r0-g0)<30)&(D<=w-1.5)
    if gray.any():tt=T[gray];t0,t1=max(t0-back,min(t0,tt.min())),max(t1,tt.max())   # 손에 가려 끊긴 칼날 조각까지
    band=(D<=w)&(T>=t0-1)&(T<=t1+ext)
    # 날밑: 손 쪽 끝 둘레 guard 안의 밝은/금색 칸 (장갑=어두운 색은 남김)
    r,g,b=[a[...,k].astype(int) for k in range(3)];lum=(r+g+b)/3
    brown=(r>g)&(g>=b-5)&(r-b>22)&(lum>40)&(lum<175)&(b<.48*r)   # 살색(b/r~.5)은 남김
    gd=((T>=t0-4.5)&(T<=t0+1.5)&(D<=7.5)&brown)|((T>=t0-14)&(T<t0-4.5)&(D<=2.6)&brown)   # 날밑(가로 막대) + 칼자루·폼멜(손 너머 갈색)
    kill=(band|gd)&(a[...,3]>0)
    hand=c+u*(t0-3);GA=((T>=t0-15)&(T<=t0+3)&(D<=9))|((D<=w+3)&(T>=t0-1)&(T<=t1+ext+2))   # 날밑·칼자루 둘레
    before=(a[...,3]>40)
    a[kill,3]=0
    # 날밑 테두리 가는 줄 지우기: 둘레 안에서 이웃(8칸)이 2칸 이하인 칸을 몇 번 깎음
    for _ in range(3):
        al=a[...,3]>40;nb=ndimage.convolve(al.astype(int),np.ones((3,3)),mode='constant')-al
        thin=al&GA&(nb<=2)
        if not thin.any():break
        a[thin,3]=0;kill|=thin
    al=a[...,3]>40;op=ndimage.binary_opening(al,np.ones((3,3)));stub=al&GA&~op;a[stub,3]=0;kill|=stub   # 손에서 삐죽 나온 3칸 미만 굵기 조각
    # 몸 속 구멍 메우기
    al=a[...,3]>40;nv=np.array([-u[1],u[0]]);ky,kx=np.nonzero(kill&~al);over=np.zeros_like(al)
    def has(px,py):
        px=np.clip(np.round(px).astype(int),0,W-1);py=np.clip(np.round(py).astype(int),0,H-1);return al[py,px]
    side=lambda sg:np.any([has(kx+sg*nv[0]*(w+dd),ky+sg*nv[1]*(w+dd)) for dd in range(1,ovr+1)],0)
    ok=side(1)&side(-1)&(T[ky,kx]>=t0-15);over[ky[ok],kx[ok]]=True   # 칼 양쪽이 다 몸 = 몸 위를 지나던 칼 -> 메움
    if axial:   # 칼이 다리(정강이)를 가리던 장: 칼 방향으로 앞뒤(axial 칸 안)에 몸이 있으면 메움 = 가려졌던 다리를 이어 그림
        uu=np.array(u);fw=lambda sg:np.any([has(kx+sg*uu[0]*dd,ky+sg*uu[1]*dd) for dd in range(1,axial+1)],0)
        ok2=fw(1)&fw(-1);over[ky[ok2],kx[ok2]]=True
    for poly in patch:   # 손으로 고른 메우기 자리 (칼에 완전히 가려 있던 몸: 다각형 안 빈칸을 이웃 색으로)
        from PIL import ImageDraw;pm=Image.new('L',(W,H));ImageDraw.Draw(pm).polygon([tuple(p) for p in poly],fill=1);over|=np.array(pm).astype(bool)&~al
    holes=(ndimage.binary_fill_holes(al)&~al&kill)|over
    if holes.any():
        a=fill_median(a,holes)
    # 떨어진 부스러기
    al=a[...,3]>40;lab,n=ndimage.label(al,np.ones((3,3)))
    if n>1:
        sz=ndimage.sum(al,lab,range(1,n+1));k=np.argmax(sz)+1;GAd=ndimage.binary_dilation(GA,iterations=3)
        for i in range(1,n+1):   # 떨어진 조각 중 칼 둘레 안에 있는 것만 지움 (칼에 가려 떨어진 장화·손끝 같은 몸은 남김)
            if i==k:continue
            m=lab==i
            if m.sum()<15 or (m&GA).sum()>=.8*m.sum() or (m.sum()<60 and (m&GAd).any()):a[m,3]=0   # 칼 띠에 잘려 떨어진 작은 망토 끝도 지움
    return a,(float(hand[0]),float(hand[1]),float(np.degrees(np.arctan2(u[1],u[0])))),int((before&~(a[...,3]>40)).sum())
