# recreation of the reference '20 skills sheet' (01 대지의 수정 .. 20 일식 검무) on the hero cast clip
import sys,os,math,random,importlib.util
from PIL import Image,ImageDraw,ImageFilter
sp=importlib.util.spec_from_file_location('G','skills/gen.py');G=importlib.util.module_from_spec(sp);sp.loader.exec_module(G)
W,H,HX,GY,HAND,TG,TC,REL=G.W,G.H,G.HX,G.GY,G.HAND,G.TG,G.TC,G.REL
glow,burst,ring,bolt,flames,Lr=G.glow_circle,G.burst,G.ring,G.bolt,G.flames,G.L
def crystal(d,x,y,h,al,col=(150,245,235),edge=(60,170,170)):
    w=h*.28;A=int(255*al);d.polygon([(x,y),(x-w,y-h*.75),(x,y-h),(x+w,y-h*.75)],fill=(*col,A),outline=(*edge,A));d.line([x,y-h,x,y],fill=(235,255,250,A))
def crescent(lay,x,y,R,ang,span,col,al,th=10,sq=1):
    g=Image.new('RGBA',(W,H));d=ImageDraw.Draw(g);A=int(255*al)
    for k in range(int(th)):
        r=R-k*.8;c=tuple(int(col[i]+(255-col[i])*(1-k/th)) for i in range(3))
        d.arc([x-r,y-r*sq,x+r,y+r*sq],ang-span/2+k*2,ang+span/2-k*2,fill=(*c,A),width=2)
    lay.alpha_composite(g)
def s01(l,t,r):   # 대지의 수정: crystal pillars erupt around the targets
    d=ImageDraw.Draw(l)
    if t<0:return {}
    hit={}
    for i,(x,y) in enumerate(TG):
        a=t-i*3
        if a<0:continue
        al=1 if a<26 else max(0,1-(a-26)/8);ring(d,x,GY,14+min(a,6)*4,(120,255,160),al,2)
        for k,(dx,h) in enumerate(((-16,30),(14,38),(-4,48),(22,24),(-24,22))):hh=h*min(1,(a-k*.5)/4) if a>k*.5 else 0;crystal(d,x+dx,GY+2,hh,al)
        if a<12:hit[i]=(160,255,230)
    return {'hit':hit}
def s02(l,t,r):   # 수정 실: a white crystal stream pours from the hand to the targets
    d=ImageDraw.Draw(l)
    if t<0:glow(l,*HAND,2+(t+REL)*.3,(200,250,255));return {}
    a=min(1,t/8);al=1 if t<24 else max(0,1-(t-24)/8);x1=HAND[0]+(TC[2][0]+20-HAND[0])*a
    g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g)
    for k in range(3):
        pts=[(x,HAND[1]+(GY-30-HAND[1])*((x-HAND[0])/max(1,TC[2][0]-HAND[0]))+math.sin(x*.08+t*.6+k*2)*(6+k*3)) for x in range(int(HAND[0]),int(x1),3)]
        if len(pts)>1:dg.line(pts,fill=(220,250,255,int((200-k*50)*al)),width=6-k*2)
    l.alpha_composite(g.filter(ImageFilter.GaussianBlur(1)));burst(d,x1,GY-30,t%8,10,(230,255,255),3,t//8,2)
    return {'hit':{i:(210,250,255) for i,(x,y) in enumerate(TG) if x<x1}}
def s03(l,t,r):   # 사중 참선: four quick slash marks on each target + sand cloud
    d=ImageDraw.Draw(l)
    if t<0:return {}
    hit={}
    for k in range(4):
        a=t-k*3
        if a<0 or a>10:continue
        for i,(x,y) in enumerate(TC):
            ang=[-.6,.6,0,1.57][k];L=22*min(1,(a+1)/2);c,s=math.cos(ang),math.sin(ang);A=int(255*(1-a/10))
            d.line([x-c*L,y-s*L,x+c*L,y+s*L],fill=(255,240,200,A),width=3);d.line([x-c*L,y-s*L,x+c*L,y+s*L],fill=(255,255,255,A),width=1);hit[i]=(255,230,180)
    for i,(x,y) in enumerate(TG):
        for k in range(8):rr=random.Random(i*9+k);px=x+rr.uniform(-30,30);rad=4+t*.4;al=max(0,1-t/30);d.ellipse([px-rad,GY-rad*.6-t*.3,px+rad,GY+rad*.6-t*.3],fill=(190,160,110,int(120*al)))
    return {'hit':hit}
def s04(l,t,r):   # 망자의 계약: pink pact circle, a wraith rises and drains the targets
    d=ImageDraw.Draw(l)
    if t<0:ring(d,HX,GY,20+(t+REL)*2,(255,150,230),1,2);return {}
    al=1 if t<30 else max(0,1-(t-30)/10);R=70
    ring(d,HX+60,GY,R,(255,160,235),al,2);ring(d,HX+60,GY,R*.75,(255,200,245),al,1)
    for k in range(5):an=math.radians(k*144+t*3);d.line([HX+60+math.cos(an)*R,GY+math.sin(an)*R*.35,HX+60+math.cos(an+math.radians(144))*R,GY+math.sin(an+math.radians(144))*R*.35],fill=(255,170,240,int(220*al)))
    gx,gy=TC[1][0],TC[1][1]-30-min(t,12)*2;g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);dg.ellipse([gx-10,gy-14,gx+10,gy+12],fill=(200,150,255,int(170*al)));dg.polygon([(gx-10,gy+4),(gx,gy+26+math.sin(t*.5)*3),(gx+10,gy+4)],fill=(200,150,255,int(140*al)));l.alpha_composite(g.filter(ImageFilter.GaussianBlur(2)))
    for i,(x,y) in enumerate(TC):
        if t>8 and t%4<2:d.line([x,y,HX+10,GY-60],fill=(230,140,255,int(120*al)),width=1)
    return {'hit':{i:(220,150,255) for i in range(3)} if t>8 else {}}
