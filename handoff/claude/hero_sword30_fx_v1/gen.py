# 30 swords, each with a unique effect: own 3-hit combo (from the 178 natural chains), 4-tone smear palette, particle kind, hit burst.
import sys,os,math,random,colorsys,numpy as np,importlib.util
from PIL import Image,ImageDraw,ImageFont
sp=importlib.util.spec_from_file_location('S','strokes/gen.py');S=importlib.util.module_from_spec(sp);sp.loader.exec_module(S)
F=S.F;P=S.P;W,H=S.W,S.H;Y,X=S.Y,S.X;PX,PY,EX,GY,HX=S.PX,S.PY,S.EX,S.GY,S.HX
def grad(st,w):
    n=len(st)-1;f=np.clip(w,0,1)*n;i=np.minimum(n-1,f.astype(int));t=(f-i)[...,None];A=np.array(st,float);return A[i]*(1-t)+A[i+1]*t
def smear(a0,a1,head,tail,r1,r2,sq,tilt,st,prism=False,alpha=1.0):
    c,s=math.cos(math.radians(-tilt)),math.sin(math.radians(-tilt));dx0=X-PX;dy0=Y-PY;dx=dx0*c-dy0*s;dy=(dx0*s+dy0*c)/sq
    r=np.hypot(dx,dy);th=np.degrees(np.arctan2(dy,dx));sgn=1 if a1>a0 else -1;span=abs(a1-a0);u=((th-a0)*sgn)%360/span
    tail=max(tail,head-120/span);vis=(u>=tail)&(u<=head)&(r>=r1)&(r<=r2);k=np.clip((u-tail)/max(head-tail,1e-3),0,1);rr=np.clip((r-r1)/(r2-r1),0,1)
    w=k**2*rr**1.2;o=np.zeros((H,W,4))
    if prism:hue=(u*1.3)%1;rgb=np.array([colorsys.hsv_to_rgb(h,.7,1) for h in np.linspace(0,1,64)])*255;col=rgb[(hue*63).astype(int)];col=col+(255-col)*np.clip((w-.6)/.4,0,1)[...,None]
    else:col=grad(st,w)
    o[vis,:3]=col[vis];o[vis,3]=np.clip(255*alpha*np.minimum(1,w*1.7),0,255)[vis]
    m=vis&(k>.92)&(rr>.3);o[m,:3]=st[-1];o[m,3]=255*alpha;m=vis&(rr>.93)&(k>.25);o[m,:3]=st[-1];o[m,3]=np.maximum(o[m,3],230*alpha*k[m])
    return Image.fromarray(o.clip(0,255).astype(np.uint8)),(u,vis)
