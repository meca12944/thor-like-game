# Ys VIII-like sword arc: sweeping thin tapered crescent, white core / cyan rim / blue glow, sparks
import numpy as np,math,random
from PIL import Image
CORE=np.array([255,255,255]);RIM=np.array([150,235,255]);GLOW=np.array([60,140,255])
def arc(R,span,T,head,tail,rot,sz=None,rev=0,sq=1):
    """R radius, span deg, T max thickness, head/tail in 0..1 of span (visible part), rot deg (0 = arc bulging right)."""
    S=sz or int(2*R+2*T+12);c=S/2;y,x=np.mgrid[0:S,0:S].astype(float)-c
    a=math.radians(rot);xr=x*math.cos(a)+y*math.sin(a);yr=-x*math.sin(a)+y*math.cos(a)
    yr=yr/sq;r=np.hypot(xr,yr);th=np.degrees(np.arctan2(yr,xr))          # th 0 = forward
    u=(th+span/2)/span;u=1-u if rev else u                                            # 0 at top start .. 1 at bottom end
    vis=(u>=tail)&(u<=head)
    k=np.clip((u-tail)/max(head-tail,1e-3),0,1)                    # 0 at tail .. 1 at head
    w=T*np.sin(np.pi*np.clip(u,0,1))**.8*(.25+.75*k)                # tapered, thicker toward head
    d=np.abs(r-R+w*.3)                                             # crescent: inner edge pulled in
    o=np.zeros((S,S,4))
    g=vis&(d<w/2+4);m=vis&(d<w/2);cc=vis&(d<w/4)
    o[g,:3]=GLOW;o[g,3]=90*k[g]+30
    o[m,:3]=RIM;o[m,3]=200
    o[cc,:3]=CORE;o[cc,3]=255
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
def sparks(img,cx,cy,n,age,seed,col=(200,245,255)):
    rnd=random.Random(seed);px=img.load()
    for i in range(n):
        ang=rnd.uniform(-1.2,1.2);sp=rnd.uniform(2,4.5);L=age*sp
        x=int(cx+math.cos(ang)*L);y=int(cy+math.sin(ang)*L)
        al=max(0,255-age*30)
        for dx in (0,1):
            if 0<=x+dx<img.width and 0<=y<img.height:px[x+dx,y]=(*col,al)
