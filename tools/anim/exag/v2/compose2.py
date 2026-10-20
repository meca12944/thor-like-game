import sys,os,json,math,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageChops
exec(open('all/compose.py').read().split("os.makedirs('all/out'")[0])
def gen_seq(d,T,loop):  # interleaved key/mid frames from one job dir, ticks split like compose.new
    g=sorted(x for x in os.listdir(d) if x.endswith('.png'));fr=[];src=[];k=0;N=len(T)
    for i,t in enumerate(T):
        e=L(f'{d}/{g[k]}');k+=1
        if k<len(g) and (i<N-1 or loop):
            m=L(f'{d}/{g[k]}');k+=1;fr+=[(e,(t+1)//2)]+([(m,t//2)] if t//2 else []);src+=[i]+([None] if t//2 else [])
        else: fr.append((e,t));src.append(i)
    return fr,src
sys.path.insert(0,'fix');from trail2 import crescent,stages
from oneblade import fix as oneblade
def body_box(im):
    a=np.array(im)[...,3]>0;ys,xs=np.nonzero(a);return xs.min(),ys.min(),xs.max(),ys.max()
sys.path.insert(0,'fix');import trail3
SPAN=[60,100,115,115,115,115]
def retrail(n,seq,src):
    h,dr=n.split('_');out=[]
    tk=[i for i in range(len(man[f'{h}_down'])) if trail(L(f'all/{h}_{"down" if dr=="up" else dr}/k{i}.png'),420)[1]]
    if not tk: return seq
    lo,hi=min(tk)-1,max(tk);st=dict(zip(tk,stages(len(tk))))
    prev=None;sgn=None;on=0;cur=None
    for (im,t),k in zip(seq,src):
        if k is not None: cur=k
        if dr=='right': im=oneblade(im)[0]
        a=np.array(im);old,c=trail(im,420)
        if c: a[np.array(old)[...,3]>0]=0
        body=Image.fromarray(a,'RGBA')
        if dr=='up':
            if k in st: cr=crescent(dr,h,body_box(body),*st[k]);cr.alpha_composite(body);body=cr
        else:
            p=trail3.pivot(body);tp=trail3.tip(body)
            ang=math.degrees(math.atan2(tp[1]-p[1],tp[0]-p[0])) if tp else None
            if ang is not None and prev is not None:
                dlt=(ang-prev+540)%360-180
                if abs(dlt)>4: sgn=1 if dlt>0 else -1
            if cur is not None and lo<=cur<=hi+1 and ang is not None and sgn:
                span=SPAN[min(on,len(SPAN)-1)] if cur<=hi else 60;on+=1
                body.alpha_composite(trail3.arc(p,tp[2],ang,sgn,span,T=18 if h=='hit3' else 13))
            if ang is not None: prev=ang
        out.append((body,t))
    return out
def up_attack(h):
    fr,src=gen_seq(f'fix/{h}_up4',man[f'{h}_up'],False);return retrail(f'{h}_up',fr,src)
PUSH={'right':(-1,0),'left':(1,0),'down':(0,-1),'up':(0,1)}
def hurt_fx(seq,dr):
    # hitstop on the impact pose with a white flash and shake, then knockback slide (ease-out 18px), then hold the recoil pose
    ims=ticks(seq);imp=ims[0];out=[]
    wh=lambda im:Image.composite(Image.new('RGBA',im.size,(255,255,255,255)),im,im.split()[3].point(lambda v:255 if v else 0))
    for t in range(10): out.append((wh(imp) if t<3 else imp,(2*(-1)**t if t<8 else 0),0))
    n=len(ims)
    for t,im in enumerate(ims): p=1-(1-(t+1)/n)**2;out.append((im,0,p))
    for t in range(14): out.append((ims[-1],0,1))
    px,py=PUSH[dr];res=[]
    for im,sh,p in out:
        o=Image.new('RGBA',(256,256));o.paste(im,(round(px*18*p)+sh,round(py*18*p)),im);res.append(o)
    return res
def grid(cols,loops,label2='NEW'):
    T=max(max(len(cols[d][0]),len(cols[d][1])) for d in cols);out=[]
    for r in range(loops):
        for t in range(T):
            cv=Image.new('RGB',(4*384,2*384),(58,74,52));dd=ImageDraw.Draw(cv)
            for c,dr in enumerate(['right','left','down','up']):
                for row in (0,1):
                    s=cols[dr][row];im=s[min(t,len(s)-1)] if row==1 and label2=='HURT' else s[t%len(s)]
                    im=im.resize((384,384),Image.NEAREST);cv.paste(im,(c*384,row*384),im)
            dd.text((8,8),'in-game',fill=(255,255,0));dd.text((8,392),'NEW v2',fill=(255,255,0));out.append(cv)
    return out
mir=lambda s:[im.transpose(Image.FLIP_LEFT_RIGHT) for im in s]
os.makedirs('fix/out',exist_ok=True)
what=sys.argv[1:] or ['idle','hurt','combo']
if 'idle' in what:
    cols={}
    for d in ['right','down','up']:
        g=[L(f'fix/idle_{d}/{x}') for x in sorted(os.listdir(f'fix/idle_{d}'))];cols[d]=(ticks(orig(f'idle_{d}')),[im for im in g for _ in range(7)])
    cols['left']=(mir(cols['right'][0]),mir(cols['right'][1]));fr=grid(cols,3);save(fr,'fix/out/idle_v2')
if 'hurt' in what:
    cols={}
    for d in ['right','down','up']:
        man_n=f'hurt_{d}';g=sorted(x for x in os.listdir(f'fix/hurt3_{d}') if x.endswith('.png'))[1:]
        seq=[(L(f'fix/hurt3_{d}/{x}'),t) for x,t in zip(g,[1,3,4,4,4,4,4])]
        cols[d]=(ticks(orig(man_n)),seq)
    cols['left']=(mir(cols['right'][0]),[(im.transpose(Image.FLIP_LEFT_RIGHT),t) for im,t in cols['right'][1]])
    cols={d:(o,hurt_fx(s,d)) for d,(o,s) in cols.items()}
    T=max(len(cols[d][1]) for d in cols);cols={d:(o,s+[s[-1]]*(T-len(s))) for d,(o,s) in cols.items()}
    fr=grid(cols,3,'HURT');save(fr,'fix/out/hurt_v2');save(fr,'fix/out/hurt_v2_slow',2)
if 'combo' in what:
    cols={}
    for d in ['right','down','up']:
        o=sum((ticks(orig(f'{h}_{d}')) for h in ['hit1','hit2','hit3']),[])
        w=sum((ticks(up_attack(h) if d=='up' else new(f'{h}_{d}')) for h in ['hit1','hit2','hit3']),[])
        cols[d]=(o,w)
    cols['left']=(mir(cols['right'][0]),mir(cols['right'][1]));fr=grid(cols,3);save(fr,'fix/out/combo_v2');save(fr,'fix/out/combo_v2_slow',2)
print('ok')
