# hero showcase (Linette style): side = in-game atlas clips, down = SE 3/4 clips, up = NE 3/4 clips; left / down-left / up-left = mirrors.
# one field, scripted sequence, labels -> MP4
import json,os,sys,subprocess,random,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/';G='/home/user/thor-like-game/test128/assets/'
A=json.load(open(G+'anim/hero8.json'));SH={}
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
def clean(im):  # drop grey smudges PixelLab sometimes paints (big flat low-saturation blobs)
    a=np.array(im.convert('RGBA'));r,g,b,al=[a[...,i].astype(int) for i in range(4)];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    m=(al>0)&(mx-mn<14)&(mn>70);core=ndimage.binary_erosion(m,iterations=2)  # thin blades vanish here, fat smudges survive
    lab,n=ndimage.label(core)
    for i in range(1,n+1):
        c=lab==i
        if c.sum()>40: a[ndimage.binary_dilation(c,iterations=3)&m]=0
    return Image.fromarray(a)
def side(name):
    out=[]
    for s,c,t,*_ in A['anims'][name+'_right']:
        if s not in SH: SH[s]=Image.open(G+A['sheets'][s]).convert('RGBA')
        x,y,w,h,ax,ay=A['cells'][s][c];o=Image.new('RGBA',(256,256));im=SH[s].crop((x,y,x+w,y+h));o.paste(im,(128-ax,189-ay),im);out.append((o,t))
    return out
def diag(name,v,tk):
    d=P+f'dg/out_{name}_{v}';fs=sorted(x for x in os.listdir(d) if x.endswith('.png'))
    T=tk if isinstance(tk,list) else [tk]*len(fs)
    return [(clean(Image.open(f'{d}/{x}')),t) for x,t in zip(fs,T)]