def s05(l,t,r):   # 해류의 숨결: a cone of rushing water + splash
    d=ImageDraw.Draw(l)
    if t<0:glow(l,*HAND,2+(t+REL)*.3,(80,170,255));return {}
    al=1 if t<20 else max(0,1-(t-20)/8)
    for k in range(40):
        rr=random.Random(k);s=(t*rr.uniform(6,10)+rr.uniform(0,40))%170;ang=rr.uniform(-.22,.22);x=HAND[0]+math.cos(ang)*s;y=HAND[1]+math.sin(ang)*s+s*.25;rad=1.5+s*.02
        d.ellipse([x-rad*1.6,y-rad,x+rad*1.6,y+rad],fill=(120,200,255,int(230*al)) if k%3 else (240,255,255,int(255*al)))
    for i,(x,y) in enumerate(TC):
        if t>4:burst(d,x,y,(t-4)%10,8,(200,240,255),3,i+t//10,2,.1)
    return {'hit':{i:(80,170,255) for i in range(3)} if t>4 else {}}
def s06(l,t,r):   # 산호 방패: pink coral sphere barrier
    if t<0:return {}
    a=Lr(t,0,6);al=1 if t<32 else max(0,1-(t-32)/10);cx,cy=HX+4,GY-58;R=62*a
    g=Image.new('RGBA',(W,H));d=ImageDraw.Draw(g);d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(255,170,200,int(70*al)),outline=(255,220,235,int(240*al)),width=3)
    for k in range(-2,3):
        d.ellipse([cx-R*abs(math.cos(k*.5)),cy-R,cx+R*abs(math.cos(k*.5)),cy+R],outline=(255,190,220,int(110*al)))
        yy=cy+k*R*.38;w=R*math.sqrt(max(0,1-(k*.38)**2));d.line([cx-w,yy,cx+w,yy],fill=(255,190,220,int(110*al)))
    l.alpha_composite(g);return {}
