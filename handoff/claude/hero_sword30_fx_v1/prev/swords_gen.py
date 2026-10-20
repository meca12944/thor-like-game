# sword-SHAPED effects: energy swords appear / fly / fall / orbit. 8 styles x 3-hit combos on the standing hero
import sys,os,math,random
from PIL import Image,ImageDraw,ImageFont,ImageFilter
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
IDLE=Image.open('/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/east/000.png').convert('RGBA')
W,H=460,300;OX,OY=30,30;HX,HY=OX+116,OY+112;GY=OY+190
C={'blue':((255,255,255),(150,220,255),(50,120,255)),'gold':((255,255,225),(255,210,90),(220,120,20)),'red':((255,235,235),(255,100,110),(180,20,40)),
   'violet':((245,225,255),(185,120,255),(90,30,200)),'jade':((235,255,245),(110,235,180),(20,140,100)),'white':((255,255,255),(225,235,245),(150,170,200))}
BASE={}
def base(col):
    if col in BASE:return BASE[col]
    core,mid,gl=C[col];L,Wd=64,26;im=Image.new('RGBA',(L+20,Wd),(0,0,0,0));d=ImageDraw.Draw(im);cy=Wd//2
    d.polygon([(22,cy-4),(L+6,cy-3),(L+16,cy),(L+6,cy+3),(22,cy+4)],fill=(*mid,235))          # blade
    d.line([(24,cy),(L+12,cy)],fill=(*core,255),width=2)                                       # fuller / edge light
    d.rectangle([17,cy-10,21,cy+10],fill=(*mid,255));d.rectangle([18,cy-9,20,cy+9],fill=(*core,255))   # guard
    d.rectangle([6,cy-2,17,cy+2],fill=(*gl,255));d.ellipse([2,cy-4,8,cy+4],fill=(*mid,255))     # grip + pommel
    g=im.filter(ImageFilter.GaussianBlur(3));gl_im=Image.new('RGBA',im.size,(*gl,0));gl_im.putalpha(g.getchannel('A').point(lambda v:min(255,int(v*1.4))))
    out=Image.new('RGBA',im.size);out.alpha_composite(gl_im);out.alpha_composite(im);BASE[col]=out;return out
CACHE={}
def sword(lay,x,y,ang,sc,col,al=1.0):
    """draw an energy sword, tip pointing at angle ang (deg, screen), centre of blade at x,y"""
    key=(col,round(ang/3)*3,round(sc*20)/20)
    if key not in CACHE:
        b=base(col);b=b.resize((max(1,int(b.width*key[2])),max(1,int(b.height*key[2]))),Image.NEAREST);CACHE[key]=b.rotate(-key[1],Image.NEAREST,expand=True)
    im=CACHE[key]
    if al<1:im=im.copy();im.putalpha(im.getchannel('A').point(lambda v:int(v*max(0,al))))
    lay.alpha_composite(im,(int(x-im.width/2),int(y-im.height/2)))
def flash(d,x,y,b,big,col=(255,255,255)):
    if b<0 or b>=7:return
    al=int(255*(1-b/7));R=5+b*(4 if big else 2.5);d.ellipse([x-R,y-R*.6,x+R,y+R*.6],outline=(*col,al),width=2)
    L=(14 if big else 9)*(1-b/7)+2;d.line([x-L,y,x+L,y],fill=(255,255,255,al),width=2);d.line([x,y-L*.7,x,y+L*.7],fill=(255,255,255,al),width=1)
def trail(lay,x0,y0,x1,y1,col,al):
    d=ImageDraw.Draw(lay);c=C[col][1];d.line([x0,y0,x1,y1],fill=(*c,int(120*al)),width=3);d.line([x0,y0,x1,y1],fill=(255,255,255,int(160*al)),width=1)
fo=lambda a,s,e:1 if a<s else max(0,1-(a-s)/(e-s))
# ---- styles: f(lay,n,a) ----
def v_flying(lay,n,a):      # 비검 3연: 1 / 2 / 3 swords launched forward
    d=ImageDraw.Draw(lay);k=n+1
    for i in range(k):
        off=(i-(k-1)/2)*16;aa=a-i;
        if aa<0:continue
        x=HX+30+aa*14;y=HY+off;al=fo(aa,10,16);trail(lay,x-40,y,x-12,y,'blue',al);sword(lay,x,y,0,1.0+.15*n,'blue',al)
        if x>HX+170:flash(d,HX+190,y,aa-10,n==2)
