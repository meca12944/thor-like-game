# 20 hero skills played on the sandbox cast clip (cast_right, release on frame 6): projectile / strike / zone / buff types
import sys,os,math,random,json,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
A='/home/user/thor-like-game/test128/sandbox/assets/';J=json.load(open(A+'hero_sbx.json'));SHT={}
def frames(k,rep):
    out=[]
    for s,c,t in J['anims'][k]:
        SHT.setdefault(s,Image.open(A+J['sheets'][s]).convert('RGBA'));x,y,w,h,ax,ay=J['cells'][s][c][:6];out+=[(SHT[s].crop((x,y,x+w,y+h)),ax,ay)]*rep
    return out
CAST=frames('cast_right',3);IDL=frames('idle_right',3);REL=6*3     # release tick
SL=Image.open(A+'slime.png').convert('RGBA');SLF=[SL.crop((i*86,0,i*86+86,78)).resize((52,47),Image.NEAREST) for i in range(3)]
W,H=440,260;HX,GY=90,222;HAND=(HX+66,GY-74);TG=[(215,GY),(280,GY),(345,GY)];TC=[(x,y-22) for x,y in TG]
LEN=62
def L(t,a,b):return max(0,min(1,(t-a)/(b-a)))
def glow_circle(lay,x,y,r,col,al=1.0):
    g=Image.new('RGBA',(W,H));d=ImageDraw.Draw(g);d.ellipse([x-r,y-r,x+r,y+r],fill=(*col,int(200*al)));g=g.filter(ImageFilter.GaussianBlur(r*.5));lay.alpha_composite(g)
    d=ImageDraw.Draw(lay);d.ellipse([x-r*.5,y-r*.5,x+r*.5,y+r*.5],fill=(255,255,255,int(255*al)))
def burst(d,x,y,t,n,col,spd=4,seed=0,size=2,grav=0):
    rnd=random.Random(seed);al=int(max(0,255-t*18))
    for k in range(n):
        g=rnd.uniform(0,6.28);s=rnd.uniform(.5,1)*spd;px=x+math.cos(g)*s*t;py=y+math.sin(g)*s*t*.7+grav*t*t;d.rectangle([px,py,px+size-1,py+size-1],fill=(*col,al))
def ring(d,x,y,r,col,al,w=2,sq=.35):d.ellipse([x-r,y-r*sq,x+r,y+r*sq],outline=(*col,int(255*max(0,al))),width=w)
def bolt(d,p0,p1,rnd,col,w=2,al=255,jit=8):
    pts=[p0];n=7
    for i in range(1,n):t=i/n;pts.append((p0[0]+(p1[0]-p0[0])*t+rnd.uniform(-jit,jit),p0[1]+(p1[1]-p0[1])*t+rnd.uniform(-jit,jit)))
    pts.append(p1);d.line(pts,fill=(*col,al),width=w+2);d.line(pts,fill=(255,255,255,al),width=max(1,w-1))
def flames(d,x,y,h,t,rnd,al=1.0,wd=6):
    for k in range(4):
        fh=h*rnd.uniform(.6,1)*(.8+.2*math.sin(t*.9+k));fx=x+rnd.uniform(-wd,wd)
        for j,(c,s) in enumerate((((200,40,0),1),((255,140,30),.7),((255,240,150),.4))):d.polygon([(fx-wd*s,y),(fx+math.sin(t*.7+k)*2,y-fh*s),(fx+wd*s,y)],fill=(*c,int(230*al)))