def s07(l,t,r):   # 업화의 검: hellfire pillars + a huge red crescent
    d=ImageDraw.Draw(l)
    if t<0:return {}
    al=1 if t<28 else max(0,1-(t-28)/10)
    for k in range(7):
        x=HX+40+k*26;h=min(1,(t-k)/5)*(50+math.sin(t*.7+k)*10) if t>k else 0
        if h>0:flames(d,x,GY,h,t+k,random.Random(k+t//3),al,7)
    if 6<=t<22:crescent(l,TC[2][0]-10,GY-60,52,0,150,(255,60,20),1-(t-6)/16,12)
    return {'hit':{i:(255,120,40) for i in range(3)} if t>6 else {}}
def s08(l,t,r):   # 뇌광 질주: lightning dash through the targets
    d=ImageDraw.Draw(l)
    if t<0:return {}
    dx=min(1,t/6)*270;x=HX+dx
    if t<14:
        for k in range(3):bolt(d,(HX,GY-50+k*12),(x,GY-50+k*12),random.Random(t*5+k),(150,210,255),2,int(255*(1-t/14)),6)
    burst(d,x,GY-50,t,14,(230,245,255),3,1,2)
    return {'dx':dx,'hit':{i:(220,240,255) for i,(tx,ty) in enumerate(TG) if tx<x and t<20}}
def s09(l,t,r):   # 시간 정지: clock rings, grey world, frozen targets
    d=ImageDraw.Draw(l)
    if t<0:return {}
    al=1 if t<34 else max(0,1-(t-34)/10);cx,cy=HX+120,GY-50
    for k,R in enumerate((40,70,100,135)):
        Rr=R*min(1,t/8);d.ellipse([cx-Rr,cy-Rr*.75,cx+Rr,cy+Rr*.75],outline=(255,255,255,int(220*al)) if k%2==0 else (30,30,30,int(200*al)),width=6 if k==3 else 3)
        for m in range(12):an=m*.5236;d.line([cx+math.cos(an)*Rr*.92,cy+math.sin(an)*Rr*.69,cx+math.cos(an)*Rr,cy+math.sin(an)*Rr*.75],fill=(255,255,255,int(200*al)),width=2)
    ah=math.radians(-90+t*2);d.line([cx,cy,cx+math.cos(ah)*60,cy+math.sin(ah)*45],fill=(255,240,180,int(255*al)),width=3);d.line([cx,cy,cx+math.cos(ah*3)*35,cy+math.sin(ah*3)*26],fill=(255,240,180,int(255*al)),width=2)
    return {'hit':{i:(160,160,160) for i in range(3)} if t>6 else {},'flash':(120,120,120,int(70*al)) if t>4 else None}
def s10(l,t,r):   # 삼룡의 각성: three dragon beams (pink/white) converge, giant light column
    d=ImageDraw.Draw(l)
    if t<0:glow(l,*HAND,2+(t+REL)*.35,(255,150,220));return {}
    al=1 if t<26 else max(0,1-(t-26)/10)
    for k in range(3):
        a=t-k*2
        if a<0:continue
        pts=[(HAND[0]+s,HAND[1]-20*k+math.sin(s*.05+t*.4+k*2)*14*(1-s/260)+(TC[1][1]-HAND[1]+20*k)*s/260) for s in range(0,int(min(1,a/8)*260),4)]
        if len(pts)>1:d.line(pts,fill=(255,140+k*40,220,int(230*al)),width=6-k);d.line(pts,fill=(255,255,255,int(255*al)),width=2)
    if t>8:x=TC[1][0]+60;g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);dg.rectangle([x-14,0,x+14,GY],fill=(255,170,230,int(160*al)));l.alpha_composite(g.filter(ImageFilter.GaussianBlur(6)));d.rectangle([x-4,0,x+4,GY],fill=(255,255,255,int(230*al)))
    return {'hit':{i:(255,170,230) for i in range(3)} if t>8 else {}}
def s11(l,t,r):   # 월광참: three moonlit crescents fly forward
    hit={}
    if t<0:return {}
    for k in range(3):
        a=t-k*4
        if a<0 or a>22:continue
        x=HAND[0]+a*11;al=1 if a<14 else max(0,1-(a-14)/8);crescent(l,x,GY-50,34,0,140,(110,190,255),al,9)
        for i,(tx,ty) in enumerate(TG):
            if abs(tx-x-20)<24:hit[i]=(170,220,255)
    return {'hit':hit}
def s12(l,t,r):   # 서리 송곳: ice spires burst out of the ground under the targets
    d=ImageDraw.Draw(l)
    if t<0:return {}
    hit={}
    for i,(x,y) in enumerate(TG):
        a=t-2-i*2
        if a<0:continue
        al=1 if a<22 else max(0,1-(a-22)/8)
        for k,(dx,h) in enumerate(((-14,34),(0,52),(14,40),(-24,22),(24,26))):crystal(d,x+dx,GY+2,h*min(1,a/3),al,(220,245,255),(110,170,230))
        ring(d,x,GY,10+min(a,8)*3,(200,240,255),al,2);hit[i]=(190,235,255)
    return {'hit':hit}
def s13(l,t,r):   # 성운 소용돌이: nebula vortex pulls the targets
    d=ImageDraw.Draw(l)
    if t<0:return {}
    cx,cy=TC[1][0],TC[1][1]-6;al=1 if t<30 else max(0,1-(t-30)/10);g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g)
    for k in range(5):
        R=10+k*10;ph=t*20*(1+k*.2);dg.arc([cx-R,cy-R*.6,cx+R,cy+R*.6],ph,ph+220,fill=(150+k*20,100+k*25,255,int(200*al)),width=4)
    l.alpha_composite(g.filter(ImageFilter.GaussianBlur(1)))
    for k in range(14):rr=random.Random(k);an=rr.uniform(0,6.28)+t*.25;dd=60-((t*3+k*5)%60);x=cx+math.cos(an)*dd;y=cy+math.sin(an)*dd*.6;d.line([x-2,y,x+2,y],fill=(255,255,220,int(240*al)));d.line([x,y-2,x,y+2],fill=(255,255,220,int(240*al)))
    return {'hit':{i:(170,130,255) for i in range(3)} if t>4 else {}}
