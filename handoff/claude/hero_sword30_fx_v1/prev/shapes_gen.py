# 12 sword-slash SHAPES (stroke-based pixel FX) on the standing hero, 3 hits each
import sys,os,math,random
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
IDLE=Image.open('/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/east/000.png').convert('RGBA')
OX,OY=40,30;CX,CY=OX+172,OY+112      # in front of the chest
LIFE=14
def stroke(img,pts,w0,cols,taper=True,alpha=1.0,glow=4):
    """pts: polyline; width w0 at the middle (tapered at both ends); cols=(core,mid,glow)"""
    d=ImageDraw.Draw(img);n=len(pts);core,mid,gl=cols
    seg=[]
    for i in range(n-1):
        (x0,y0),(x1,y1)=pts[i],pts[i+1];L=max(1,int(math.hypot(x1-x0,y1-y0)))
        for k in range(L):seg.append((x0+(x1-x0)*k/L,y0+(y1-y0)*k/L,(i+k/L)/(n-1)))
    for layer,(col,add,a) in enumerate(((gl,glow,.35),(mid,0,.9),(core,-.5,1))):
        for x,y,t in seg:
            w=w0*(math.sin(math.pi*t)**.7 if taper else 1)*(.3+.7*t)
            r=max(.5,w/2*(1 if layer<2 else .4)+add)
            d.ellipse([x-r,y-r,x+r,y+r],fill=(*col,int(255*a*alpha)))
def arcpts(cx,cy,R,a0,a1,n=40,sq=1):return [(cx+R*math.cos(math.radians(a0+(a1-a0)*i/n)),cy+R*math.sin(math.radians(a0+(a1-a0)*i/n))*sq) for i in range(n+1)]
def part(pts,h,tl):   # visible part of a polyline (head/tail 0..1)
    n=len(pts);i0=int(tl*(n-1));i1=max(i0+1,int(h*(n-1)));return pts[i0:i1+1]
BLUE=((255,255,255),(130,210,255),(50,110,255))
def ht(a,grow=2.5,hold=4,fade=7):return min(1,(a+1)/grow),(0 if a<hold else min(1,(a-hold)/fade))
def fadea(a):return 1 if a<7 else max(0,1-(a-7)/7)
def s_iai(img,a,big,rnd):   # 1 일섬: long straight flash line
    h,t=ht(a,1.5,3,6);L=150*(1.3 if big else 1);pts=[(CX-30+L*i/20,CY+5-6*i/20) for i in range(21)]
    p=part(pts,h,t)
    if len(p)>1:stroke(img,p,8 if big else 6,BLUE,alpha=fadea(a))
    if a<3:d=ImageDraw.Draw(img);d.line([CX-40,CY+5,CX+L,CY-1],fill=(255,255,255,200),width=1)
def s_ring(img,a,big,rnd):  # 2 회전베기: full circle around the hero
    h,t=ht(a,3,5,7);p=part(arcpts(OX+116,OY+120,70*(1.15 if big else 1),-90,270,60,.45),h,t)
    if len(p)>1:stroke(img,p,12,BLUE,alpha=fadea(a))
def s_cross(img,a,big,rnd): # 3 십자참: two crossing straight slashes
    s=1.3 if big else 1
    for k,(dx0,dy0,dx1,dy1) in enumerate(((-30,-45,45,40),(-30,40,45,-45))):
        aa=a-k*2
        if aa<0:continue
        h,t=ht(aa,1.5,3,6);pts=[(CX+(dx0+(dx1-dx0)*i/16)*s,CY+(dy0+(dy1-dy0)*i/16)*s) for i in range(17)];p=part(pts,h,t)
        if len(p)>1:stroke(img,p,9,BLUE,alpha=fadea(aa))
def s_claw(img,a,big,rnd):  # 4 삼연 발톱: three parallel claw marks
    s=1.25 if big else 1
    for k in range(3):
        aa=a-k;
        if aa<0:continue
        h,t=ht(aa,1.5,3,6);o=(k-1)*14*s;pts=[(CX-20+o+(55*s)*i/12,CY-45*s+o*.3+(85*s)*i/12) for i in range(13)];p=part(pts,h,t)
        if len(p)>1:stroke(img,p,7,((255,255,255),(255,120,120),(200,30,60)),alpha=fadea(aa))
def s_spiral(img,a,big,rnd):# 5 나선 검풍
    h,t=ht(a,3,5,7);R=55*(1.2 if big else 1);pts=[(CX+10+(R*(.3+.7*i/60))*math.cos(math.radians(-120+i*9)),CY+(R*(.3+.7*i/60))*math.sin(math.radians(-120+i*9))*.8) for i in range(61)];p=part(pts,h,t)
    if len(p)>1:stroke(img,p,10,((240,255,250),(120,240,190),(30,150,110)),alpha=fadea(a))