# each skill: f(lay,t,rnd) -> dict(hit={target:tint or None}, dx=hero x offset, tint=screen tint)
def k_fireball(lay,t,r):
    d=ImageDraw.Draw(lay);o={}
    if t<0:glow_circle(lay,*HAND,3+(t+REL)*.35,(255,120,20));return o
    if t<10:
        x=HAND[0]+(TC[1][0]-HAND[0])*t/10;y=HAND[1]+(TC[1][1]-HAND[1])*t/10
        for k in range(6):glow_circle(lay,x-k*7,y-k*.6,6-k*.8,(255,120-k*12,20),.6-k*.08)
        glow_circle(lay,x,y,9,(255,140,30));return o
    b=t-10;glow_circle(lay,*TC[1],8+b*3,(255,100,20),max(0,1-b/14));burst(d,*TC[1],b,24,(255,200,80),4,1,3,.05);ring(d,TG[1][0],GY,10+b*5,(255,180,80),1-b/14)
    if b>4:
        for k in range(6):rr=random.Random(k);x=TC[1][0]+rr.uniform(-20,20);y=TC[1][1]-b*1.2-rr.uniform(0,10);rad=4+b*.6;d.ellipse([x-rad,y-rad,x+rad,y+rad],fill=(60,50,50,int(150*max(0,1-b/26))))
    return {'hit':{1:(255,120,40)} if b<12 else {}}
