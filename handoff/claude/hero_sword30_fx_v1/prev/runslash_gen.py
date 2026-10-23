# run-and-slash melee: the hero runs, slimes come in, each one takes a close swing (3-hit combo cycles). multi-tone smears,
# contact FX on the enemy (cut line, sparks, white flash, knockback), hit-stop + shake. 6 colour styles.
import sys,os,math,random,colorsys,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
A='/home/user/thor-like-game/test128/sandbox/assets/';J=json.load(open(A+'hero_sbx.json'));SH={}
def clipfr(k):
    out=[]
    for s,c,t in J['anims'][k]:
        SH.setdefault(s,Image.open(A+J['sheets'][s]).convert('RGBA'));x,y,w,h,ax,ay=J['cells'][s][c][:6];out+=[(SH[s].crop((x,y,x+w,y+h)),ax,ay)]*t
    return out
RUN=clipfr('run_right')
SL=Image.open(A+'slime.png').convert('RGBA');SLF=[SL.crop((i*86,0,i*86+86,78)).resize((52,47),Image.NEAREST) for i in range(3)]
W,H=440,260;HX,GY=130,210;PX,PY=HX+20,GY-60                      # hero feet / sword-hand pivot on screen
Y,X=np.mgrid[0:H,0:W].astype(float)
def grad(stops,w):
    """w in 0..1 -> colour from a list of stops (dark glow ... white core)"""
    n=len(stops)-1;f=np.clip(w,0,1)*n;i=np.minimum(n-1,f.astype(int));t=(f-i)[...,None];S=np.array(stops,float);return S[i]*(1-t)+S[i+1]*t
def smear(a0,a1,head,tail,r1,r2,sq,stops,prism=False):
    dx=X-PX;dy=(Y-PY)/sq;r=np.hypot(dx,dy);th=np.degrees(np.arctan2(dy,dx));sgn=1 if a1>a0 else -1;u=((th-a0)*sgn)%360/abs(a1-a0)
    tail=max(tail,head-110/abs(a1-a0));vis=(u>=tail)&(u<=head)&(r>=r1)&(r<=r2);k=np.clip((u-tail)/max(head-tail,1e-3),0,1);rr=np.clip((r-r1)/(r2-r1),0,1)
    w=k**2*rr**1.2;o=np.zeros((H,W,4))
    if prism:
        hue=(u*1.4)%1;rgb=np.array([colorsys.hsv_to_rgb(h,.75,1) for h in np.linspace(0,1,64)])*255;col=rgb[(hue*63).astype(int)];col=col+(255-col)*np.clip((w-.6)/.4,0,1)[...,None]
    else:col=grad(stops,w)
    o[vis,:3]=col[vis];o[vis,3]=np.clip(255*np.minimum(1,w*1.7),0,255)[vis]
    m=vis&(k>.92)&(rr>.3);o[m,:3]=255;o[m,3]=255;m=vis&(rr>.93)&(k>.25);o[m,:3]=255;o[m,3]=np.maximum(o[m,3],230*k[m])
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
STY=[dict(nm='네온 사이안·마젠타',st=[(120,20,200),(220,60,255),(80,240,255),(255,255,255)],sp=[(255,240,90),(80,240,255),(255,120,255)]),
     dict(nm='선셋 블레이드',st=[(150,10,40),(255,80,40),(255,200,70),(255,255,230)],sp=[(90,230,255),(255,220,90),(255,255,255)]),
     dict(nm='오로라',st=[(70,30,170),(40,160,200),(120,255,200),(255,255,255)],sp=[(255,140,220),(140,255,210),(255,255,255)]),
     dict(nm='블러드 문',st=[(40,0,60),(200,20,60),(255,120,160),(255,245,250)],sp=[(255,215,90),(255,90,120),(255,255,255)]),
     dict(nm='일렉트릭',st=[(30,40,200),(60,160,255),(255,240,80),(255,255,255)],sp=[(255,255,255),(120,200,255),(255,240,80)]),
     dict(nm='프리즘',st=None,prism=1,sp=[(255,90,90),(90,255,140),(90,160,255),(255,240,90)])]
HITS=[(-105,55,4,34,88,.75),(80,-85,4,34,90,.8),(-150,100,6,30,100,1.0)]   # a0,a1,frames,r1,r2,squash
SPEED=5;GAP=125
def simulate():
    """world timeline shared by all styles: list of states"""
    hero=0.0;en=[{'x':170+i*GAP,'hp':1,'kb':0,'fl':0,'dead':-1,'vy':0,'y':0} for i in range(9)];sw=None;stop=0;shake=0;fx=[];T=[];combo=0;f=0;runf=0
    for f in range(300):
        if stop>0:stop-=1;T.append(dict(hero=hero,en=[dict(e) for e in en],sw=dict(sw) if sw else None,fx=[dict(q) for q in fx],shake=shake,runf=runf,frozen=1));shake*=.85;continue
        hero+=SPEED*(.55 if sw else 1);runf+=1
        tgt=[e for e in en if e['dead']<0 and e['x']-hero<75 and e['x']-hero>0]
        if not sw and tgt:sw={'n':combo%3,'a':0,'e':en.index(tgt[0])};combo+=1
        if sw:
            n=sw['n'];D=HITS[n][2];sw['a']+=1
            if sw['a']==D-1:
                e=en[sw['e']];e['fl']=4;e['kb']=[7,8,16][n];e['dead']=0;e['vy']=[-2,-3,-7][n];stop=[3,3,7][n];shake=[2,2.5,5][n]
                fx.append({'t':0,'x':e['x'],'y':-22,'n':n})
            if sw['a']>D+7:sw=None
        for e in en:
            if e['fl']>0:e['fl']-=1
            if e['dead']>=0:e['dead']+=1;e['x']+=e['kb'];e['kb']*=.85;e['y']+=e['vy'];e['vy']+=.8;e['y']=min(0,e['y'])
        for q in fx:q['t']+=1
        fx=[q for q in fx if q['t']<12];shake=shake*.8 if shake>.3 else 0
        T.append(dict(hero=hero,en=[dict(e) for e in en],sw=dict(sw) if sw else None,fx=[dict(q) for q in fx],shake=shake,runf=runf,frozen=0))
        if hero>170+8*GAP:break
    return T
