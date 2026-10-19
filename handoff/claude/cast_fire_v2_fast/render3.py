import json,math,random,numpy as np
from PIL import Image,ImageDraw,ImageFont
R='/home/user/thor-like-game/test128/assets/'
d=json.load(open(R+'anim/hero8.json'))
sh=[Image.open(R+s).convert('RGBA') for s in d['sheets']]
def cell(s,c):
    x,y,w,h,ax,ay=d['cells'][s][c]; return sh[s].crop((x,y,x+w,y+h)),ax,ay
S=2; CW,CH=210,200; RX,RY=105,165
dirs=['down','up','right','left']; dk={'down':'아래','up':'위','right':'오른쪽','left':'왼쪽'}
sk=[('s1','S1 청록'),('s2','S2 빨강'),('s3','S3 금색')]
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',32)
# flame palettes (hot core -> skill color -> dark smoke), per skill
PAL={'s1':[(255,255,255),(200,255,255),(90,230,255),(30,150,230),(20,70,140)],
     's2':[(255,255,235),(255,230,120),(255,140,50),(230,50,30),(120,20,20)],
     's3':[(255,255,240),(255,245,160),(255,205,70),(230,140,30),(130,70,20)]}
# timeline (ticks @60fps). entries index into original cast anim: 0,1 windup, 2 hold(channel), 6,7,8 release, 9,10 recover
T_W=6; LAP0=3; LAP=40           # faster: one lap in 40 ticks
HOLD_END=LAP0+LAP+6
TPF=5
PLAN=[(0,T_W),(1,T_W),(2,HOLD_END-2*T_W),(6,TPF),(7,TPF),(8,TPF),(9,TPF),(10,TPF+3)]
TOTAL=sum(n for _,n in PLAN)
def entry_at(t):
    for i,n in PLAN:
        if t<n: return i,t
        t-=n
    return PLAN[-1][0],0
A0=math.pi/2   # start at the front (bottom) of the ellipse, sweep clockwise on screen
def masked(img,ax,ay,cx,cy,rx,ry,sweep):
    a=np.asarray(img).copy(); h,w=a.shape[:2]
    yy,xx=np.mgrid[0:h,0:w]; ang=np.arctan2((yy-ay-cy)/ry,(xx-ax-cx)/rx)
    rel=np.mod(ang-A0,2*math.pi); a[...,3]=np.where(rel<=sweep,a[...,3],0)
    return Image.fromarray(a)
def tongue(px,py,hgt,wid,pal,alpha,rng,front,out):
    """one pixel-art flame tongue standing on (px,py): wide hot base -> thin dark tip, swaying"""
    sway=rng.uniform(-1,1)
    H=max(2,int(hgt))
    for r in range(H):
        u=r/H
        w=max(1,round(wid*(1-u)**0.8+0.3))
        x=px+sway*u*u*3-w/2
        ci=min(4,int(u*4.2+rng.uniform(-.3,.5)))
        if r==0: ci=min(ci,1)
        a=int(alpha*(1-u*u*0.7))
        out.append((x,py-r,w,1,pal[max(0,ci)]+(a,),front))
def flame(t,s,cx,cy,rx,ry,rng):
    pal=PAL[s]; out=[]
    lt=t-LAP0
    if lt<0: return out
    sweep=min(2*math.pi,2*math.pi*lt/LAP)
    post=lt-LAP
    pt=lambda a:(cx+rx*math.cos(a),cy+ry*math.sin(a),math.sin(a)>-0.05)
    if post<0:
        # running fire: big head tongue + shrinking trail behind it on the lit arc
        span=min(sweep,1.5)
        n=int(span/0.06)+1
        for k in range(n):
            u=k/max(1,n-1) if n>1 else 0
            a=A0+sweep-k*0.06
            x,y,fr=pt(a)
            h=(23 if k<2 else 17)*(1-u)**1.4+2+rng.uniform(-1.5,1.5)
            w=(8 if k<2 else 6)*(1-u*0.6)
            tongue(x,y,h,w,pal,int(255*(1-u*0.5)),rng,fr,out)
        # sparks rising from the head
        for _ in range(4):
            a=A0+sweep-rng.uniform(0,.25); age=rng.random(); x,y,fr=pt(a)
            out.append((x+rng.uniform(-3,3),y-14-age*16,1,1,pal[min(4,1+int(age*3))]+(int(240*(1-age)),),fr))
        # low embers on the already-lit arc
        for k in range(int(sweep/(2*math.pi)*30)):
            if rng.random()<0.5: continue
            a=A0+rng.uniform(0,max(0,sweep-1.5)); x,y,fr=pt(a)
            tongue(x,y,rng.uniform(1,4),2,pal,170,rng,fr,out)
    else:
        # ring closed: whole circle burns up (short), then dies down by the release end
        f=max(0.0,1-post/34); boost=max(0.0,1-post/10)
        for k in range(40):
            a=A0+k*2*math.pi/40+rng.uniform(-.04,.04); x,y,fr=pt(a)
            h=(3+9*boost+rng.uniform(0,4))*f
            if h<1.2: continue
            tongue(x,y,h,3+2*boost,pal,int(255*min(1,f*1.3)),rng,fr,out)
        for _ in range(int(10*f)):
            a=rng.uniform(0,2*math.pi); age=rng.random(); x,y,fr=pt(a)
            out.append((x,y-6-age*18,1,1,pal[min(4,1+int(age*3))]+(int(220*(1-age)*f),),fr))
    return out
