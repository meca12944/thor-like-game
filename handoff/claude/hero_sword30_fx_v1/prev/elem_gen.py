# run-and-slash, elemental: hit1 = horizontal (x-axis) sweep, hit2 = vertical (y-axis) cut, hit3 = both crossing (+) big.
# elements: poison / fire / electric / water / ice / dark - smear palette, particles off the smear, hit burst, status on the slime.
import sys,os,math,random,numpy as np,importlib.util
from PIL import Image,ImageDraw,ImageFont
sp=importlib.util.spec_from_file_location('R','runslash/gen.py');R=importlib.util.module_from_spec(sp);sp.loader.exec_module(R)
F=R.F;RUN=R.RUN;SLF=R.SLF;W,H=440,260;HX,GY=130,210;Y,X=R.Y,R.X
def smear(px,py,a0,a1,head,tail,r1,r2,sq,stops):
    dx=X-px;dy=(Y-py)/sq;r=np.hypot(dx,dy);th=np.degrees(np.arctan2(dy,dx));sgn=1 if a1>a0 else -1;span=abs(a1-a0);u=((th-a0)*sgn)%360/span
    tail=max(tail,head-120/span);vis=(u>=tail)&(u<=head)&(r>=r1)&(r<=r2);k=np.clip((u-tail)/max(head-tail,1e-3),0,1);rr=np.clip((r-r1)/(r2-r1),0,1)
    w=k**2*rr**1.2;o=np.zeros((H,W,4));col=R.grad(stops,w);o[vis,:3]=col[vis];o[vis,3]=np.clip(255*np.minimum(1,w*1.7),0,255)[vis]
    m=vis&(k>.92)&(rr>.3);o[m,:3]=255;o[m,3]=255;m=vis&(rr>.93)&(k>.25);o[m,:3]=255;o[m,3]=np.maximum(o[m,3],230*k[m])
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
# cuts: (pivot dx, pivot dy from feet, a0, a1, frames, r1, r2, squash)
HORZ=(14,-60,165,15,4,30,104,.45);VERT=(40,-66,-95,95,4,26,84,.9)
HITS=[[HORZ],[VERT],[(14,-60,165,15,6,32,122,.48),(46,-70,-100,100,6,28,98,1.0)]]
EL=[dict(nm='독',st=[(40,0,60),(120,30,170),(110,220,60),(230,255,190)],acc=(150,255,80),acc2=(190,90,255),tint=(120,255,90)),
    dict(nm='화염',st=[(120,0,0),(240,60,10),(255,180,40),(255,255,220)],acc=(255,200,60),acc2=(255,90,20),tint=(255,130,60)),
    dict(nm='전기',st=[(20,30,160),(60,150,255),(200,240,255),(255,255,255)],acc=(255,250,120),acc2=(120,220,255),tint=(200,240,255)),
    dict(nm='물',st=[(0,40,120),(20,120,220),(110,210,255),(240,255,255)],acc=(160,230,255),acc2=(60,150,255),tint=(90,170,255)),
    dict(nm='얼음',st=[(40,90,170),(120,200,255),(210,245,255),(255,255,255)],acc=(230,250,255),acc2=(140,210,255),tint=(170,230,255)),
    dict(nm='암흑',st=[(10,0,20),(80,10,110),(200,60,220),(255,220,255)],acc=(230,120,255),acc2=(40,0,60),tint=(150,60,190))]
SPEED=5;GAP=125
def simulate():
    hero=0.0;en=[{'x':170+i*GAP,'kb':0,'fl':0,'dead':-1,'vy':0,'y':0,'st':0,'hn':0} for i in range(7)];sw=None;stop=0;shake=0;fx=[];T=[];combo=0;runf=0
    for f in range(320):
        if stop>0:stop-=1;T.append(dict(hero=hero,en=[dict(e) for e in en],sw=dict(sw) if sw else None,fx=[dict(q) for q in fx],shake=shake,runf=runf,frozen=1));shake*=.85;continue
        hero+=SPEED*(.55 if sw else 1);runf+=1
        tgt=[e for e in en if e['dead']<0 and 0<e['x']-hero<80]
        if not sw and tgt:sw={'n':combo%3,'a':0,'e':en.index(tgt[0])};combo+=1
        if sw:
            n=sw['n'];D=HITS[n][0][4];sw['a']+=1
            if sw['a']==D-1:
                e=en[sw['e']];e['fl']=4;e['kb']=[6,4,15][n];e['dead']=0;e['vy']=[-1,-4,-8][n];e['st']=40;e['hn']=n;stop=[3,3,7][n];shake=[2,2.5,5][n]
                fx.append({'t':0,'x':e['x'],'y':-22,'n':n,'seed':f})
            if sw['a']>D+8:sw=None
        for e in en:
            if e['fl']>0:e['fl']-=1
            if e['st']>0:e['st']-=1
            if e['dead']>=0:e['dead']+=1;e['x']+=e['kb'];e['kb']*=.85;e['y']+=e['vy'];e['vy']+=.8;e['y']=min(0,e['y'])
        for q in fx:q['t']+=1
        fx=[q for q in fx if q['t']<16];shake=shake*.8 if shake>.3 else 0
        T.append(dict(hero=hero,en=[dict(e) for e in en],sw=dict(sw) if sw else None,fx=[dict(q) for q in fx],shake=shake,runf=runf,frozen=0))
        if hero>170+6*GAP:break
    return T