def panel(st,s,lab):
    cam=s['hero']-HX+0;img=Image.new('RGBA',(W,H),(70,102,60,255));d=ImageDraw.Draw(img)
    for gx in range(-int(cam)%40-40,W,40):                     # scrolling ground marks
        d.rectangle([gx,GY+8,gx+3,GY+9],fill=(90,125,74,255));d.rectangle([gx+20,GY+26,gx+22,GY+27],fill=(56,86,48,255))
    d.line([0,GY+2,W,GY+2],fill=(62,92,54,255))
    for e in s['en']:
        if e['dead']>18:continue
        sx=e['x']-cam;fr=SLF[(s['runf']//6)%3]
        if e['fl']>0:fr=fr.copy();px=np.array(fr);px[...,:3]=np.where(px[...,3:]>0,255,px[...,:3]);fr=Image.fromarray(px)
        al=1 if e['dead']<10 else 1-(e['dead']-10)/8
        if al<1:fr=fr.copy();fr.putalpha(fr.getchannel('A').point(lambda v:int(v*al)))
        d.ellipse([sx-16,GY-3,sx+16,GY+3],fill=(0,0,0,50));img.alpha_composite(fr,(int(sx-26),int(GY-47+e['y'])))
    im,ax,ay=RUN[s['runf']%len(RUN)];d.ellipse([HX-22,GY-4,HX+22,GY+4],fill=(0,0,0,60));img.alpha_composite(im,(HX-ax,GY-ay))
    sw=s['sw']
    if sw:
        a0,a1,D,r1,r2,sq=HITS[sw['n']];a=sw['a'];t=min(1,a/D);head=1-(1-t)**3;tail=0 if a<D+1 else min(1,(a-D-1)/5)
        if tail<head:img.alpha_composite(smear(a0,a1,head,tail,r1,r2*(1.12 if sw['n']==2 else 1),sq,st['st'],st.get('prism')))
    for q in s['fx']:
        lay=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(lay);t=q['t'];x=q['x']-cam;y=GY+q['y'];big=q['n']==2;rnd=random.Random(int(q['x']));al=max(0,1-t/12)
        L=(44 if big else 32)*min(1,(t+1)/2);ang=[-.5,.6,-1.2][q['n']];cx,cy=math.cos(ang),math.sin(ang)
        c1=st['sp'][0];dd.line([x-cx*L,y-cy*L,x+cx*L,y+cy*L],fill=(*c1,int(255*al)),width=4 if big else 3);dd.line([x-cx*L,y-cy*L,x+cx*L,y+cy*L],fill=(255,255,255,int(255*al)),width=1)   # cut line
        if t<4:R=6+t*(5 if big else 3.5);dd.ellipse([x-R,y-R,x+R,y+R],outline=(*st['sp'][1],int(255*al)),width=2)
        for k in range(18 if big else 11):
            g=rnd.uniform(-1.6,1.6);sp=rnd.uniform(2.5,6);px_=x+math.cos(g)*sp*t;py_=y+math.sin(g)*sp*t*.8+t*t*.15;c=st['sp'][k%len(st['sp'])]
            dd.rectangle([px_,py_,px_+(2 if k%3 else 1),py_+1],fill=(*c,int(255*al)))
        if t<3:dd.line([x-14,y,x+14,y],fill=(255,255,255,int(255*al)),width=2);dd.line([x,y-10,x,y+10],fill=(255,255,255,int(255*al)),width=1)
        img.alpha_composite(lay)
    if s['frozen'] and any(q['t']<1 for q in s['fx']):img.alpha_composite(Image.new('RGBA',(W,H),(255,255,255,40)))
    sh=s['shake'];o=Image.new('RGBA',(W,H),(70,102,60,255));o.alpha_composite(img,(round((random.random()*2-1)*sh),round((random.random()*2-1)*sh*.6)))
    p=o.resize((480,284),Image.NEAREST);ImageDraw.Draw(p).text((8,6),lab,font=F,fill='white');return p
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);T=simulate();n=0
    for slow in (1,2):
        for s in T:
            fr=Image.new('RGB',(1440,568))
            for i,st in enumerate(STY):fr.paste(panel(st,s,f'{i+47}. {st["nm"]}'+(' · 1/2 슬로우' if slow>1 else '')).convert('RGB'),((i%3)*480,(i//3)*284))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n,len(T))
