# 5 legendary-weapon sword arcs (procedural pixel FX) on the standing hero, 3 hits each
import sys,os,math,random,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
sys.path.insert(0,'slash20');sys.path.insert(0,'slash');import fx2
import importlib.util;ARGV=list(sys.argv)
sp=importlib.util.spec_from_file_location('g','slash20/gen.py');G=importlib.util.module_from_spec(sp);sys.argv=['x'];sp.loader.exec_module(G)
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
IDLE=G.IDLE;SL=G.SL;LIFE=16
W=(255,255,255)
L5=[('성검 · 천상의 빛',dict(c=(W,(255,230,140),(255,200,60)),tk=1.25,ga=110,gw=7)),
    ('마검 · 심연의 칼날',dict(c=((255,120,120),(150,10,30),(40,0,30)),out=(10,0,10),tk=1.3,ga=140,gw=8)),
    ('뇌신검 · 천둥',dict(c=(W,(150,240,255),(60,140,255)),tk=1.1,jag=1,ga=120)),
    ('빙결검 · 서리 꽃',dict(c=(W,(190,240,255),(110,190,255)),out=(40,80,160),tk=1.2,ga=100)),
    ('염룡검 · 화염 용',dict(c=((255,255,210),(255,140,30),(200,30,0)),tk=1.4,jag=1,ga=130,gw=8))]
def bolt(d,x0,y0,x1,y1,rnd,col,w=2,depth=0):
    pts=[(x0,y0)];n=7
    for i in range(1,n):t=i/n;pts.append((x0+(x1-x0)*t+rnd.uniform(-7,7),y0+(y1-y0)*t+rnd.uniform(-7,7)))
    pts.append((x1,y1));d.line(pts,fill=col,width=w)
    if depth<1:
        for k in range(2):i=rnd.randrange(1,n);a=rnd.uniform(-1.5,1.5);L=rnd.uniform(10,22);px,py=pts[i];bolt(d,px,py,px+math.cos(a)*L,py+math.sin(a)*L,rnd,col,1,depth+1)
def extras(lay,i,s,hx,hy,cx,cy,R):
    a=s['age'];d=ImageDraw.Draw(lay);rnd=random.Random(s['n']*31+i);big=s['n']==2;al=lambda m=1:max(0,int(255*m*(1-a/LIFE)))
    if i==0:   # holy: light rays + halo + floating motes
        for k in range(6 if big else 4):
            ang=-1.2+k*.5+rnd.uniform(-.1,.1);L=(30+a*8)*(1.4 if big else 1)
            d.line([hx,hy,hx+math.cos(ang)*L,hy+math.sin(ang)*L],fill=(255,245,190,al(.7)),width=2)
        if a<10:r=8+a*5;d.ellipse([hx-r,hy-r*.35,hx+r,hy+r*.35],outline=(255,240,170,al()),width=2)
        for k in range(14):
            x=cx+rnd.uniform(-10,R+10);y=cy+rnd.uniform(-R,R)-a*rnd.uniform(1,2.5);d.rectangle([x,y,x+1,y+1],fill=(255,250,200,al()))
    if i==1:   # demonic: dark smoke puffs + red cracks + embers
        for k in range(10):
            x=cx+rnd.uniform(0,R+10)+a*1.5;y=cy+rnd.uniform(-R*.9,R*.9)-a*1.2;r=rnd.uniform(4,9)+a*.6
            d.ellipse([x-r,y-r,x+r,y+r],fill=(30,0,30,al(.45)))
        if a<9:
            for k in range(3):bolt(d,hx,hy,hx+rnd.uniform(15,35),hy+rnd.uniform(-30,30),rnd,(255,40,60,al()),2)
        for k in range(12):x=cx+rnd.uniform(0,R+20);y=cy+rnd.uniform(-R,R)-a*rnd.uniform(1,3);d.rectangle([x,y,x+1,y+1],fill=(200,60,255,al()))
    if i==2:   # thunder: bolts from the arc + flash core
        if a<10:
            for k in range(4 if big else 3):
                t=rnd.uniform(-1,1);px=cx+R*math.cos(t*.9)*.95;py=cy+R*math.sin(t*.9);bolt(d,px,py,px+rnd.uniform(20,45),py+rnd.uniform(-25,25),rnd,(220,250,255,al()),2)
        if a<3:r=10+a*6;d.ellipse([hx-r,hy-r,hx+r,hy+r],fill=(230,250,255,al(.6)))
    if i==3:   # frost: ice shards flying out + frost mist
        for k in range(10 if big else 7):
            ang=rnd.uniform(-1,1);L=a*rnd.uniform(3,6);x=hx+math.cos(ang)*L;y=hy+math.sin(ang)*L*1.3;sz=rnd.uniform(5,9)
            d.polygon([(x,y-sz),(x+sz*.5,y),(x,y+sz),(x-sz*.5,y)],fill=(220,245,255,al()),outline=(90,160,230,al()))
        for k in range(8):x=cx+rnd.uniform(0,R);y=cy+rnd.uniform(-R,R)+a*.5;r=3+a*.8;d.ellipse([x-r,y-r,x+r,y+r],fill=(220,245,255,al(.15)))
    if i==4:   # flame dragon: rising flames + embers + heat ring
        for k in range(16):
            x=cx+rnd.uniform(-5,R+15);y=cy+rnd.uniform(-R,R)-a*rnd.uniform(1.5,3.5);r=max(1,rnd.uniform(2,5)*(1-a/LIFE)*2)
            col=[(255,240,150),(255,160,40),(230,60,10)][k%3];d.ellipse([x-r,y-r*1.4,x+r,y+r*1.4],fill=(*col,al()))
        if a<10 and big:r=10+a*7;d.ellipse([hx-r*.5,hy-r,hx+r*.5,hy+r],outline=(255,180,60,al()),width=3)
