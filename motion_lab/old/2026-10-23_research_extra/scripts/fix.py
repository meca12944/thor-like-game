import json,numpy as np
from measure import load,stats,R
from slip import stance
G=189
def warp(a,dy=0.0,dx=0.0,hip=None):
    """move the body above the hips by (dx,dy); legs bend/lean smoothly so the feet stay planted"""
    if not dy and not dx:return a
    m=a[...,3]>40;ys=np.nonzero(m.any(1))[0];top,bot=ys.min(),ys.max()
    hip=hip or int(top+(bot-top)*.55);out=np.zeros_like(a)
    for y in range(256):
        f=1.0 if y<=hip else max(0.0,(bot-y)/max(1,bot-hip))
        sy=int(round(y-dy*f));sx=int(round(dx*f))
        if 0<=sy<256:out[y]=np.roll(a[sy],sx,0)
    return out
def retime(d,total,mn=2):
    if sum(1 for x in d if x)<len(d)/2:return None   # not enough planted-foot readings: keep the old beat
    d=np.array([x if x else np.nan for x in d],float);d[np.isnan(d)]=np.nanmean(d)
    w=d/d.sum()*total;t=np.floor(w).astype(int)
    for j in np.argsort(-(w-t))[:total-t.sum()]:t[j]+=1
    while t.min()<mn:i=t.argmin();j=t.argmax();t[i]+=1;t[j]-=1
    return [int(x) for x in t]
def spread(fr):
    s=stats(fr);o=[]
    for a,(top,bot,bx,h) in zip(fr,s):
        rows=a[int(bot-h*.18):int(bot)+1,:,3]>40;xs=np.nonzero(rows.any(0))[0];o.append(np.ptp(xs))
    o=np.array(o,float);return (o-o.min())/max(1,np.ptp(o))
def slipscore(d,ticks):
    v=sum(x for x in d if x)/sum(t for x,t in zip(d,ticks) if x)
    return sum(abs(x-v*t) for x,t in zip(d,ticks) if x)
from scipy import ndimage
def feet(a,h=16):
    """connected blobs touching the lowest h rows (feet/boots)"""
    m=a[...,3]>40;ys=np.nonzero(m.any(1))[0];bot=ys.max();sub=m.copy();sub[:bot-h]=False
    lab,n=ndimage.label(sub);return [(lab==i) for i in range(1,n+1) if (lab==i).sum()>25],bot
def track(fr,ky=0.0,h=16):
    """backward travel (x px) of the planted foot between frames; ky = screen y the ground moves per x (diag 0.8)"""
    n=len(fr);out=[]
    for i in range(n):
        A,_=feet(fr[i],h);a=fr[i].astype(int);b=fr[(i+1)%n].astype(int);best=(0.55,None)
        for blob in A:
            ys,xs=np.nonzero(blob)
            if ys.max()<G-4:continue
            col=a[ys,xs,:3]
            for sx in range(-6,36):
                for e in (-2,-1,0,1,2):
                    sy=int(round(-ky*sx))+e;yy,xx=ys+sy,xs-sx
                    ok=(yy>=0)&(yy<256)&(xx>=0)&(xx<256)
                    t=b[yy[ok],xx[ok]];hit=(t[:,3]>40)&(np.abs(t[:,:3]-col[ok]).sum(1)<60)
                    sc=hit.sum()/len(ys)-0.01*abs(e)
                    if sc>best[0]:best=(sc,sx)
        out.append(best[1])
    d=np.array([x if x is not None else np.nan for x in out],float);med=np.nanmedian(d)
    return [None if np.isnan(x) or x>2.2*med or x<0 else int(x) for x in d]
def track(fr,ky=0,h=16):
    d=np.array([x[1] if x[1] is not None else np.nan for x in stance(fr)],float);med=np.nanmedian(d)
    return [None if np.isnan(x) or x>2*med or x<0.3*med else int(x) for x in d]