def s_thrust(img,a,big,rnd):# 6 창섬 찌르기: cone spike forward + rings
    h,t=ht(a,1.5,3,6);L=(110 if not big else 150)*h;d=ImageDraw.Draw(img);al=int(255*fadea(a))
    x0=CX-20;d.polygon([(x0,CY-9),(x0+L,CY),(x0,CY+9)],fill=(80,150,255,al//2));d.polygon([(x0,CY-5),(x0+L,CY),(x0,CY+5)],fill=(170,225,255,al));d.line([x0,CY,x0+L,CY],fill=(255,255,255,al),width=2)
    for k in range(3):
        rx=x0+L*(.35+.25*k);r=10-k*2+a*.5;d.ellipse([rx-r*.35,CY-r,rx+r*.35,CY+r],outline=(220,245,255,al),width=1)
def s_wave(img,a,big,rnd):  # 7 파동 검기: sine ribbon travelling forward
    h,t=ht(a,3,5,7);sh=a*5;pts=[(CX-20+sh+i*4,CY+math.sin(i*.45+a*.6)*14*(1.2 if big else 1)) for i in range(36)];p=part(pts,h,t)
    if len(p)>1:stroke(img,p,9,((255,250,255),(220,150,255),(130,60,220)),alpha=fadea(a))
def s_boomer(img,a,big,rnd):# 8 부메랑 검풍: crescent flying far and spinning
    x=CX-5+a*12;rot=a*28;R=26*(1.3 if big else 1);pts=arcpts(x,CY,R,rot-70,rot+70,24)
    stroke(img,pts,10,BLUE,alpha=fadea(a))
    if a>1:
        for g in (1,2):
            gx=x-g*14;stroke(img,arcpts(gx,CY,R,rot-g*28-70,rot-g*28+70,16),6,BLUE,alpha=fadea(a)*.3/g)
def s_petal(img,a,big,rnd): # 9 꽃잎 베기: arc + sakura petals
    h,t=ht(a);p=part(arcpts(CX-35,CY,60*(1.2 if big else 1),-70,70,40),h,t)
    if len(p)>1:stroke(img,p,12,((255,250,252),(255,170,200),(230,90,150)),alpha=fadea(a))
    d=ImageDraw.Draw(img);r2=random.Random(7)
    for k in range(16):
        ang=r2.uniform(-1.3,1.3);L=a*r2.uniform(2,6);x=CX+25+math.cos(ang)*L;y=CY+math.sin(ang)*L+a*a*.08;s=r2.uniform(2,4)
        d.ellipse([x-s,y-s*.6,x+s,y+s*.6],fill=(255,190,215,int(255*max(0,1-a/LIFE))))
def s_crack(img,a,big,rnd): # 10 지면 균열: downward cut + ground cracks
    h,t=ht(a,1.5,4,7);pts=[(CX+5+10*i/16,CY-60+(115)*i/16) for i in range(17)];p=part(pts,h,t)
    if len(p)>1:stroke(img,p,10,((255,255,220),(255,200,90),(220,110,20)),alpha=fadea(a))
    if a>=2:
        d=ImageDraw.Draw(img);r2=random.Random(3);gy=OY+190;al=int(255*max(0,1-(a-2)/12))
        for k in range(5 if big else 3):
            x=CX+15;y=gy;ang=r2.uniform(-.5,.5)+(0 if k%2 else math.pi*0)
            for j in range(int(min(a-1,6))):
                nx=x+r2.uniform(8,14);ny=y+r2.uniform(-4,4)*.6+(k-2)*1.5;d.line([x,y,nx,ny],fill=(60,40,20,al),width=2);d.line([x,y-1,nx,ny-1],fill=(255,210,120,al//2),width=1);x,y=nx,ny
def s_flurry(img,a,big,rnd):# 11 난도질: many quick small slashes
    r2=random.Random(11);n=8 if big else 5
    for k in range(n):
        aa=a-k*1.2
        if aa<0 or aa>8:continue
        cx=CX+r2.uniform(-5,45);cy=CY+r2.uniform(-35,35);ang=r2.uniform(0,math.pi);L=r2.uniform(25,40)
        h,t=ht(aa,1,2,4);pts=[(cx-math.cos(ang)*L/2+math.cos(ang)*L*i/8,cy-math.sin(ang)*L/2+math.sin(ang)*L*i/8) for i in range(9)];p=part(pts,h,t)
        if len(p)>1:stroke(img,p,5,BLUE,alpha=max(0,1-aa/8))
def s_moon(img,a,big,rnd):  # 12 만월 이중: two opposing crescents forming a full moon
    h,t=ht(a,3,5,7);R=50*(1.2 if big else 1)
    for k,(a0,a1) in enumerate(((-100,100),(80,280))):
        p=part(arcpts(CX+15,CY,R*(1 if k==0 else .85),a0,a1,40),h,t)
        if len(p)>1:stroke(img,p,11 if k==0 else 7,((255,255,235),(255,225,120),(210,150,40)) if k==0 else ((235,245,255),(160,180,255),(80,90,220)),alpha=fadea(a))
V=[('일섬',s_iai),('회전베기',s_ring),('십자참',s_cross),('삼연 발톱',s_claw),('나선 검풍',s_spiral),('창섬 찌르기',s_thrust),
   ('파동 검기',s_wave),('부메랑 검풍',s_boomer),('꽃잎 베기',s_petal),('지면 균열',s_crack),('난도질',s_flurry),('만월 이중',s_moon)]
def panel(fn,act,lab):
    spr=Image.new('RGBA',(440,300),(66,96,58,255));spr.alpha_composite(IDLE,(OX,OY))
    for s in act:
        lay=Image.new('RGBA',spr.size);fn(lay,s['age'],s['n']==2,None);spr.alpha_composite(lay)
    p=spr.crop((60,40,420,280)).resize((240,160),Image.NEAREST).resize((288,192),Image.NEAREST);ImageDraw.Draw(p).text((6,4),lab,font=F,fill='white');return p
def timeline():
    T=[[] for _ in range(6)]
    for n in range(3):
        for a in range(LIFE+(3 if n<2 else 10)):T.append([{'n':n,'age':a}] if a<LIFE else [])
    return T
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);TL=timeline();n=0
    for slow in (1,1,2):
        for f,act in enumerate(TL):
            fr=Image.new('RGB',(288*4,192*3))
            for i,(nm,fn) in enumerate(V):fr.paste(panel(fn,act,f'{i+21}. {nm}').convert('RGB'),((i%4)*288,(i//4)*192))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