def part(d,kind,x,y,t,rnd,c1,c2,A):
    """one particle of a given kind at age t"""
    g=rnd.uniform(0,6.28);sp=rnd.uniform(1.5,4.5);x+=math.cos(g)*sp*t;y+=math.sin(g)*sp*t*.7;a=A
    if kind=='spark':d.rectangle([x,y,x+1,y+1],fill=(*c1,a))
    elif kind=='star':L=3-t*.15;d.line([x-L,y,x+L,y],fill=(*c1,a));d.line([x,y-L,x,y+L],fill=(*c1,a))
    elif kind=='ember':y-=t*1.6;r=max(.8,2.5-t*.15);d.ellipse([x-r,y-r*1.4,x+r,y+r*1.4],fill=(*(c1 if rnd.random()<.5 else c2),a))
    elif kind=='shard':s=3;d.polygon([(x,y-s*1.7),(x+s*.6,y),(x,y+s*1.7),(x-s*.6,y)],fill=(*c1,a),outline=(*c2,a))
    elif kind=='bolt':
        if t<6:pts=[(x,y)];[pts.append((pts[-1][0]+rnd.uniform(-6,6),pts[-1][1]+rnd.uniform(-6,6))) for _ in range(3)];d.line(pts,fill=(*c1,a),width=1)
    elif kind=='drop':y+=t*t*.15;d.ellipse([x-1.5,y-2,x+1.5,y+2],fill=(*c1,a))
    elif kind=='bubble':y-=t*1.1;r=rnd.uniform(1.5,3.5);d.ellipse([x-r,y-r,x+r,y+r],outline=(*c1,a))
    elif kind=='smoke':y-=t*.5;r=2+t*.6;d.ellipse([x-r,y-r,x+r,y+r],fill=(*c2,int(a*.5)))
    elif kind=='ray':L=6+t*3;d.line([x,y,x+math.cos(g)*L,y+math.sin(g)*L],fill=(*c1,int(a*.8)))
    elif kind=='leaf':y+=t*.4+math.sin(t*.8+g)*2;d.ellipse([x-3,y-1.5,x+3,y+1.5],fill=(*c1,a))
    elif kind=='sand':y+=t*.6;d.point((x,y),fill=(*c1,a));d.point((x+1,y+1),fill=(*c2,a))
    elif kind=='petal':y+=t*.5+math.sin(t*.6+g)*1.5;d.ellipse([x-2.5,y-1.5,x+2.5,y+1.5],fill=(*c1,a))
    elif kind=='blood':y+=t*t*.2;d.ellipse([x-1.5,y-1.5,x+1.5,y+2.5],fill=(*c1,a))
    elif kind=='prism':c=tuple(int(v*255) for v in colorsys.hsv_to_rgb(rnd.random(),.7,1));d.rectangle([x,y,x+1,y+1],fill=(*c,a))
    elif kind=='scale':d.arc([x-3,y-3,x+3,y+3],200,340,fill=(*c1,a),width=1)
    elif kind=='rock':y+=t*t*.18;s=2;d.rectangle([x-s,y-s,x+s,y+s],fill=(*c2,a));d.point((x,y),fill=(*c1,a))
    elif kind=='snow':L=2.5;d.line([x-L,y,x+L,y],fill=(*c1,a));d.line([x,y-L,x,y+L],fill=(*c1,a));d.line([x-L*.7,y-L*.7,x+L*.7,y+L*.7],fill=(*c1,a))
    elif kind=='feather':y+=t*.3;d.line([x-3,y+2,x+3,y-2],fill=(*c1,a),width=1);d.point((x+3,y-2),fill=(*c2,a))
    elif kind=='wisp':y-=t*.8;r=2+t*.3;d.ellipse([x-r,y-r,x+r,y+r],outline=(*c1,int(a*.6)))
    elif kind=='flare':r=2+t*1.2;d.ellipse([x-r,y-r,x+r,y+r],outline=(*c1,int(a*.5)))
    elif kind=='glyph':d.arc([x-3,y-3,x+3,y+3],60,300,fill=(*c1,a),width=1)
    elif kind=='rune':d.rectangle([x-2,y-2,x+2,y+2],outline=(*c1,a));d.point((x,y),fill=(*c2,a))
    elif kind=='butterfly':f=abs(math.sin(t*.9+g))*3+1;y-=t*.4;d.polygon([(x,y),(x-f,y-3),(x-f,y+2)],fill=(*c1,a));d.polygon([(x,y),(x+f,y-3),(x+f,y+2)],fill=(*c2,a))
    elif kind=='dust':y-=t*.2;r=2+t*.5;d.ellipse([x-r,y-r*.6,x+r,y+r*.6],fill=(*c1,int(a*.45)))
    elif kind=='streak':L=8;d.line([x-L,y,x+L*.3,y],fill=(*c1,int(a*.8)))
    elif kind=='mist':r=3+t*.8;d.ellipse([x-r,y-r,x+r,y+r],fill=(*c1,int(a*.25)))