def k_icespear(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:glow_circle(lay,*HAND,2+(t+REL)*.25,(150,220,255));return {}
    if t<6:
        x=HAND[0]+(TC[0][0]-HAND[0])*t/6;y=HAND[1]+(TC[0][1]-HAND[1])*t/6;ang=math.atan2(TC[0][1]-HAND[1],TC[0][0]-HAND[0]);c,s=math.cos(ang),math.sin(ang);p=lambda f,o:(x+c*f-s*o,y+s*f+c*o)
        d.polygon([p(-34,0),p(0,-5),p(16,0),p(0,5)],fill=(190,240,255,240),outline=(90,160,230,255));d.line([p(-50,0),p(-30,0)],fill=(220,250,255,150),width=2);return {}
    b=t-6;burst(d,*TC[0],b,20,(220,250,255),4.5,2,3)
    for k in range(8):
        g=k*.785;rr=12+b*3;x=TC[0][0]+math.cos(g)*rr;y=TC[0][1]+math.sin(g)*rr*.6;s=4;al=int(255*max(0,1-b/18));d.polygon([(x,y-s*1.6),(x+s*.6,y),(x,y+s*1.6),(x-s*.6,y)],fill=(220,250,255,al),outline=(90,160,230,al))
    ring(d,TG[0][0],GY,8+b*3,(200,240,255),1-b/18);return {'hit':{0:(170,230,255)} if b<40 else {}}
def k_chain(lay,t,r):
    d=ImageDraw.Draw(lay);o={'hit':{}}
    if t<0:
        if (t+REL)%3==0:bolt(d,HAND,(HAND[0]+8,HAND[1]-8),r,(255,250,140),1)
        return {}
    seq=[HAND]+TC
    for i in range(3):
        a=t-i*4
        if 0<=a<10:bolt(d,seq[i],seq[i+1],random.Random(t*7+i),(255,250,140),2,int(255*(1-a/10)));burst(d,*seq[i+1],a,10,(255,255,180),3,i,2);o['hit'][i]=(255,255,170)
    return o
def k_meteor(lay,t,r):
    d=ImageDraw.Draw(lay);x0,y0=TG[1]
    if t>=-6:
        a=L(t,-6,10);R=18+a*28;al=1 if t<22 else max(0,1-(t-22)/10);ring(d,x0,y0,R,(255,120,40),al,2);ring(d,x0,y0,R*.7,(255,200,90),al,1)
    if 4<=t<16:
        a=(t-4)/12;x=x0+120*(1-a);y=-30+(y0-20+30)*a
        for k in range(8):glow_circle(lay,x+k*8,y-k*9,9-k,(255,100-k*8,20),.7-k*.07)
        glow_circle(lay,x,y,13,(255,160,40))
    b=t-16
    if b>=0:
        glow_circle(lay,x0,y0-14,14+b*4,(255,90,10),max(0,1-b/16));ring(d,x0,y0,16+b*8,(255,200,120),1-b/16,3);burst(d,x0,y0-16,b,30,(255,200,80),5,4,3,.12)
        return {'hit':{0:(255,120,40),1:(255,120,40),2:(255,120,40)} if b<14 else {},'shake':max(0,5-b*.4)}
    return {}
def k_heal(lay,t,r):
    d=ImageDraw.Draw(lay);a=max(0,t+6)
    if a<=0:return {}
    al=1 if t<26 else max(0,1-(t-26)/10);ring(d,HX,GY,30+min(a,8)*2,(120,255,150),al,2)
    for k in range(14):
        rr=random.Random(k);x=HX+rr.uniform(-28,28);y=GY-((a*rr.uniform(2,4)+rr.uniform(0,40))%110);s=rr.choice((2,3))
        d.line([x-s,y,x+s,y],fill=(150,255,170,int(255*al)),width=2);d.line([x,y-s,x,y+s],fill=(150,255,170,int(255*al)),width=2)
    return {'hero':(120,255,150,int(70*al*(.6+.4*math.sin(t*.5))))}
def k_shield(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    a=L(t,0,6);al=1 if t<30 else max(0,1-(t-30)/12);cx,cy=HX+6,GY-60;rx,ry=52*a,70*a
    g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);dg.ellipse([cx-rx,cy-ry,cx+rx,cy+ry],fill=(120,200,255,int(60*al)),outline=(200,240,255,int(230*al)),width=2)
    for k in range(-3,4):
        yy=cy+k*18*a;w=rx*math.sqrt(max(0,1-(k*18*a/max(ry,1))**2));dg.line([cx-w,yy,cx+w,yy],fill=(200,240,255,int(80*al)))
    sh=(t*6)%(2*ry+1)-ry if ry else 0;dg.line([cx-rx*.7,cy+sh,cx+rx*.7,cy+sh-8],fill=(255,255,255,int(150*al)),width=2);lay.alpha_composite(g);return {}
def k_bladestorm(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    al=1 if t<26 else max(0,1-(t-26)/8);R=40+min(t,8)*8
    for k in range(4):
        ph=t*28+k*90
        for j in range(6):
            an=math.radians(ph-j*9);x=HX+10+math.cos(an)*R;y=GY-40+math.sin(an)*R*.4;a2=al*(1-j/6)
            d.line([x,y,x+math.cos(an+1.57)*10,y+math.sin(an+1.57)*4],fill=(170,230,255,int(255*a2)),width=3 if j==0 else 2)
    return {'hit':{0:(200,240,255)} if t%6<2 and t<26 else {}}
def k_blink(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    burst(d,HX,GY-60,t,18,(200,170,255),3.5,2,2)
    if t<10:
        for k in range(4):x=HX+(t/10)*110*(k/4);d.rectangle([x-8,GY-110,x+8,GY],fill=(180,150,255,int(60*(1-t/10))))
    if t>=6:b=t-6;burst(d,HX+110,GY-60,b,18,(230,210,255),3.5,3,2);ring(d,HX+110,GY,10+b*3,(200,170,255),1-b/14)
    return {'dx':110 if t>=6 else 0,'heroal':(0 if 2<=t<6 else 1)}
def k_poison(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    a=L(t,0,8);al=1 if t<40 else max(0,1-(t-40)/12);cx=TG[1][0];g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g)
    dg.ellipse([cx-90*a,GY-14*a,cx+90*a,GY+14*a],fill=(90,170,40,int(150*al)),outline=(160,255,90,int(220*al)),width=2);lay.alpha_composite(g)
    for k in range(12):
        rr=random.Random(k);x=cx+rr.uniform(-80,80)*a;ph=(t*rr.uniform(.8,1.5)+rr.uniform(0,20))%20;y=GY-ph*1.2;rad=1.5+ph*.12;d.ellipse([x-rad,y-rad,x+rad,y+rad],outline=(180,255,110,int(220*al*(1-ph/20))))
    return {'hit':{0:(140,255,90),1:(140,255,90),2:(140,255,90)} if t>4 else {}}
def k_tornado(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    x=HAND[0]+t*5;al=1 if t<34 else max(0,1-(t-34)/8)
    for k in range(12):
        y=GY-k*9;w=6+k*3.2;ph=t*.9+k*.6;ox=math.sin(ph)*4
        d.arc([x+ox-w,y-w*.25,x+ox+w,y+w*.25],200,520,fill=(210,255,235,int(220*al)),width=2)
    burst(d,x,GY-20,t%10,8,(200,230,200),3,t//10,2)
    return {'hit':{i:(210,255,235) for i,(tx,ty) in enumerate(TG) if abs(tx-x)<26}}
def k_pillar(lay,t,r):
    d=ImageDraw.Draw(lay);x=TG[1][0]
    if t<0:return {}
    if t<6:ring(d,x,GY,10+t*4,(255,230,140),1,2);return {}
    b=t-6;al=1 if b<14 else max(0,1-(b-14)/8);w=10+min(b,4)*4
    g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);dg.rectangle([x-w,0,x+w,GY],fill=(255,230,140,int(150*al)));g=g.filter(ImageFilter.GaussianBlur(6));lay.alpha_composite(g)
    d.rectangle([x-w*.35,0,x+w*.35,GY],fill=(255,255,235,int(230*al)));ring(d,x,GY,w*2.2,(255,240,170),al,3)
    for k in range(8):an=k*.785+b*.1;d.line([x,GY-20,x+math.cos(an)*(30+b*2),GY-20+math.sin(an)*(30+b*2)*.5],fill=(255,245,190,int(160*al)))
    return {'hit':{1:(255,240,160)} if b<16 else {}}
def k_spikes(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    hit={}
    for k in range(8):
        x=HX+50+k*38;a=t-k*1.5
        if a<0:continue
        h=min(1,a/3)*(34+(k%3)*8);al=1 if a<14 else max(0,1-(a-14)/8)
        d.polygon([(x-10,GY+2),(x-1,GY-h),(x+10,GY+2)],fill=(120,90,60,int(255*al)),outline=(70,50,30,int(255*al)));d.line([x-1,GY-h,x+3,GY-h*.4],fill=(180,150,110,int(255*al)))
        if a<6:burst(d,x,GY,a,6,(170,140,100),2.5,k,2)
        for i,(tx,ty) in enumerate(TG):
            if abs(tx-x)<20 and a<10:hit[i]=(200,170,120)
    return {'hit':hit}
def k_darkorb(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:glow_circle(lay,*HAND,2+(t+REL)*.3,(140,60,200));return {}
    a=L(t,0,24);x=HAND[0]+(TC[1][0]-HAND[0])*a;y=HAND[1]+(TC[1][1]-HAND[1])*a
    if t<26:
        g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);dg.ellipse([x-14,y-14,x+14,y+14],fill=(90,20,140,200));g=g.filter(ImageFilter.GaussianBlur(5));lay.alpha_composite(g)
        d.ellipse([x-8,y-8,x+8,y+8],fill=(20,0,30,255),outline=(200,120,255,255))
        for k in range(10):rr=random.Random(k);an=rr.uniform(0,6.28)+t*.3;dd=30-((t*2+k*3)%30);d.rectangle([x+math.cos(an)*dd,y+math.sin(an)*dd,x+math.cos(an)*dd+1,y+math.sin(an)*dd+1],fill=(200,140,255,230))
        return {}
    b=t-26;ring(d,x,y,30-b*3 if b<8 else 6+(b-8)*6,(200,120,255),1-b/20,3,1);burst(d,x,y,max(0,b-8),20,(220,160,255),4,9,2)
    return {'hit':{0:(160,90,220),1:(160,90,220),2:(160,90,220)} if 8<=b<20 else {}}
def k_wave(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    x=HAND[0]-10+t*7;al=1 if t<30 else max(0,1-(t-30)/8);h=30+math.sin(t*.4)*4
    g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);dg.polygon([(x-60,GY+2),(x-20,GY-h*.5),(x,GY-h),(x+10,GY-h*.6),(x+8,GY+2)],fill=(40,140,230,int(200*al)));lay.alpha_composite(g)
    d.line([(x-20,GY-h*.5),(x,GY-h),(x+10,GY-h*.6)],fill=(220,250,255,int(255*al)),width=3)
    burst(d,x+6,GY-h,t%8,10,(200,240,255),3,t//8,2,.12)
    return {'hit':{i:(80,170,255) for i,(tx,ty) in enumerate(TG) if -10<x-tx<30}}
def k_nova(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    R=10+t*7;al=1 if t<24 else max(0,1-(t-24)/10);ring(d,HX,GY,R,(200,240,255),al,3);ring(d,HX,GY,R*.85,(140,210,255),al*.6,1)
    for k in range(16):
        an=k*.3927;x=HX+math.cos(an)*R;y=GY+math.sin(an)*R*.35;s=4+(k%2)*2;d.polygon([(x,y-s*2),(x+s*.5,y),(x,y+2),(x-s*.5,y)],fill=(220,250,255,int(240*al)),outline=(90,160,230,int(255*al)))
    return {'hit':{i:(170,230,255) for i,(tx,ty) in enumerate(TG) if R>tx-HX-10}}
def k_firewall(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    al=1 if t<36 else max(0,1-(t-36)/10)
    for k in range(9):
        x=TG[0][0]-30+k*8;h=min(1,(t-k*.6)/6)*(38+math.sin(t*.8+k)*8)
        if h>0:flames(d,x,GY,h,t+k,random.Random(k*3+t//3),al,6)
    return {'hit':{0:(255,140,60)} if t>4 else {}}
def k_thunder(lay,t,r):
    d=ImageDraw.Draw(lay);hit={}
    if t<0:return {}
    for i,(x,y) in enumerate(TG):
        a=t-i*5
        if 0<=a<9:
            al=int(255*(1-a/9));bolt(d,(x+random.Random(t).uniform(-10,10),0),(x,y-20),random.Random(t*3+i),(150,200,255),5,al,10);glow_circle(lay,x,y-20,10,(180,220,255),1-a/9);ring(d,x,GY,8+a*4,(220,240,255),1-a/9,2);burst(d,x,y-20,a,14,(255,255,200),4,i,2);hit[i]=(230,240,255)
    return {'hit':hit,'flash':(255,255,255,60) if t in (0,5,10) else None}
def k_berserk(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    al=1 if t<34 else max(0,1-(t-34)/10)
    for k in range(10):
        rr=random.Random(k);x=HX+rr.uniform(-26,30);h=rr.uniform(30,60)*(1+.2*math.sin(t*.7+k));flames(d,x,GY,h,t+k,random.Random(k+t//2),al*.75,5)
    if t%7<2:bolt(d,(HX-20,GY-110),(HX+20,GY-60),random.Random(t),(255,60,60),1,int(220*al))
    return {'hero':(255,60,40,int(80*al)),'flash':(255,0,0,int(30*al)) if t<4 else None}
def k_haste(lay,t,r):
    d=ImageDraw.Draw(lay)
    if t<0:return {}
    al=1 if t<34 else max(0,1-(t-34)/10)
    for k in range(12):
        rr=random.Random(k);y=GY-rr.uniform(10,110);x=HX-60+((t*9+rr.uniform(0,120))%150);d.line([x,y,x+18,y],fill=(200,255,220,int(200*al)),width=1)
    for k in range(3):an=t*.4+k*2.1;d.arc([HX-36,GY-80+k*20,HX+40,GY-60+k*20],math.degrees(an),math.degrees(an)+150,fill=(150,255,200,int(220*al)),width=2)
    return {'hero':(150,255,200,int(50*al))}
def k_arrows(lay,t,r):
    d=ImageDraw.Draw(lay);hit={}
    if t<0:return {}
    for k in range(5):
        a=(t-k*2)/12
        if a<0 or a>1.6:continue
        tx,ty=TC[k%3];a1=min(1,a);sx,sy=HAND;cx,cy=(sx+tx)/2,sy-60-k*10
        x=(1-a1)**2*sx+2*(1-a1)*a1*cx+a1*a1*tx;y=(1-a1)**2*sy+2*(1-a1)*a1*cy+a1*a1*ty
        if a<1:
            dx=2*(1-a1)*(cx-sx)+2*a1*(tx-cx);dy=2*(1-a1)*(cy-sy)+2*a1*(ty-cy);n=math.hypot(dx,dy) or 1;dx,dy=dx/n,dy/n
            d.line([x-dx*20,y-dy*20,x,y],fill=(255,240,160,200),width=2);d.polygon([(x+dx*6,y+dy*6),(x-dy*3,y+dx*3),(x+dy*3,y-dx*3)],fill=(255,255,220,255))
        else:b=(a-1)*12;burst(d,tx,ty,b,10,(255,240,160),3,k,2);hit[k%3]=(255,240,160)
    return {'hit':hit}
SK=[('화염구',k_fireball),('빙창',k_icespear),('연쇄 번개',k_chain),('메테오',k_meteor),('회복의 빛',k_heal),('수호 방패',k_shield),('검기 폭풍',k_bladestorm),('순간이동',k_blink),
    ('독 장판',k_poison),('회오리',k_tornado),('성광 기둥',k_pillar),('대지 균열',k_spikes),('암흑 구체',k_darkorb),('물의 파동',k_wave),('빙결 서클',k_nova),('화염 벽',k_firewall),
    ('뇌신 강림',k_thunder),('버서크',k_berserk),('바람 가속',k_haste),('별빛 화살',k_arrows)]
def tinted(im,col,k):
    a=np.array(im).astype(float);a[...,:3]=a[...,:3]*(1-k)+np.array(col[:3])*k;return Image.fromarray(a.clip(0,255).astype(np.uint8))
def panel(i,f):
    nm,fn=SK[i];t=f-REL;img=Image.new('RGBA',(W,H),(66,96,58,255));d=ImageDraw.Draw(img);lay=Image.new('RGBA',(W,H));o=fn(lay,t,random.Random(i)) or {}
    hit=o.get('hit',{})
    for k,(x,y) in enumerate(TG):
        fr=SLF[(f//6)%3]
        if k in hit:fr=tinted(fr,hit[k],.55)
        d.ellipse([x-16,y-3,x+16,y+3],fill=(0,0,0,50));img.alpha_composite(fr,(x-26,y-47))
    im,ax,ay=(CAST[f] if f<len(CAST) else IDL[f%len(IDL)]);dx=o.get('dx',0)
    if 'hero' in o:im=tinted(im,o['hero'],o['hero'][3]/255)
    if o.get('heroal',1)>0:img.alpha_composite(im,(int(HX+dx-ax),GY-ay))
    img.alpha_composite(lay)
    if o.get('flash'):img.alpha_composite(Image.new('RGBA',(W,H),o['flash']))
    sh=o.get('shake',0);q=Image.new('RGBA',(W,H),(66,96,58,255));q.alpha_composite(img,(round((random.random()*2-1)*sh),0))
    p=q.crop((30,40,430,250)).resize((288,151),Image.NEAREST);ImageDraw.Draw(p).text((4,2),nm if nm[:2].isdigit() else f'{i+1}. {nm}',font=F,fill='white');return p
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);n=0
    for slow in (1,2):
        for f in range(REL+LEN):
            fr=Image.new('RGB',(1440,604))
            for i in range(20):fr.paste(panel(i,f).convert('RGB'),((i%5)*288,(i//5)*151))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
