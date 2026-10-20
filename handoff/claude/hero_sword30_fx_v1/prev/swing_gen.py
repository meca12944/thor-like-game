# sword-SWING effects: a phantom blade sweeps around the hand, leaving a swept smear (bright leading edge, fading tail),
# blade afterimages, tip sparks, impact burst. 6 styles x 3 hits.
import sys,os,math,random,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
IDLE=Image.open('/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/east/000.png').convert('RGBA')
W,H=440,300;OX,OY=40,30;PX,PY=OX+132,OY+118     # pivot = sword hand
Y,X=np.mgrid[0:H,0:W].astype(float)
def ease(t):return 1-(1-t)**3
def smear(a0,a1,head,tail,r1,r2,sq,pal,edge=True,rings=0):
    """swept annular sector from angle a0 to a1 (deg, screen, y down); visible part tail..head (0..1 of the sweep)"""
    dx=X-PX;dy=(Y-PY)/sq;r=np.hypot(dx,dy);th=np.degrees(np.arctan2(dy,dx))
    sgn=1 if a1>a0 else -1;u=((th-a0)*sgn)%360/abs(a1-a0)        # 0..1 progress along the sweep
    tail=max(tail,head-115/abs(a1-a0))                             # trail never longer than ~115 deg
    vis=(u>=tail)&(u<=head)&(r>=r1)&(r<=r2);k=np.clip((u-tail)/max(head-tail,1e-3),0,1);rr=np.clip((r-r1)/(r2-r1),0,1)
    o=np.zeros((H,W,4));core,mid,glow=[np.array(c,float) for c in pal]
    w=k**2.2*rr**1.3                                                 # ribbon: bright at the tip radius and the leading edge                                          # brighter toward the leading edge and the blade tip
    col=np.where((w>.55)[...,None],mid+(core-mid)*((w-.55)/.45)[...,None],glow+(mid-glow)*(w/.55)[...,None])
    o[vis,:3]=col[vis];o[vis,3]=np.clip(255*np.minimum(1,w*1.6),0,255)[vis]
    if rings:
        for q in range(rings):
            rq=r1+(r2-r1)*(.45+.18*q);m=vis&(np.abs(r-rq)<.8);o[m,:3]=core;o[m,3]=np.maximum(o[m,3],150*k[m])
    if edge:m=vis&(k>.93)&(rr>.3);o[m,:3]=core;o[m,3]=255
    m=vis&(rr>.94)&(k>.2);o[m,:3]=core;o[m,3]=np.maximum(o[m,3],220*k[m])   # crisp outer rim
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
def blade(d,ang,r1,r2,sq,al,col=(235,240,250),edge=(120,130,150)):
    c,s=math.cos(math.radians(ang)),math.sin(math.radians(ang));p=lambda r,o=0:(PX+c*r-s*o,PY+(s*r+c*o)*sq)
    d.polygon([p(r1,-3),p(r2-8,-2.5),p(r2+2,0),p(r2-8,2.5),p(r1,3)],fill=(*col,al),outline=(*edge,al))
    d.line([p(r1-4,-6),p(r1-4,6)],fill=(200,160,60,al),width=2)
STY=[dict(nm='청백 스윙',pal=((255,255,255),(140,215,255),(40,100,240)),sp=(220,245,255)),
     dict(nm='황금 대검',pal=((255,252,220),(255,205,90),(200,110,20)),sp=(255,220,120),wide=1.35,dust=1),
     dict(nm='잔광 블레이드',pal=((255,255,255),(170,225,255),(70,120,240)),sp=(230,250,255),ghost=4),
     dict(nm='진홍 쌍격',pal=((255,235,235),(255,90,100),(150,10,40)),sp=(255,150,150),twin=1),
     dict(nm='염화 휘두르기',pal=((255,255,210),(255,150,40),(210,40,0)),sp=(255,200,80),ember=1),
     dict(nm='심연 휘두르기',pal=((235,200,255),(150,70,230),(30,0,60)),sp=(200,140,255),dark=1)]