def s14(l,t,r):   # 섬영: phantom step — blink forward, a huge blue crescent sweeps around
    d=ImageDraw.Draw(l)
    if t<0:return {}
    dx=90 if t>=4 else 0
    if t<6:burst(d,HX,GY-60,t,16,(180,220,255),3.5,2,2)
    if 4<=t<22:a=(t-4)/18;crescent(l,HX+dx+10,GY-50,70,-60+a*240,200,(110,190,255),1-a*.8,14,.8)
    return {'dx':dx,'heroal':0 if 1<=t<4 else 1,'hit':{i:(170,220,255) for i in range(3)} if 6<=t<20 else {}}
def s15(l,t,r):   # 별똥 낙인: shooting stars fall and brand the ground
    d=ImageDraw.Draw(l)
    if t<0:return {}
    hit={}
    for k in range(6):
        a=t-k*2;tx,ty=TG[k%3];tx+=(k//3)*18-9
        if a<0:continue
        if a<8:u=a/8;x=tx+80*(1-u);y=GY-20-180*(1-u);glow(l,x,y,6,(255,240,150));d.line([x,y,x+30,y-60],fill=(255,240,170,180),width=2)
        else:
            b=a-8;al=max(0,1-b/16);ring(d,tx,GY,10+min(b,4)*3,(255,230,140),al,2)
            for m in range(5):an=math.radians(m*144-90);an2=math.radians((m+2)*144-90);R=12;d.line([tx+math.cos(an)*R,GY+math.sin(an)*R*.35,tx+math.cos(an2)*R,GY+math.sin(an2)*R*.35],fill=(255,230,140,int(255*al)),width=1)
            hit[k%3]=(255,235,150)
    return {'hit':hit}
def s16(l,t,r):   # 백야의 창광: a long white lance beam
    d=ImageDraw.Draw(l)
    if t<0:glow(l,*HAND,2+(t+REL)*.4,(230,245,255));return {}
    L=min(1,t/4)*300;al=1 if t<18 else max(0,1-(t-18)/8);y=HAND[1]+6
    g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);dg.rectangle([HAND[0],y-9,HAND[0]+L,y+9],fill=(150,200,255,int(150*al)));l.alpha_composite(g.filter(ImageFilter.GaussianBlur(4)))
    d.rectangle([HAND[0],y-3,HAND[0]+L,y+3],fill=(255,255,255,int(255*al)))
    for k in range(4):rx=HAND[0]+L*(.25+.2*k);rr=12-k*2+t*.4;d.ellipse([rx-rr*.3,y-rr,rx+rr*.3,y+rr],outline=(220,240,255,int(220*al)),width=1)
    return {'hit':{i:(230,245,255) for i in range(3)} if t>3 and t<20 else {}}
