# every basic sword stroke (9 primitives) + all natural 3-hit chains between them (end zone of one = start zone of the next)
import sys,os,math,random,itertools,numpy as np
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16);FS=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
IDLE=Image.open('/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/east/000.png').convert('RGBA')
SL=Image.open('/home/user/thor-like-game/test128/sandbox/assets/slime.png').convert('RGBA').crop((0,0,86,78)).resize((52,47),Image.NEAREST)
W,H=360,250;OX,OY=0,10;HX,GY=OX+116,OY+190;PX,PY=HX+26,GY-70;EX=HX+112
Y,X=np.mgrid[0:H,0:W].astype(float)
ST=[(30,80,220),(70,160,255),(170,230,255),(255,255,255)]
def grad(w):
    n=len(ST)-1;f=np.clip(w,0,1)*n;i=np.minimum(n-1,f.astype(int));t=(f-i)[...,None];S=np.array(ST,float);return S[i]*(1-t)+S[i+1]*t
def smear(a0,a1,head,tail,r1,r2,sq,tilt,px=PX,py=PY):
    c,s=math.cos(math.radians(-tilt)),math.sin(math.radians(-tilt));dx0=X-px;dy0=Y-py;dx=dx0*c-dy0*s;dy=(dx0*s+dy0*c)/sq
    r=np.hypot(dx,dy);th=np.degrees(np.arctan2(dy,dx));sgn=1 if a1>a0 else -1;span=abs(a1-a0);u=((th-a0)*sgn)%360/span
    tail=max(tail,head-120/span);vis=(u>=tail)&(u<=head)&(r>=r1)&(r<=r2);k=np.clip((u-tail)/max(head-tail,1e-3),0,1);rr=np.clip((r-r1)/(r2-r1),0,1)
    w=k**2*rr**1.2;o=np.zeros((H,W,4));col=grad(w);o[vis,:3]=col[vis];o[vis,3]=np.clip(255*np.minimum(1,w*1.7),0,255)[vis]
    m=vis&(k>.92)&(rr>.3);o[m,:3]=255;o[m,3]=255;m=vis&(rr>.93)&(k>.25);o[m,:3]=255;o[m,3]=np.maximum(o[m,3],230*k[m])
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
# primitive: name, arrow, start zone, end zone, smear params (a0,a1,r1,r2,sq,tilt) or 'thrust', cut-mark angle on the enemy
P=[('내려베기','↓','T','B',(-100,80,26,92,1,0),90),
   ('올려베기','↑','B','T',(80,-100,26,92,1,0),90),
   ('가로베기','→','K','F',(165,15,30,108,.42,0),0),
   ('되베기','←','F','K',(15,165,30,108,.42,0),0),
   ('사선 내려베기','↘','TK','BF',(165,15,30,104,.42,35),35),
   ('역사선 내려베기','↙','TF','BK',(15,165,30,104,.42,-35),-35),
   ('사선 올려베기','↗','BK','TF',(165,15,30,104,.42,-35),-35),
   ('역사선 올려베기','↖','BF','TK',(15,165,30,104,.42,35),35),
   ('찌르기','▶','C','F','thrust',0)]
def link(e,s):  # next stroke can start where the last one ended: share a zone letter; thrust (C) can follow anything that ends in front
    if s=='C':return 'F' in e or e=='C'
    return bool(set(e)&set(s))