def footdiff(fr):
    s=stats(fr);o=[]
    for a,(top,bot,bx,h) in zip(fr,s):
        m=a[...,3]>40;cx=int(bx);y0=int(bot-h*.12)
        L=np.nonzero(m[y0:,:cx].any(1))[0];Rr=np.nonzero(m[y0:,cx:].any(1))[0]
        o.append(((L.max() if len(L) else 0)-(Rr.max() if len(Rr) else 0)))
    return np.array(o,float)
def front_walk(fr,toward_cam=True,A=2.0,B=2.6):
    f=footdiff(fr);n=len(fr);c=int(np.argmax(np.abs(f)))
    Lfwd=(f[c]>0)==toward_cam                       # which foot is stepping forward at the big contact
    sgn=-1 if Lfwd else 1                            # body leans over that foot (screen side)
    dx=[round(sgn*A*np.sin(2*np.pi*(i-c)/n)) for i in range(n)]
    dy=[round(B/2*np.cos(4*np.pi*(i-c-0.5)/n)+0.01) for i in range(n)]   # down just after each foot lands, up while passing
    return [warp(a,dy=y,dx=x) for a,x,y in zip(fr,dx,dy)],dx,dy
def breathe(a,dy):
    """chest/shoulders/head rise by dy (negative = up); waist and legs stay"""
    if not dy:return a
    m=a[...,3]>40;ys=np.nonzero(m.any(1))[0];top,bot=ys.min(),ys.max();h=bot-top
    c0,c1=int(top+h*.32),int(top+h*.5);out=np.zeros_like(a)
    for y in range(256):
        f=1.0 if y<=c0 else max(0.0,(c1-y)/(c1-c0))
        sy=int(round(y-dy*f))
        if 0<=sy<256:out[y]=a[sy]
    return out
def torso_y(fr):
    """vertical position of the chest/shoulders per frame, by matching the torso band of frame 0 (hair-proof)"""
    s=stats(fr);top,bot=s[0,0],s[0,1];h=bot-top
    y0,y1=int(top+h*.28),int(top+h*.5);ref=fr[0][y0:y1].astype(int);rm=ref[...,3]>40;out=[]
    for a in fr:
        best=(1e9,0)
        for dy in range(-14,15):
            for dx in range(-14,15,1):
                seg=np.roll(a,(-dy,-dx),(0,1))[y0:y1].astype(int);m=rm|(seg[...,3]>40)
                e=(np.abs(seg[...,:3]-ref[...,:3]).sum(2)*m).sum()/max(1,m.sum())+((seg[...,3]>40)!=rm).mean()*400
                if e<best[0]:best=(e,dy)
        out.append(best[1])
    return np.array(out)
def chest_y(fr,ch):
    """top row of a colour landmark on the chest: Linette red top, hero gold pauldron (hair/cape proof)"""
    o=[]
    for a in fr:
        r,g,b,al=[a[...,i].astype(int) for i in range(4)]
        if ch=='linette':m=(r>150)&(g<80)&(b<80)&(al>200)
        else:m=(r>140)&(g>100)&(b<90)&(r-b>70)&(al>200)
        m[150:]=False;rows=np.nonzero(m.sum(1)>=3)[0]
        o.append(int(rows.min()) if len(rows) else -1)
    return np.array(o)
def head_y(fr,ch=None):
    """head-top height measured in a narrow column over the neck (flying ponytail/cape ignored)"""
    o=[]
    for a in fr:
        m=a[...,3]>40;ys=np.nonzero(m.any(1))[0];top=ys.min()
        # neck x = centre of the figure rows 18..30 px under the top (head/neck)
        band=m[top+18:top+30];xs=np.nonzero(band.any(0))[0];cx=int(np.median(np.nonzero(band)[1]))
        col=m[:,cx-4:cx+5].any(1);o.append(int(np.nonzero(col)[0].min()))
    return np.array(o)