def v_giant(lay,n,a):       # 거대검: swing / rise / falls from the sky
    d=ImageDraw.Draw(lay)
    if n<2:
        a0,a1=(-110,30) if n==0 else (60,-90);t=min(1,a/5);ang=a0+(a1-a0)*(1-(1-t)**3)
        for g in range(1,4):
            tg=max(0,t-g*.12);ag=a0+(a1-a0)*(1-(1-tg)**3);r=58;sword(lay,HX+20+math.cos(math.radians(ag))*r,HY+math.sin(math.radians(ag))*r,ag,1.6,'gold',fo(a,6,12)*.3/g)
        r=58;sword(lay,HX+20+math.cos(math.radians(ang))*r,HY+math.sin(math.radians(ang))*r,ang,1.6,'gold',fo(a,6,12))
        if a>=5:x=HX+20+math.cos(math.radians(a1))*110;y=HY+math.sin(math.radians(a1))*110;flash(d,x,y,a-5,False,(255,220,120))
    else:
        tx=HX+120;yy=min(GY-60,OY-60+a*22);sword(lay,tx,yy,90,3.0,'gold',fo(a,14,22))
        if yy>=GY-60:
            b=a-int((GY-60-(OY-60))/22);flash(d,tx,GY,b,True,(255,220,120))
            for q in range(10):
                rr=random.Random(q);x=tx+rr.uniform(-40,40)+b*rr.uniform(-3,3);y=GY-b*rr.uniform(.5,2);r=2+b*.8;d.ellipse([x-r,y-r*.6,x+r,y+r*.6],fill=(200,180,140,int(200*max(0,1-b/12))))
def v_rain(lay,n,a):        # 검우: swords drop from above onto the area in front
    d=ImageDraw.Draw(lay);k=[3,5,10][n];rnd=random.Random(n*7)
    for i in range(k):
        st=i*(1.2 if n<2 else .7);aa=a-st
        if aa<0:continue
        x=HX+60+rnd.uniform(0,110);gy=GY-rnd.uniform(0,25);y=min(gy-30,OY-40+aa*26)
        sword(lay,x,y,90,1.1,'violet',fo(aa,9,14))
        if y>=gy-30:flash(d,x,gy,aa-int((gy-30-(OY-40))/26),n==2,(200,150,255))
def v_orbit(lay,n,a):       # 회전 검륜: swords circle the hero then launch
    k=[2,3,6][n];d=ImageDraw.Draw(lay)
    for i in range(k):
        ph=i*360/k+a*40
        if a<7:
            r=46;x=HX+math.cos(math.radians(ph))*r;y=HY+10+math.sin(math.radians(ph))*r*.45;sword(lay,x,y,ph+90,.9,'jade',1)
        else:
            aa=a-7;ang=-25+50*i/max(1,k-1) if k>1 else 0;x=HX+40+math.cos(math.radians(ang))*aa*15;y=HY+math.sin(math.radians(ang))*aa*15
            trail(lay,x-math.cos(math.radians(ang))*30,y-math.sin(math.radians(ang))*30,x,y,'jade',fo(aa,7,12));sword(lay,x,y,ang,1.0,'jade',fo(aa,7,12))
def v_fan(lay,n,a):         # 검진 부채: swords appear in a fan behind, then fire forward
    k=[3,5,7][n];d=ImageDraw.Draw(lay)
    for i in range(k):
        sp=i/(k-1);bx=HX-25+abs(sp-.5)*30;by=HY-70+sp*90
        if a<5:al=min(1,(a+1)/3);sword(lay,bx-10,by,0,1.0,'red',al)
        else:
            aa=a-5-i*.6
            if aa<0:sword(lay,bx-10,by,0,1.0,'red',1);continue
            x=bx-10+aa*20;y=by+(HY-by)*min(1,aa/6)*.6;trail(lay,x-40,y,x-10,y,'red',fo(aa,7,11));sword(lay,x,y,0,1.0,'red',fo(aa,7,11))