# name, palette stops (glow..core), particle, accent colours, hit ring colour, specials
SW=[('철검',[(40,70,200),(90,170,255),(190,235,255),(255,255,255)],'spark',(255,240,160),(150,200,255),{}),
    ('은월검',[(60,60,110),(150,160,200),(220,225,245),(255,255,255)],'glyph',(230,235,255),(170,180,230),{}),
    ('홍련검',[(120,0,0),(240,60,10),(255,180,40),(255,255,220)],'ember',(255,200,60),(255,80,20),{}),
    ('빙백검',[(40,90,170),(120,200,255),(210,245,255),(255,255,255)],'shard',(230,250,255),(120,190,255),{'freeze':1}),
    ('뇌명검',[(30,30,170),(70,150,255),(255,240,90),(255,255,255)],'bolt',(255,250,140),(120,220,255),{}),
    ('수룡검',[(0,40,120),(20,120,220),(110,210,255),(240,255,255)],'drop',(160,230,255),(60,150,255),{'ripple':1}),
    ('독사검',[(40,0,60),(120,30,170),(110,220,60),(230,255,190)],'bubble',(150,255,80),(190,90,255),{}),
    ('흑요검',[(10,0,20),(70,20,90),(170,90,200),(240,220,255)],'smoke',(220,160,255),(30,0,40),{}),
    ('성광검',[(160,110,20),(255,210,90),(255,245,190),(255,255,255)],'ray',(255,245,190),(255,220,120),{}),
    ('풍신검',[(20,120,90),(90,220,170),(210,255,235),(255,255,255)],'leaf',(140,230,120),(200,255,220),{}),
    ('사막검',[(110,70,20),(200,150,70),(250,220,150),(255,250,230)],'sand',(240,210,140),(170,120,60),{}),
    ('벚꽃검',[(170,40,100),(255,140,190),(255,215,230),(255,255,255)],'petal',(255,180,210),(255,120,170),{}),
    ('혈검',[(60,0,10),(180,10,30),(255,80,90),(255,230,230)],'blood',(200,20,40),(255,90,100),{}),
    ('금강검',[(80,80,120),(200,220,255),(255,255,255),(255,255,255)],'prism',(255,255,255),(200,220,255),{}),
    ('성운검',[(30,10,80),(120,60,220),(80,200,255),(255,255,255)],'star',(255,255,200),(150,120,255),{}),
    ('용린검',[(20,80,60),(40,170,110),(240,210,90),(255,255,230)],'scale',(250,220,110),(60,200,140),{}),
    ('화산검',[(30,10,10),(120,30,10),(255,110,20),(255,230,150)],'rock',(255,150,40),(60,30,20),{}),
    ('서리꽃검',[(90,60,160),(200,140,230),(170,240,255),(255,255,255)],'snow',(235,250,255),(210,160,240),{}),
    ('천둥새검',[(80,30,160),(170,90,255),(255,235,90),(255,255,255)],'feather',(255,240,120),(190,120,255),{}),
    ('심해검',[(0,20,50),(0,90,110),(40,200,190),(220,255,250)],'bubble',(120,240,230),(20,120,140),{}),
    ('유령검',[(40,70,60),(120,190,160),(210,255,235),(255,255,255)],'wisp',(200,255,230),(140,220,190),{'ghost':1}),
    ('태양검',[(200,60,0),(255,150,20),(255,235,140),(255,255,255)],'flare',(255,220,120),(255,150,40),{}),
    ('월광검',[(20,30,90),(80,110,200),(190,210,255),(255,255,255)],'glyph',(210,225,255),(120,150,230),{}),
    ('마검',[(20,0,0),(120,0,20),(230,40,60),(255,210,210)],'rune',(255,60,80),(60,0,10),{'double':1}),
    ('수정검',[(90,20,110),(220,90,220),(255,200,250),(255,255,255)],'shard',(255,210,250),(220,90,220),{}),
    ('나비검',[(60,20,120),(140,90,240),(240,170,255),(255,255,255)],'butterfly',(200,150,255),(255,180,240),{}),
    ('강철대검',[(50,55,65),(130,140,155),(210,215,225),(255,255,255)],'dust',(190,170,140),(140,145,160),{'heavy':1}),
    ('바람칼날',[(20,110,140),(90,210,240),(220,250,255),(255,255,255)],'streak',(220,250,255),(120,220,240),{'double':1}),
    ('독안개검',[(20,50,10),(80,140,40),(170,230,90),(240,255,210)],'mist',(150,220,80),(90,160,50),{}),
    ('무지개검',[(0,0,0)]*3+[(255,255,255)],'prism',(255,255,255),(255,255,255),{'prism':1})]