def track2(fr,ky=0.0,h=12):
    """planted-foot backward travel by colour template matching of the lowest boot pixels"""
    n=len(fr);out=[]
    for i in range(n):
        a=fr[i].astype(int);b=fr[(i+1)%n].astype(int)
        m=a[...,3]>40;bot=np.nonzero(m.any(1))[0].max();best=(1e9,None)
        if bot<G-3:out.append(None);continue
        reg=np.zeros_like(m);reg[bot-h:bot+1]=m[bot-h:bot+1]
        lab,nb=ndimage.label(reg)
        for j in range(1,nb+1):
            ys,xs=np.nonzero(lab==j)
            if len(ys)<30 or ys.max()<bot-2:continue
            col=a[ys,xs]
            for sx in range(-4,34):
                for e in (-1,0,1):
                    sy=int(round(-ky*sx))+e;yy,xx=ys+sy,xs-sx
                    ok=(yy>=0)&(yy<256)&(xx>=0)&(xx<256)
                    if ok.mean()<.95:continue
                    t=b[yy[ok],xx[ok]];err=np.abs(t[:,:3]-col[ok][:,:3]).sum(1);err[t[:,3]<40]=300
                    sc=err.mean()+3*abs(e)
                    if sc<best[0]:best=(sc,sx)
        out.append(best[1] if best[0]<120 else None)
    d=np.array([x if x is not None else np.nan for x in out],float);med=np.nanmedian(d)
    return [None if np.isnan(x) or x>2*med or x<0.25*med else int(x) for x in d]
def footlock(fr,d,ticks,lim=3):
    """leftover slip after retiming: nudge each frame sideways so the planted foot stays put (body speeds up/slows a hair, as in real running)"""
    sp=sum(x for x in d if x)/sum(t for x,t in zip(d,ticks) if x)
    e=[(x-sp*t) if x else 0 for x,t in zip(d,ticks)];o=-np.cumsum([0]+e[:-1]);o+=np.arange(len(o))*sum(e)/len(o);o-=o.mean()
    o=np.clip(np.round(o),-lim,lim).astype(int)
    nd=[(x+int(o[(i+1)%len(o)]-o[i])) if x else None for i,x in enumerate(d)]
    return [np.roll(a,int(-v),1) for a,v in zip(fr,o)],list(o),nd
def feet_bot(a):
    """lowest body pixel, ignoring the steel blade (grey/white, low colour)"""
    r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    blade=(mx-mn<34)&(mx>70)
    m=(al>40)&~ndimage.binary_dilation(blade,iterations=2)
    lab,n=ndimage.label(m);sz=ndimage.sum(m,lab,range(1,n+1));big=np.isin(lab,1+np.nonzero(sz>=25)[0])
    return int(np.nonzero(big.any(1))[0].max())
def boot_bot(a):
    """주인공 장화(갈색) 맨 아래 — 칼집·칼끝·망토에 속지 않게"""
    r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    m=(al>40)&(r>=40)&(r>=b+15)&(r>=g+10);m[:150]=False
    m=ndimage.binary_opening(m);ys=np.nonzero(m.sum(1)>=2)[0]
    return int(ys.max()) if len(ys) else feet_bot(a)
def boot_bot(a):
    """주인공 발바닥: 갈색 장화에서 아래로 이어진 밑창까지 (칼집·칼끝·망토 무시)"""
    r,g,b,al=[a[...,c].astype(int) for c in range(4)];A=al>40
    m=A&(r>=40)&(r>=b+15)&(r>=g+10);m[:150]=False;m=ndimage.binary_opening(m)
    best=-1
    for x in np.nonzero(m.any(0))[0]:
        y=np.nonzero(m[:,x])[0].max()
        while y+1<256 and A[y+1,x] and y-np.nonzero(m[:,x])[0].max()<6:y+=1
        best=max(best,y)
    return int(best) if best>0 else feet_bot(a)