def bolt(d,x0,y0,x1,y1,rnd,col,w=2):
    pts=[(x0,y0)]
    for i in range(1,6):t=i/6;pts.append((x0+(x1-x0)*t+rnd.uniform(-6,6),y0+(y1-y0)*t+rnd.uniform(-6,6)))
    pts.append((x1,y1));d.line(pts,fill=col,width=w);d.line(pts,fill=(255,255,255,col[3]),width=1)
def smear_particles(d,el,px,py,a0,a1,head,r2,sq,a,seed,i):
    rnd=random.Random(seed);n=10
    for k in range(n):
        h=rnd.uniform(max(0,head-.6),head);an=math.radians(a0+(a1-a0)*h);rr=r2*rnd.uniform(.75,1.05);x=px+math.cos(an)*rr;y=py+math.sin(an)*rr*sq;al=max(0,255-a*20)
        if i==0:y-=a*rnd.uniform(.5,1.5);r=rnd.uniform(1.5,3);d.ellipse([x-r,y-r,x+r,y+r],outline=(*el['acc'],al),width=1)          # bubbles
        elif i==1:y-=a*rnd.uniform(1,2.5);r=max(1,3-a*.2);d.ellipse([x-r,y-r*1.5,x+r,y+r*1.5],fill=(*(el['acc'] if k%2 else el['acc2']),al))   # embers
        elif i==2:
            if k<3 and a<6:bolt(d,x,y,x+rnd.uniform(-14,14),y+rnd.uniform(-14,14),rnd,(*el['acc'],al),1)
        elif i==3:y+=a*a*.12;x+=rnd.uniform(-1,1)*a;d.ellipse([x-1.5,y-2,x+1.5,y+2],fill=(*el['acc'],al))                          # droplets
        elif i==4:s=2.5;d.polygon([(x,y-s*1.6),(x+s,y),(x,y+s*1.6),(x-s,y)],fill=(*el['acc'],al),outline=(*el['acc2'],al))          # frost bits
        else:y-=a*.6;r=2+a*.5;d.ellipse([x-r,y-r,x+r,y+r],fill=(30,0,40,max(0,160-a*12)))                                         # dark smoke
def hit_fx(d,el,i,q,x,y):
    t=q['t'];big=q['n']==2;rnd=random.Random(q['seed']);al=max(0,1-t/16);A=int(255*al)
    # cut marks: x-axis, y-axis, or both
    L=(46 if big else 32)*min(1,(t+1)/2)
    if q['n'] in (0,2):d.line([x-L,y,x+L,y],fill=(*el['acc'],A),width=4 if big else 3);d.line([x-L,y,x+L,y],fill=(255,255,255,A),width=1)
    if q['n'] in (1,2):d.line([x,y-L,x,y+L],fill=(*el['acc'],A),width=4 if big else 3);d.line([x,y-L,x,y+L],fill=(255,255,255,A),width=1)
    if t<4:R_=6+t*(6 if big else 4);d.ellipse([x-R_,y-R_,x+R_,y+R_],outline=(*el['acc2'],A),width=2)
    for k in range(20 if big else 12):
        g=rnd.uniform(0,2*math.pi);s=rnd.uniform(2,5.5);px_=x+math.cos(g)*s*t;py_=y+math.sin(g)*s*t*.8
        if i==0:py_-=t*.8;r=rnd.uniform(1.5,3.5);d.ellipse([px_-r,py_-r,px_+r,py_+r],fill=(*(el['acc'] if k%2 else el['acc2']),int(A*.8)))
        elif i==1:py_-=t*1.4;r=max(1,4-t*.25);d.ellipse([px_-r,py_-r*1.5,px_+r,py_+r*1.5],fill=(*(el['acc'] if k%3 else el['acc2']),A))
        elif i==2:
            if k<(5 if big else 3) and t<7:bolt(d,x,y,x+math.cos(g)*rnd.uniform(18,34),y+math.sin(g)*rnd.uniform(14,28),rnd,(*el['acc'],A),2)
        elif i==3:py_+=t*t*.2;d.ellipse([px_-2,py_-2.5,px_+2,py_+2.5],fill=(*el['acc'],A))
        elif i==4:s_=rnd.uniform(3,6);d.polygon([(px_,py_-s_*1.6),(px_+s_*.6,py_),(px_,py_+s_*1.6),(px_-s_*.6,py_)],fill=(*el['acc'],A),outline=(*el['acc2'],A))
        else:r=3+t*.7;d.ellipse([px_-r,py_-r,px_+r,py_+r],fill=(30,0,40,int(A*.5)))
    if i==3 and t<14:rr=8+t*4;d.ellipse([x-rr,GY-rr*.25,x+rr,GY+rr*.25],outline=(160,230,255,A),width=2)   # water ripple on the ground