# 30 distinct natural chains spread over the 178
CH=random.Random(30).sample(S.CHAINS,30)
D=5;LIFE=13;G=8
def scene(i,act):
    nm,st,kind,c1,c2,sp=SW[i];img=Image.new('RGBA',(W,H),(66,96,58,255));d=ImageDraw.Draw(img);d.ellipse([EX-16,GY-3,EX+16,GY+3],fill=(0,0,0,50))
    hit=any(0<=a-(D-2)<3 for _,a in act);fz=sp.get('freeze') and any(a-(D-2)>=0 for _,a in act)
    sl=S.SL;px=np.array(sl).astype(float)
    if fz:px[...,:3]=px[...,:3]*.45+np.array([190,235,255])*.55
    if hit:px[...,:3]=np.where(px[...,3:]>0,255,px[...,:3])
    img.alpha_composite(Image.fromarray(px.clip(0,255).astype(np.uint8)),(EX-26,GY-47));img.alpha_composite(S.IDLE.crop((40,40,220,200)),(HX-88,GY-150))
    lay=Image.new('RGBA',(W,H));dl=ImageDraw.Draw(lay)
    for k,(pi,a) in enumerate(act):
        pr=P[pi][4];rnd=random.Random(i*31+k)
        if pr=='thrust':
            t=min(1,(a+1)/3);L=150*(1-(1-t)**3);al=1 if a<5 else max(0,1-(a-5)/6);x0,y0=PX-20,PY+6;A=int(255*al);ang=math.atan2((GY-24)-y0,EX-x0);c_,s_=math.cos(ang),math.sin(ang);q=lambda f_,o:(x0+c_*f_-s_*o,y0+s_*f_+c_*o)
            g_,m_,c__=(st[1],st[2],st[3]) if not sp.get('prism') else ((255,90,90),(120,255,160),(255,255,255))
            dl.polygon([q(0,-10),q(L,0),q(0,10)],fill=(*g_,A//2));dl.polygon([q(0,-5),q(L,0),q(0,5)],fill=(*m_,A));dl.line([q(0,0),q(L,0)],fill=(*c__,A),width=2)
            for q2 in range(6):x,y=q(L*rnd.uniform(.3,1),rnd.uniform(-6,6));part(dl,kind,x,y,a*.6,rnd,c1,c2,max(0,255-a*18))
        else:
            a0,a1,r1,r2,sq,tilt=pr;sc=1.15 if sp.get('heavy') else 1;t=min(1,(a+1)/D);head=1-(1-t)**3;tail=0 if a<D+1 else min(1,(a-D-1)/5)
            if tail<head:
                im,_=smear(a0,a1,head,tail,r1,r2*sc,sq,tilt,st,sp.get('prism'),.55 if sp.get('ghost') else 1);img.alpha_composite(im)
                if sp.get('double'):im2,_=smear(a0,a1,max(0,head-.15),max(0,tail-.15) if tail>0 else 0,r1*.7,r2*.78,sq,tilt,st);img.alpha_composite(im2)
                for q in range(9):   # particles shed from the blade path
                    h=rnd.uniform(max(0,head-.5),head);an=math.radians(a0+(a1-a0)*h);rr=r2*rnd.uniform(.8,1.05);ct,stn=math.cos(math.radians(tilt)),math.sin(math.radians(tilt))
                    lx,ly=math.cos(an)*rr,math.sin(an)*rr*sq;x=PX+lx*ct-ly*stn;y=PY+lx*stn+ly*ct;part(dl,kind,x,y,a*.6,rnd,c1,c2,max(0,255-a*18))
        b=a-(D-2)
        if 0<=b<12:   # hit burst on the dummy in the sword's own particle + cut mark along the stroke
            ex,ey=EX,GY-24;A=int(255*max(0,1-b/12));cut=P[pi][5];ca,sa=math.cos(math.radians(cut)),math.sin(math.radians(cut));L=26*min(1,(b+1)/2)
            if pr!='thrust':dl.line([ex-ca*L,ey-sa*L,ex+ca*L,ey+sa*L],fill=(*c2,A),width=3);dl.line([ex-ca*L,ey-sa*L,ex+ca*L,ey+sa*L],fill=(255,255,255,A),width=1)
            else:dl.ellipse([ex-7-b,ey-7-b,ex+7+b,ey+7+b],outline=(*c2,A),width=2)
            if b<4:R=5+b*4;dl.ellipse([ex-R,ey-R,ex+R,ey+R],outline=(*c1,A),width=2)
            r2_=random.Random(i*7+k)
            for q in range(14):part(dl,kind,ex,ey,b,r2_,c1,c2,A)
            if sp.get('ripple') and b<10:rr=6+b*4;dl.ellipse([ex-rr,GY-rr*.25,ex+rr,GY+rr*.25],outline=(160,230,255,A),width=1)
            if sp.get('heavy') and b<8:
                for q in range(6):x=ex+r2_.uniform(-24,24);r=3+b;dl.ellipse([x-r,GY-r*.5-b*.5,x+r,GY+r*.5-b*.5],fill=(190,170,140,A//2))
    img.alpha_composite(lay);return img
def panel(i,f):
    c=CH[i];act=[(c[k],f-k*G) for k in range(3) if 0<=f-k*G<LIFE]
    im=scene(i,act).crop((40,30,360,250)).resize((240,165),Image.NEAREST);d=ImageDraw.Draw(im)
    d.text((4,2),f'{i+1}. {SW[i][0]}',font=F,fill='white');d.text((4,146),' '.join(P[k][1] for k in c),font=F,fill=(255,235,150));return im
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);n=0
    for slow in (1,1,2):
        for f in range(G*2+LIFE+5):
            fr=Image.new('RGB',(1440,826))
            for i in range(30):fr.paste(panel(i,f).convert('RGB'),((i%6)*240,(i//6)*165))
            for q in range(slow*2):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