def draw(spr,s,i,OX,OY):
    st=L5[i][1];a=s['age'];R,span,T,rot,y,rev,sq=SL[s['n']];R*=1.15;x=116+22+a*4
    h=min(1,(a+1)/2.5);tl=0 if a<5 else min(1,(a-5)/9)
    if tl<h:
        Tn=T*(1 if a<7 else max(.35,1-(a-7)/8))
        if i in (0,4,1):   # second outer arc for legend weight
            im=G.arc(R*1.18,span*.9,Tn*.5,h*.95,min(h,tl+.08),rot+5,rev,sq,st);im.putalpha(im.getchannel('A').point(lambda v:int(v*.75)));spr.alpha_composite(im,(int(OX+x-im.width/2),int(OY+y-im.height/2)))
        im=G.arc(R*(1+.025*a),span,Tn,h,tl,rot,rev,sq,st)
        if i==1 or i==4:   # glow halo
            g=im.filter(ImageFilter.GaussianBlur(3));g.putalpha(g.getchannel('A').point(lambda v:int(v*.8)));spr.alpha_composite(g,(int(OX+x-im.width/2),int(OY+y-im.height/2)))
        spr.alpha_composite(im,(int(OX+x-im.width/2),int(OY+y-im.height/2)))
    lay=Image.new('RGBA',spr.size);hx,hy=OX+x+R,OY+y;extras(lay,i,s,hx,hy,OX+x,OY+y,R);fx2.star(lay,hx,hy,a,True);spr.alpha_composite(lay)
TINT=[(255,240,180),(120,0,40),(200,240,255),(200,240,255),(255,150,60)]
def panel(i,act,shake,lab):
    spr=Image.new('RGBA',(440,300),(66,96,58,255));OX,OY=40,30;spr.alpha_composite(IDLE,(OX,OY))
    for s in act:draw(spr,s,i,OX,OY)
    fl=max([0]+[(4-s['age'])*(.12 if s['n']==2 else .05) for s in act if s['age']<4])
    if fl:spr.alpha_composite(Image.new('RGBA',spr.size,(*TINT[i],int(255*fl))))
    p=spr.crop((100,30,420,294)).resize((480,396),Image.NEAREST);dx=round((random.random()*2-1)*shake*3);q=Image.new('RGBA',p.size,(66,96,58,255));q.alpha_composite(p,(dx,0))
    ImageDraw.Draw(q).text((8,6),lab,font=F,fill='white');return q
def timeline():
    T=[([],0)]*6;sh=0
    for n in range(3):
        for a in range(LIFE+(2 if n<2 else 12)):
            if a==0:sh=[2,2.5,5][n]
            T.append(([{'n':n,'age':a}] if a<LIFE else [],sh));sh=sh*.8 if sh>.3 else 0
    return T
if __name__=='__main__':
    OUT=ARGV[1];os.makedirs(OUT,exist_ok=True);TL=timeline();n=0
    for slow in (1,1,2):
        for act,sh in TL:
            fr=Image.new('RGB',(1440,792),(20,20,20))
            for i,(nm,_) in enumerate(L5):
                p=panel(i,act,sh,f'{i+1}. {nm}'+(' · 1/2 슬로우' if slow>1 else '')).convert('RGB')
                fr.paste(p,((i%3)*480 if i<3 else 240+(i-3)*480,(i//3)*396))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