CHAINS=[c for c in itertools.product(range(9),repeat=3) if link(P[c[0]][3],P[c[1]][2]) and link(P[c[1]][3],P[c[2]][2])]
D=5;LIFE=13
def draw_stroke(img,i,a,mark=True):
    nm,ar,s0,e0,pr,cut=P[i];lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    if pr=='thrust':
        t=min(1,(a+1)/3);L=150*(1-(1-t)**3);al=1 if a<5 else max(0,1-(a-5)/6);x0,y0=PX-20,PY+6;A=int(255*al)
        ang=math.atan2((GY-24)-y0,EX-x0);c_,s_=math.cos(ang),math.sin(ang);q=lambda f,o:(x0+c_*f-s_*o,y0+s_*f+c_*o)
        d.polygon([q(0,-10),q(L,0),q(0,10)],fill=(60,140,255,A//2));d.polygon([q(0,-5),q(L,0),q(0,5)],fill=(170,230,255,A));d.line([q(0,0),q(L,0)],fill=(255,255,255,A),width=2)
        for k in range(3):
            cx_,cy_=q(L*(.4+.2*k),0);r=11-k*2+a*.6;d.ellipse([cx_-r*.35,cy_-r,cx_+r*.35,cy_+r],outline=(220,245,255,A),width=1)
    else:
        a0,a1,r1,r2,sq,tilt=pr;t=min(1,(a+1)/D);head=1-(1-t)**3;tail=0 if a<D+1 else min(1,(a-D-1)/5)
        if tail<head:img.alpha_composite(smear(a0,a1,head,tail,r1,r2,sq,tilt))
    # contact on the dummy: cut mark along the stroke + sparks
    b=a-(D-2)
    if mark and 0<=b<10:
        ex,ey=EX,GY-24;al=max(0,1-b/10);A=int(255*al);L=26*min(1,(b+1)/2);ca,sa=math.cos(math.radians(cut)),math.sin(math.radians(cut))
        if pr=='thrust':d.ellipse([ex-8-b,ey-8-b,ex+8+b,ey+8+b],outline=(220,245,255,A),width=2)
        else:d.line([ex-ca*L,ey-sa*L,ex+ca*L,ey+sa*L],fill=(130,210,255,A),width=3);d.line([ex-ca*L,ey-sa*L,ex+ca*L,ey+sa*L],fill=(255,255,255,A),width=1)
        rnd=random.Random(i)
        for k in range(10):g=rnd.uniform(0,6.28);sp=rnd.uniform(2,5);d.rectangle([ex+math.cos(g)*sp*b,ey+math.sin(g)*sp*b*.8,ex+math.cos(g)*sp*b+1,ey+math.sin(g)*sp*b*.8+1],fill=(255,240,150,A))
    img.alpha_composite(lay)
def scene(strokes,lab,sub=''):
    img=Image.new('RGBA',(W,H),(66,96,58,255));d=ImageDraw.Draw(img);d.ellipse([EX-16,GY-3,EX+16,GY+3],fill=(0,0,0,50))
    hit=any(0<=a-(D-2)<3 for i,a in strokes);sl=SL
    if hit:px=np.array(SL);px[...,:3]=np.where(px[...,3:]>0,255,px[...,:3]);sl=Image.fromarray(px)
    img.alpha_composite(sl,(EX-26,GY-47));img.alpha_composite(IDLE.crop((40,40,220,200)),(HX-88,GY-150))
    for i,a in strokes:draw_stroke(img,i,a)
    d=ImageDraw.Draw(img);d.text((6,4),lab,font=F,fill='white')
    if sub:d.text((6,24),sub,font=F,fill=(255,235,150))
    return img
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);n=0
    # part 1: the 9 primitives, each twice
    for rep in range(2):
        for a in range(LIFE+4):
            fr=Image.new('RGB',(1440,750))
            for i in range(9):fr.paste(scene([(i,a)] if a<LIFE else [],f'{P[i][1]} {P[i][0]}','기본 9동작').convert('RGB'),(180+(i%3)*360,(i//3)*250))
            for q in range(2):fr.save(f'{OUT}/{n:05d}.png');n+=1
    # part 2: sample chains (12 shown), full count in the label
    rnd=random.Random(5);pick=[]
    pref=[(0,1,8),(2,3,0),(4,7,8),(5,6,0),(2,5,6),(0,2,3),(1,4,8),(6,7,2),(3,4,1),(8,2,3),(4,6,0),(7,5,8)]
    for c in pref:
        if c in CHAINS:pick.append(c)
    while len(pick)<12:
        c=rnd.choice(CHAINS)
        if c not in pick:pick.append(c)
    G=9   # frames between strokes
    for rep in range(2):
        for f in range(G*2+LIFE+6):
            fr=Image.new('RGB',(1440,750))
            for j,c in enumerate(pick):
                act=[(c[k],f-k*G) for k in range(3) if 0<=f-k*G<LIFE]
                lab=f'콤보 {" ".join(P[k][1] for k in c)}';fr.paste(scene(act,lab,f'자연 연결 {len(CHAINS)}가지 중').convert('RGB').resize((360,250)),((j%4)*360,(j//4)*250))
            for q in range(2):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n,len(CHAINS))