def v_cross(lay,n,a):       # 십자검: thrust / X cross / giant cross
    d=ImageDraw.Draw(lay)
    if n==0:
        x=HX+20+min(a,5)*14;sword(lay,x,HY,0,1.2,'white',fo(a,7,12));flash(d,x+45,HY,a-5,False)
    elif n==1:
        for i,ang in enumerate((-40,40)):
            aa=a-i*2
            if aa<0:continue
            t=min(1,aa/4);cx,cy=HX+90,HY;r=70*(1-t);x=cx-math.cos(math.radians(ang))*r;y=cy-math.sin(math.radians(ang))*r;sword(lay,x,y,ang,1.3,'white',fo(aa,8,13))
        flash(d,HX+90,HY,a-6,False)
    else:
        sc=2.2;cx,cy=HX+100,HY-5;al=fo(a,12,20)
        if a<4:sc*=a/4+.2
        sword(lay,cx,cy,-45,sc,'blue',al);sword(lay,cx,cy,45,sc,'blue',al);flash(d,cx,cy,a-4,True)
def v_ghost(lay,n,a):       # 유령검 베기: a ghost sword sweeps and leaves sword-shaped afterimages along the arc
    a0,a1,r,sc=[(-100,40,52,1.3),(70,-90,52,1.3),(-150,100,62,1.7)][n];D=[5,5,7][n];col=['blue','violet','gold'][n]
    t=min(1,a/D);hd=1-(1-t)**3;steps=7 if n<2 else 11
    for i in range(steps+1):
        u=i/steps
        if u>hd:break
        ag=a0+(a1-a0)*u;age=(hd-u)*D+max(0,a-D);al=max(0,1-age/(6 if n<2 else 8))*(.35+.65*(u/hd if hd else 1))
        sword(lay,HX+35+math.cos(math.radians(ag))*r,HY+math.sin(math.radians(ag))*r*(.6 if n==0 else .8 if n==1 else 1),ag,sc,col,al)
    if a>=D:d=ImageDraw.Draw(lay);flash(d,HX+35+math.cos(math.radians(a1))*(r+40),HY+math.sin(math.radians(a1))*(r+40)*.8,a-D,n==2)
def v_spikes(lay,n,a):      # 지면검 솟구치기: swords erupt from the ground in a line forward
    k=[3,5,8][n];d=ImageDraw.Draw(lay)
    for i in range(k):
        aa=a-i*1.2
        if aa<0:continue
        x=HX+45+i*(140/k)*(1.3 if n==2 else 1);up=min(1,aa/3);sc=[1.0,1.15,1.4][n];L=40*sc
        y=GY+12-up*L;al=fo(aa,8,12);sword(lay,x,y,-90,sc,'red' if n==2 else 'jade',al)
        if aa<4:d.ellipse([x-10,GY-3,x+10,GY+3],fill=(70,50,30,int(200*al)))
        flash(d,x,GY-L,aa-2,n==2,(255,200,200) if n==2 else (200,255,230))
STY=[('비검 3연',v_flying),('거대검',v_giant),('검우',v_rain),('회전 검륜',v_orbit),('검진 부채',v_fan),('십자검',v_cross),('유령검 베기',v_ghost),('지면검 솟구치기',v_spikes)]
LIFE=[18,18,26]
def panel(fn,act,shake,lab):
    spr=Image.new('RGBA',(W,H),(66,96,58,255));spr.alpha_composite(IDLE,(OX,OY))
    for s in act:
        lay=Image.new('RGBA',(W,H));fn(lay,s['n'],s['age']);spr.alpha_composite(lay)
    p=spr.crop((40,0,440,300)).resize((360,270),Image.NEAREST);q=Image.new('RGBA',p.size,(66,96,58,255));q.alpha_composite(p,(round((random.random()*2-1)*shake*2),0))
    ImageDraw.Draw(q).text((6,4),lab,font=F,fill='white');return q
def timeline():
    T=[([],0)]*6;sh=0
    for n in range(3):
        for a in range(LIFE[n]+(2 if n<2 else 8)):
            if a==5:sh=[1.2,1.8,4][n]
            T.append(([{'n':n,'age':a}] if a<LIFE[n] else [],sh));sh=sh*.8 if sh>.3 else 0
    return T
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);TL=timeline();n=0
    for slow in (1,1,2):
        for act,sh in TL:
            fr=Image.new('RGB',(1440,540))
            for i,(nm,fn) in enumerate(STY):fr.paste(panel(fn,act,sh,f'{i+39}. {nm}'+(' · 1/2 슬로우' if slow>1 else '')).convert('RGB'),((i%4)*360,(i//4)*270))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