def ringflash(t):
    lt=t-LAP0-LAP
    return max(0.0,1-lt/10) if 0<=lt<10 else 0.0
def draw_cell(t,s,dd,rng):
    k=f'cast_{s}_{dd}'; seq=d['anims'][k]; i,_=entry_at(t); e=seq[i]
    full=seq[2]  # full-size circle
    cimg,cax,cay=cell(full[3],full[4])
    a=np.asarray(cimg)[...,3]; ys,xs=np.nonzero(a>0)
    cx=(xs.min()+xs.max())/2-cax; cy=(ys.min()+ys.max())/2-cay; rx=(xs.max()-xs.min())/2; ry=(ys.max()-ys.min())/2
    c=Image.new('RGBA',(CW,CH),(0,0,0,0)); g=ImageDraw.Draw(c)
    g.ellipse((RX-30,RY-6,RX+30,RY+6),fill=(0,0,0,70))
    lt=t-LAP0; sweep=0 if lt<0 else min(2*math.pi,2*math.pi*lt/LAP)
    # back fx: circle revealed by the fire while the lap runs, then the original layers
    if i<=2 and lt<LAP:
        if sweep>0: c.alpha_composite(masked(cimg,cax,cay,cx,cy,rx,ry,sweep),(RX-cax,RY-cay))
    elif e[3]>=0:
        p,ax,ay=cell(e[3],e[4]); c.alpha_composite(p,(RX-ax,RY-ay))
    fl=ringflash(t)
    if fl>0:  # brief brightening when the ring closes
        p=cimg.copy(); arr=np.asarray(p).astype(np.float32); arr[...,:3]=arr[...,:3]+(255-arr[...,:3])*fl*0.7
        c.alpha_composite(Image.fromarray(arr.clip(0,255).astype(np.uint8)),(RX-cax,RY-cay))
    parts=flame(t,s,cx,cy,rx,ry,rng)
    def blit(front):
        for x,y,w,h,col,fr in parts:
            if fr!=front: continue
            X=round(RX+x); Y=round(RY+y); g.rectangle((X,Y,X+w-1,Y+h-1),fill=col)
    lay=Image.new('RGBA',(CW,CH)); g=ImageDraw.Draw(lay,'RGBA'); blit(False); c.alpha_composite(lay)
    p,ax,ay=cell(e[0],e[1]); c.alpha_composite(p,(RX-ax,RY-ay))
    if len(e)>=7 and e[5]>=0:
        p,ax,ay=cell(e[5],e[6]); c.alpha_composite(p,(RX-ax,RY-ay))
    lay=Image.new('RGBA',(CW,CH)); g=ImageDraw.Draw(lay,'RGBA'); blit(True); c.alpha_composite(lay)
    return c.resize((CW*S,CH*S),Image.NEAREST)
LW,TH=150,50; W=LW+CW*S*4; H=TH+CH*S*3+50
def draw(t,label):
    im=Image.new('RGBA',(W,H),(34,38,46,255)); g=ImageDraw.Draw(im)
    for j,dd in enumerate(dirs): g.text((LW+j*CW*S+CW*S//2-40,10),dk[dd],font=F,fill='white')
    for i,(s,nm) in enumerate(sk):
        g.text((10,TH+i*CH*S+CH*S//2-14),nm,font=F,fill='white')
        for j,dd in enumerate(dirs):
            rng=random.Random(t*131+i*17+j*7)
            im.alpha_composite(draw_cell(t,s,dd,rng),(LW+j*CW*S,TH+i*CH*S))
    g.text((10,H-42),label,font=F,fill=(200,200,200))
    return im.convert('RGB')
if __name__=='__main__':
    import sys
    k=0
    def save(im):
        global k; im.save(f'h_{k:05d}.png'); k+=1
    for rep in range(3):
        for t in range(TOTAL): save(draw(t,f'새 시안: 게임 속도 ({TOTAL/60:.1f}초, 기존 0.9초)'))
        for _ in range(20): save(draw(TOTAL-1,f'새 시안: 게임 속도 ({TOTAL/60:.1f}초, 기존 0.9초)'))
    for t in range(TOTAL):
        im=draw(t,'1/2 느리게'); save(im); save(im)
    print(TOTAL,k)