def s17(l,t,r):   # 폭풍 칼날: green wind blades spiral outward around the hero
    hit={}
    if t<0:return {}
    al=1 if t<28 else max(0,1-(t-28)/8)
    for k in range(6):
        an=k*60+t*14;R=26+t*3.2;x=HX+20+math.cos(math.radians(an))*R;y=GY-40+math.sin(math.radians(an))*R*.45
        crescent(l,x,y,13,an+90,150,(110,230,160),al,6)
        for i,(tx,ty) in enumerate(TC):
            if math.hypot(tx-x,ty-y)<20:hit[i]=(170,255,200)
    return {'hit':hit}
def s18(l,t,r):   # 가시나무 결박: thorn vines rise and bind the targets, then a green slash
    d=ImageDraw.Draw(l)
    if t<0:return {}
    al=1 if t<30 else max(0,1-(t-30)/10)
    for i,(x,y) in enumerate(TG):
        for k in range(4):
            h=min(1,t/8)*(26+k*4);pts=[(x-14+k*9+math.sin(j*.6+k)*5,GY-j*h/8) for j in range(9)]
            d.line(pts,fill=(60,140,50,int(255*al)),width=3)
            for j in range(1,8,2):px,py=pts[j];d.polygon([(px,py),(px+4,py-2),(px,py-4)],fill=(150,220,90,int(255*al)))
    if 8<=t<20:crescent(l,TC[1][0],GY-40,60,0,140,(170,255,90),1-(t-8)/12,9)
    return {'hit':{i:(140,220,90) for i in range(3)} if t>4 else {}}
def s19(l,t,r):   # 연쇄 뇌창: a lightning spear hits the first target and chains on
    d=ImageDraw.Draw(l)
    if t<0:return {}
    hit={}
    if t<6:
        x=HAND[0]+(TC[0][0]-HAND[0])*t/6;y=HAND[1]+(TC[0][1]-HAND[1])*t/6;d.line([x-30,y-3,x,y],fill=(255,250,170,255),width=4);d.polygon([(x+8,y),(x,y-5),(x,y+5)],fill=(255,255,230,255))
    seq=TC
    for i in range(3):
        a=t-6-i*4
        if 0<=a<9:
            p0=seq[i-1] if i else (TC[0][0]-20,TC[0][1]);bolt(d,p0,seq[i],random.Random(t*3+i),(255,240,120),2,int(255*(1-a/9)));glow(l,*seq[i],10,(255,240,140),1-a/9);hit[i]=(255,245,170)
    return {'hit':hit}
def s20(l,t,r):   # 일식 검무: eclipse disc + white-gold rings and whirling slashes
    d=ImageDraw.Draw(l)
    if t<0:return {}
    al=1 if t<30 else max(0,1-(t-30)/10);cx,cy=HX+95,GY-55
    g=Image.new('RGBA',(W,H));dg=ImageDraw.Draw(g);R=30+min(t,10)*4;dg.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(255,240,190,int(150*al)));l.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
    d.ellipse([cx-R*.6,cy-R*.6,cx+R*.6,cy+R*.6],fill=(20,10,30,int(230*al)),outline=(255,250,220,int(255*al)),width=2)
    for k in range(3):crescent(l,cx,cy,R+14+k*10,t*30+k*120,120,(255,230,160),al,7,.8)
    return {'hit':{i:(255,240,190) for i,(tx,ty) in enumerate(TG) if tx-cx<R+50} if t>4 else {}}
G.SK=[('01 대지의 수정',s01),('02 수정 실',s02),('03 사중 참선',s03),('04 망자의 계약',s04),('05 해류의 숨결',s05),('06 산호 방패',s06),('07 업화의 검',s07),('08 뇌광 질주',s08),('09 시간 정지',s09),('10 삼룡의 각성',s10),
      ('11 월광참',s11),('12 서리 송곳',s12),('13 성운 소용돌이',s13),('14 섬영',s14),('15 별똥 낙인',s15),('16 백야의 창광',s16),('17 폭풍 칼날',s17),('18 가시나무 결박',s18),('19 연쇄 뇌창',s19),('20 일식 검무',s20)]
def panel(i,f):
    p=G.panel(i,f);d=ImageDraw.Draw(p);d.rectangle([0,0,140,18],fill=(0,0,0,0));return p
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);n=0
    for slow in (1,2):
        for f in range(REL+G.LEN):
            fr=Image.new('RGB',(1440,604))
            for i in range(20):fr.paste(G.panel(i,f).convert('RGB'),((i%5)*288,(i//5)*151))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