TK={'idle':6,'walk':4,'run':3,'dash':[2,2,3,3,3,3,4],'death':[5,5,5,6,6,6,8,8,10],'jump':3,'cast':4,'hurt':[8,3,3,4,4,4,4]}
SIDE={'idle':'idle','walk':'walk','run':'run','dash':'dash','death':'death','jump':'jump','cast':'cast_s1','hurt':'hurtys','hit1':'hit1','hit2':'hit2','hit3':'hit3'}
sys.path.insert(0,P+'fix');sys.path.insert(0,P+'all');import trail3;from trail import trail;from oneblade import fix as oneblade
MAN=json.load(open(P+'all/manifest.json'))
def diag_attack(h,v):
    d=P+f'dg/out_{h}_{v}';fs=sorted(x for x in os.listdir(d) if x.endswith('.png'));T=MAN[f'{h}_right'];N=len(T)
    tk=[i for i in range(N) if trail(Image.open(P+f'all/{h}_right/k{i}.png'),420)[1]];lo,hi=min(tk)-1,max(tk)
    out=[];k=0;prev=None;sgn=None;on=0
    for i,t in enumerate(T):
        for part,tt in ((0,(t+1)//2),(1,t//2)):
            if part==1 and i==N-1: break
            im=clean(Image.open(f'{d}/{fs[k]}'));k+=1
            if tt==0: continue
            p=trail3.pivot(im);tp=trail3.tip(im);ang=None
            if tp:
                import math;ang=math.degrees(math.atan2(tp[1]-p[1],tp[0]-p[0]))
                if prev is not None:
                    dl=(ang-prev+540)%360-180
                    if abs(dl)>4: sgn=1 if dl>0 else -1
                prev=ang
            if lo<=i<=hi and ang is not None and sgn:  # thin Ys8-style arc, well ahead of the tip; behind the body for the back view
                arc=trail3.arc(p,tp[2],ang,sgn,[60,95,110][min(on,2)]);on+=1
                if v=='ne': arc.alpha_composite(im);im=arc
                else: im.alpha_composite(arc)
            out.append((im,tt))
    return out
ATKDIR='a4'  # attacks rebuilt from the in-game side combo skeleton (+40% lean, wider finisher)
def atk_ticks(h):
    T=MAN[f'{h}_right'];out=[]
    for i,t in enumerate(T):
        out.append(max(1,(t+1)//2))
        if i<len(T)-1: out.append(max(1,t//2))
    return out[:15]
def atk_swing(h):
    tk=[i for i in range(len(MAN[f'{h}_right'])) if trail(Image.open(P+f'all/{h}_right/k{i}.png'),420)[1]]
    return {f for i in tk for f in (2*i-1,2*i)}
def new_attack(h,v):  # 3D-designed combo (a3/), code-drawn thin trails ahead of the tip during the swing frames
    import math
    d=P+f'{ATKDIR}/out_{h}_{v}';fs=sorted(x for x in os.listdir(d) if x.endswith('.png'));out=[];prev=None;sgn=None;on=0
    for i,(f,tt) in enumerate(zip(fs,atk_ticks(h))):
        im=clean(Image.open(f'{d}/{f}'))
        if v=='east': im=oneblade(im)[0]
        a=np.array(im);o,cn=trail(im,420)
        if cn: a[np.array(o)[...,3]>0]=0;im=Image.fromarray(a)  # drop any slash PixelLab painted; trails are drawn in code
        p=trail3.pivot(im);tp=trail3.tip(im);ang=None
        if tp:
            ang=math.degrees(math.atan2(tp[1]-p[1],tp[0]-p[0]))
            if prev is not None:
                dl=(ang-prev+540)%360-180
                if abs(dl)>4: sgn=1 if dl>0 else -1
            prev=ang
        if i in atk_swing(h) and ang is not None and sgn:
            arc=trail3.arc(p,tp[2],ang,sgn,[60,95,110][min(on,2)]);on+=1
            if v=='ne': arc.alpha_composite(im);im=arc
            else: im.alpha_composite(arc)
        out.append((im,tt))
    return out
cache={}
def clip(m,d):
    k=(m,d)
    if k in cache: return cache[k]
    if m.startswith('hit'): c=new_attack(m,'east' if d in ('right','left') else 'se' if d.startswith('down') else 'ne')
    elif d in ('right','left'): c=side(SIDE[m])
    else: c=diag(m,'se' if d.startswith('down') else 'ne',TK[m])
    if d in ('left','downl','upl'): c=[(im.transpose(Image.FLIP_LEFT_RIGHT),t) for im,t in c]
    cache[k]=c;return c
DV={'right':(1,0),'left':(-1,0),'down':(0.7,0.7),'downl':(-0.7,0.7),'up':(0.7,-0.7),'upl':(-0.7,-0.7)}
DN={'right':'→','left':'←','down':'↘','downl':'↙','up':'↗','upl':'↖'}
W,H=480,300;bg=Image.new('RGBA',(W,H),(86,124,70,255));g=ImageDraw.Draw(bg);rnd=random.Random(3)
for _ in range(500): x,y=rnd.randrange(W),rnd.randrange(H);g.rectangle((x,y,x+1,y),fill=(72,108,58,255) if rnd.random()<.6 else (104,142,82,255))
SCRIPT=[('idle','down',70,0,'대기'),('walk','down',80,0.9,'걷기'),('walk','right',80,0.9,'걷기'),('walk','up',80,0.9,'걷기'),
        ('run','up',60,2.2,'달리기'),('run','left',70,2.2,'달리기'),('run','downl',60,2.2,'달리기'),('run','down',60,2.2,'달리기'),
        ('dash','right',None,4.0,'대시'),('dash','up',None,3.0,'대시'),('dash','downl',None,3.0,'대시'),
        ('hit1','right',None,0.4,'1타'),('hit2','right',None,0.4,'2타'),('hit3','right',None,0.6,'3타'),
        ('hit1','left',None,0.4,'1타'),('hit2','left',None,0.4,'2타'),('hit3','left',None,0.6,'3타'),
        ('hit1','down',None,0.4,'1타'),('hit2','down',None,0.4,'2타'),('hit3','down',None,0.6,'3타'),
        ('hit1','downl',None,0.4,'1타'),('hit2','downl',None,0.4,'2타'),('hit3','downl',None,0.6,'3타'),
        ('hit1','up',None,0.4,'1타'),('hit2','up',None,0.4,'2타'),('hit3','up',None,0.6,'3타'),
        ('hit1','upl',None,0.4,'1타'),('hit2','upl',None,0.4,'2타'),('hit3','upl',None,0.6,'3타'),
        ('idle','upl',50,0,'대기'),('hurt','down',None,-0.8,'맞기'),('hurt','up',None,0.8,'맞기'),('hurt','right',None,-0.8,'맞기'),
        ('jump','down',None,0,'점프'),('jump','upl',None,0,'점프'),('cast','down',None,0,'시전'),('cast','up',None,0,'시전'),
        ('idle','right',40,0,'대기'),('death','down',None,0,'사망'),('death','down',40,0,'사망')]
T=P+'dg/show_f';os.makedirs(T,exist_ok=True);[os.remove(T+'/'+f) for f in os.listdir(T)]
x,y=240.0,190.0;k=0
for m,d,ticks,sp,lab in SCRIPT:
    c=clip(m,d);seq=[im for im,t in c for _ in range(t)]
    if ticks: seq=[seq[i%len(seq)] for i in range(ticks)] if not (m=='death') else [c[-1][0]]*ticks
    for im in seq:
        dx,dy=DV[d];x=min(W-130,max(130,x+dx*sp));y=min(H-20,max(150,y+dy*sp))
        f=bg.copy();ImageDraw.Draw(f).ellipse((x-24,y-6,x+24,y+5),fill=(0,0,0,60))
        f.alpha_composite(im.resize((128,128),Image.NEAREST) if False else im,(int(x-128),int(y-189)))
        ImageDraw.Draw(f).text((8,6),f'주인공 · {lab} · {DN[d]}',font=F,fill='white')
        f.convert('RGB').resize((W*2,H*2),Image.NEAREST).save(f'{T}/f_{k:05d}.png');k+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{T}/f_%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',P+'hero_showcase_diag.mp4'],check=True)
print('frames',k)
