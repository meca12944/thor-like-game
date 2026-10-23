# stylish sword-arc variants. A: blue-white flash (gradient head->tail, double arc, speed lines, star)  B: pixel-art cel crescent (navy outline, 3 tone bands, dithered tail)
# C: triple fan (3 thin staggered arcs + afterimage)
import numpy as np,math,random
from PIL import Image,ImageDraw
BAY=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])/16
def field(R,span,T,head,tail,rot,rev,sq,S):
    c=S/2;y,x=np.mgrid[0:S,0:S].astype(float)-c;a=math.radians(rot);xr=x*math.cos(a)+y*math.sin(a);yr=(-x*math.sin(a)+y*math.cos(a))/sq
    r=np.hypot(xr,yr);th=np.degrees(np.arctan2(yr,xr));u=(th+span/2)/span;u=1-u if rev else u
    vis=(u>=tail)&(u<=head)&(u>=0)&(u<=1);k=np.clip((u-tail)/max(head-tail,1e-3),0,1)
    w=T*np.sin(np.pi*np.clip(u,0,1))**.6*(.15+.85*k**1.3);d=r-R+w*.35     # signed: <0 inner, >0 outer
    return vis,k,w,d,y.astype(int)+int(c),x.astype(int)+int(c)
def put(o,m,col,al):o[m,:3]=col;o[m,3]=np.maximum(o[m,3],al if np.isscalar(al) else al[m])
def arcA(R,span,T,head,tail,rot,rev=0,sq=1):
    S=int(2*R+2*T+30);o=np.zeros((S,S,4));vis,k,w,d,Y,X=field(R,span,T,head,tail,rot,rev,sq,S);ad=np.abs(d)
    glow=vis&(ad<w/2+6);put(o,glow,(40,110,255),(40+80*k))
    body=vis&(ad<w/2);col=np.stack([90+165*k**2,190+65*k,255*np.ones_like(k)],-1)
    o[body,:3]=col[body];o[body,3]=230
    core=vis&(ad<w/5)&(k>.25);put(o,core,(255,255,255),255)
    edge=vis&(d>w/2-1.5)&(d<w/2)&(k>.4);put(o,edge,(255,255,255),255)                    # crisp bright outer edge
    v2,k2,w2,d2,_,_=field(R*.78,span*.85,T*.45,head*.95,tail+.1,rot,rev,sq,S);b2=v2&(np.abs(d2)<w2/2);put(o,b2&~body,(150,225,255),180*k2)  # inner echo arc
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
def arcB(R,span,T,head,tail,rot,rev=0,sq=1):
    S=int(2*R+2*T+30);o=np.zeros((S,S,4));vis,k,w,d,Y,X=field(R,span,T*1.25,head,tail,rot,rev,sq,S);ad=np.abs(d)
    dith=k>BAY[Y%4,X%4]*.9                                                                # tail breaks up into dither
    out=vis&(ad<w/2+1.5)&dith;put(o,out,(20,30,80),255)
    b=vis&(ad<w/2)&dith;put(o,b,(60,120,230),255)
    m=vis&(d>-w*.15)&(d<w/2-1)&dith;put(o,m,(140,220,255),255)
    h=vis&(d>w*.15)&(d<w/2-1.5)&(k>.35);put(o,h,(255,255,255),255)
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
def arcC(R,span,T,head,tail,rot,rev=0,sq=1):
    S=int(2*R*1.25+2*T+30);acc=Image.new('RGBA',(S,S))
    for j,(rr,dt,tt) in enumerate(((1.0,0,1),(1.18,.12,.55),(.84,.22,.45))):
        h=max(0,head-dt);im=arcA(R*rr,span*(1-.1*j),T*tt,h,min(h,tail),rot+j*6,rev,sq)
        acc.alpha_composite(im,((S-im.width)//2,(S-im.height)//2))
    return acc
def star(img,x,y,a,big):
    if a>3:return
    d=ImageDraw.Draw(img);L=(10 if big else 7)*(1-a/4)+3;al=int(255*(1-a/4))
    d.line([x-L,y,x+L,y],fill=(255,255,255,al),width=2);d.line([x,y-L*.6,x,y+L*.6],fill=(255,255,255,al),width=1)
    d.ellipse([x-3,y-3,x+3,y+3],fill=(220,245,255,al))
def lines(img,x,y,a,n,seed,dirx=1):
    rnd=random.Random(seed);d=ImageDraw.Draw(img);al=max(0,int(220*(1-a/8)))
    for i in range(n):
        yy=y+rnd.uniform(-30,30);L=rnd.uniform(14,34);xx=x-rnd.uniform(0,30)+a*5
        d.line([xx,yy,xx+L*dirx,yy],fill=(200,240,255,al),width=1)
def sparks(img,x,y,n,a,seed):
    rnd=random.Random(seed);px=img.load();al=max(0,255-a*28)
    for i in range(n):
        g=rnd.uniform(-1.3,1.3);L=a*rnd.uniform(2,5);xx=int(x+math.cos(g)*L);yy=int(y+math.sin(g)*L)
        for dx,dy in ((0,0),(1,0),(0,1)):
            if 0<=xx+dx<img.width and 0<=yy+dy<img.height:px[xx+dx,yy+dy]=(220,250,255,al)