# hits: start/end angle (deg, 0 = forward/right, -90 = up), sweep frames, r1, r2(blade length), squash
HITS=[(-120,40,5,30,82,.55),(70,-110,5,30,84,.7),(-150,95,7,30,104,1.0)]
LIFE=16
def draw(spr,st,n,a,seed):
    a0,a1,D,r1,r2,sq=HITS[n];r2*=st.get('wide',1);t=min(1,(a+1)/D);head=ease(t);tail=0 if a<D+1 else min(1,(a-D-1)/6)
    ang=a0+(a1-a0)*head;lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    if st.get('dark') and tail<head:
        g=smear(a0,a1,head,tail,r1-4,r2+6,sq,((60,0,80),(40,0,60),(20,0,30)),edge=False).filter(ImageFilter.GaussianBlur(3));lay.alpha_composite(g)
    if tail<head:lay.alpha_composite(smear(a0,a1,head,tail,r1,r2,sq,st['pal'],rings=0))
    if st.get('twin') and a>=2:
        b=a-2;t2=min(1,(b+1)/D);h2=ease(t2);tl2=0 if b<D+1 else min(1,(b-D-1)/6)
        if tl2<h2:lay.alpha_composite(smear(a1,a0,h2,tl2,r1+6,r2*.85,sq,st['pal']))
    if st.get('ghost') and a<D+2:
        for g in range(1,st['ghost']+1):
            gh=ease(max(0,t-g*.12));blade(d,a0+(a1-a0)*gh,r1,r2,sq,int(110/g))
    if a<D+3:blade(d,ang,r1,r2,sq,255 if a<D+1 else int(255*(1-(a-D)/3)))
    rnd=random.Random(seed);c,s=math.cos(math.radians(ang)),math.sin(math.radians(ang));tx,ty=PX+c*r2,PY+s*r2*sq
    # tip sparks along the path
    for k in range(10 if n==2 else 6):
        h=rnd.uniform(max(0,head-.5),head);an=math.radians(a0+(a1-a0)*h);rr=r2*rnd.uniform(.9,1.08);x=PX+math.cos(an)*rr+rnd.uniform(-3,3)*a;y=PY+math.sin(an)*rr*sq+rnd.uniform(-3,3)*a*.6
        al=max(0,255-a*16);d.rectangle([x,y,x+1,y+1],fill=(*st['sp'],al))
    if st.get('ember'):
        for k in range(14):
            h=rnd.uniform(0,head);an=math.radians(a0+(a1-a0)*h);rr=rnd.uniform(r1,r2);x=PX+math.cos(an)*rr;y=PY+math.sin(an)*rr*sq-a*rnd.uniform(1,2.5);rd=max(1,3-a*.15)
            d.ellipse([x-rd,y-rd*1.4,x+rd,y+rd*1.4],fill=(255,rnd.choice((120,180,230)),40,max(0,255-a*15)))
    # impact burst when the swing completes
    b=a-D
    if 0<=b<8:
        al=int(255*(1-b/8));R=6+b*(5 if n==2 else 3.5);d.ellipse([tx-R,ty-R*.6,tx+R,ty+R*.6],outline=(*st['sp'],al),width=2)
        L=(16 if n==2 else 11)*(1-b/8)+2;d.line([tx-L,ty,tx+L,ty],fill=(255,255,255,al),width=2);d.line([tx,ty-L*.7,tx,ty+L*.7],fill=(255,255,255,al),width=1)
        if st.get('dust') and n==2:
            for k in range(8):x=tx+rnd.uniform(-30,30)+b*rnd.uniform(-2,2);y=OY+188-b*rnd.uniform(.5,1.5);r=3+b;d.ellipse([x-r,y-r*.6,x+r,y+r*.6],fill=(200,180,140,al//2))
    spr.alpha_composite(lay)
def panel(i,act,shake,lab):
    st=STY[i];spr=Image.new('RGBA',(W,H),(66,96,58,255));spr.alpha_composite(IDLE,(OX,OY))
    for s in act:draw(spr,st,s['n'],s['age'],s['n']*97+i)
    fl=max([0]+[(3-(s['age']-HITS[s['n']][2]))*(.1 if s['n']==2 else .04) for s in act if 0<=s['age']-HITS[s['n']][2]<3])
    if fl:spr.alpha_composite(Image.new('RGBA',spr.size,(255,255,255,int(255*fl))))
    p=spr.crop((60,10,410,290)).resize((480,384),Image.NEAREST);q=Image.new('RGBA',p.size,(66,96,58,255));q.alpha_composite(p,(round((random.random()*2-1)*shake*3),0))
    ImageDraw.Draw(q).text((8,6),lab,font=F,fill='white');return q
def timeline():
    T=[([],0)]*6;sh=0
    for n in range(3):
        D=HITS[n][2]
        for a in range(LIFE+(1 if n<2 else 10)):
            if a==D:sh=[1.5,2,4.5][n]
            T.append(([{'n':n,'age':a}] if a<LIFE else [],sh));sh=sh*.8 if sh>.3 else 0
    return T
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);TL=timeline();n=0
    for slow in (1,1,3):
        for act,sh in TL:
            fr=Image.new('RGB',(1440,768))
            for i,st in enumerate(STY):fr.paste(panel(i,act,sh,f'{i+33}. {st["nm"]}'+(' · 1/3 슬로우' if slow>1 else '')).convert('RGB'),((i%3)*480,(i//3)*384))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