def slime_img(e,el,i,runf):
    fr=SLF[(runf//6)%3].copy();px=np.array(fr).astype(float)
    if e['st']>0:                                                             # element status tint
        tint=np.array(el['tint']);k=.55 if i==4 else .4;px[...,:3]=px[...,:3]*(1-k)+tint*k
    if e['fl']>0:px[...,:3]=np.where(px[...,3:]>0,255,px[...,:3])
    return Image.fromarray(px.clip(0,255).astype(np.uint8))
def panel(i,s,lab):
    el=EL[i];cam=s['hero']-HX;img=Image.new('RGBA',(W,H),(70,102,60,255));d=ImageDraw.Draw(img)
    for gx in range(-int(cam)%40-40,W,40):d.rectangle([gx,GY+8,gx+3,GY+9],fill=(90,125,74,255));d.rectangle([gx+20,GY+26,gx+22,GY+27],fill=(56,86,48,255))
    for e in s['en']:
        if e['dead']>20:continue
        sx=e['x']-cam;fr=slime_img(e,el,i,s['runf']);al=1 if e['dead']<12 else 1-(e['dead']-12)/8
        if al<1:fr.putalpha(fr.getchannel('A').point(lambda v:int(v*al)))
        d.ellipse([sx-16,GY-3,sx+16,GY+3],fill=(0,0,0,50));img.alpha_composite(fr,(int(sx-26),int(GY-47+e['y'])))
        if e['st']>0:   # status particles on the slime
            dd=ImageDraw.Draw(img);rnd=random.Random(int(e['x'])+s['runf']);yy=GY-24+e['y']
            if i==0 and s['runf']%4<2:dx_=rnd.uniform(-8,8);dd.ellipse([sx+dx_-2,yy+18,sx+dx_+2,yy+23],fill=(150,255,80,200))
            if i==1:
                for k in range(3):fx_=sx+rnd.uniform(-14,14);fy=yy-rnd.uniform(4,20);dd.ellipse([fx_-2,fy-4,fx_+2,fy+2],fill=(255,rnd.choice((120,190)),40,220))
            if i==2 and s['runf']%3==0:bolt(dd,sx-12,yy+rnd.uniform(-10,10),sx+12,yy+rnd.uniform(-10,10),rnd,(255,250,140,230),1)
            if i==4:dd.polygon([(sx-16,yy+20),(sx-10,yy-6),(sx-2,yy+4),(sx+6,yy-14),(sx+16,yy+20)],outline=(230,250,255,200))
    im,ax,ay=RUN[s['runf']%len(RUN)];d.ellipse([HX-22,GY-4,HX+22,GY+4],fill=(0,0,0,60));img.alpha_composite(im,(HX-ax,GY-ay))
    sw=s['sw']
    if sw:
        lay=Image.new('RGBA',(W,H));dl=ImageDraw.Draw(lay)
        for j,(pdx,pdy,a0,a1,D,r1,r2,sq) in enumerate(HITS[sw['n']]):
            a=sw['a']-j;
            if a<0:continue
            t=min(1,a/D);head=1-(1-t)**3;tail=0 if a<D+1 else min(1,(a-D-1)/5)
            if tail<head:img.alpha_composite(smear(HX+pdx,GY+pdy,a0,a1,head,tail,r1,r2,sq,el['st']));smear_particles(dl,el,HX+pdx,GY+pdy,a0,a1,head,r2,sq,a,sw['e']*7+j,i)
        img.alpha_composite(lay)
    lay=Image.new('RGBA',(W,H));dl=ImageDraw.Draw(lay)
    for q in s['fx']:hit_fx(dl,el,i,q,q['x']-cam,GY+q['y'])
    img.alpha_composite(lay)
    if s['frozen'] and any(q['t']<1 for q in s['fx']):img.alpha_composite(Image.new('RGBA',(W,H),(*el['tint'],45)))
    sh=s['shake'];o=Image.new('RGBA',(W,H),(70,102,60,255));o.alpha_composite(img,(round((random.random()*2-1)*sh),round((random.random()*2-1)*sh*.6)))
    p=o.resize((480,284),Image.NEAREST);ImageDraw.Draw(p).text((8,6),lab,font=F,fill='white');return p
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);T=simulate();n=0
    for slow in (1,2):
        for s in T:
            fr=Image.new('RGB',(1440,568))
            for i,el in enumerate(EL):fr.paste(panel(i,s,f'{i+53}. {el["nm"]} · 가로→세로→교차'+(' · 1/2 슬로우' if slow>1 else '')).convert('RGB'),((i%3)*480,(i//3)*284))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n,len(T))
