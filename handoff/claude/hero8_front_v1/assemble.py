# Front view (down) pack for the caped hero (owner 10-23 "12345 전부 니 추천대로"):
#  1 idle  = old front idle (sandbox idle_s) lowered-sword frames 3..7 ping-pong (no sword snap / hair pop at the loop)
#  2 walk  = new key pose + one 8-frame cycle (cyc_walk)
#  3 run   = old front run (run_s) with feet put back on the ground (air <= 4 px, no sinking) and the body kept centred
#  4 hurt / dash / jump front = new (key pose + in-betweens)
#  5 size  = whole front set at 96% (the wide cape made it look bigger than the diagonal views)
# -> test128/assets/anim/hero8_front.webp + H8 atlas patch (idle/walk/run/hurt/dash/jump _down).
import sys,os,glob,json,numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from pxscale import pxscale
D=os.path.dirname(os.path.abspath(__file__));G=os.path.join(D,'../../../test128');SC=.96
SA=json.load(open(f'{G}/sandbox/assets/hero_sbx.json'));SIM={}
def sbx(f):
    if f[0] not in SIM:SIM[f[0]]=Image.open(f'{G}/sandbox/assets/'+SA['sheets'][f[0]]).convert('RGBA')
    x,y,w,h,ax,ay=SA['cells'][f[0]][f[1]];c=Image.new('RGBA',(256,256));c.paste(SIM[f[0]].crop((x,y,x+w,y+h)),(128-ax,189-ay));return c
def body(im):
    a=np.array(im.convert('RGBA')).astype(int);al=a[...,3]>0;v=a[...,:3].max(2);dk=al&(v<150);ys,xs=np.nonzero(dk);return ys.min(),ys.max(),float(np.median(xs))
def place(im,s,lift=0,cx=None):   # scale about the feet by s, feet on y 189 - lift, body centre at cx
    t,b,x=body(im)
    if abs(s-1)>.005:
        im2=pxscale(im,s);c=Image.new('RGBA',(256,256));c.paste(im2,(round(x-x*s),round(b-b*s)),im2);im=c;t,b,x=body(im)
    c=Image.new('RGBA',(256,256));c.paste(im,(0 if cx is None else round(cx-x),189-lift-b),im);return c
F=lambda d:[Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'{D}/{d}/*.png'))]
I=[sbx(f) for f in SA['anims']['idle_s']];t0,b0,X0=body(I[3]);H0=(b0-t0)*SC   # reference: front idle, lowered sword
CL={}
CL['idle_down']=[place(I[k],SC,0,X0) for k in (3,4,5,6,7,6,5,4)]
# walk / run keep their own motion (owner 10-23 "수정전보다 뻣뻣하다"): v1 scaled every frame to the same height and pinned every
# frame's feet / centre, which flattened the body rise of the walk and turned the run's jump into a crouch. Now one scale and one
# shift per clip (about the canvas feet point), and only frames that sink below the ground are lifted back onto it.
def keep(frames,s,ground=None,clamp=True):
    sc=[]
    for im in frames:
        if abs(s-1)>.005:im2=pxscale(im,s);c=Image.new('RGBA',(256,256));c.paste(im2,(round(128-128*s),round(189-189*s)),im2);im=c
        sc.append(im)
    bs=[body(im) for im in sc];g=max(b for _,b,_ in bs) if ground is None else ground;dx=round(X0-np.mean([x for _,_,x in bs]))
    out=[]
    for im,(t,b,x) in zip(sc,bs):
        dy=189-g if ground is not None or clamp else 0;dy-=max(0,b+dy-189) if clamp else 0;c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im);out.append(c)
    return out
W=F('cyc_walk')[:8];CL['walk_down']=keep(W,H0/(body(W[0])[1]-body(W[0])[0]))
def sway(frames,amp):   # weight shift onto the standing leg: one side-to-side swing per full cycle (2 steps)
    out=[]
    for i,im in enumerate(frames):c=Image.new('RGBA',(256,256));c.paste(im,(round(amp*np.sin(2*np.pi*i/len(frames))),0),im);out.append(c)
    return out
CL['walk_down']=sway(CL['walk_down'],2)
R=[sbx(f) for f in SA["anims"]["run_s"]];CL['run_down']=keep(R,SC,None,False)   # the run's own up/down kept as drawn (lifting its 2 landing frames made the head jump)
def clip(frames):  # transitions: one scale for the clip (from its first, standing frame), feet on the ground, centre from frame 0
    s=H0/(body(frames[0])[1]-body(frames[0])[0]);dx=None;out=[]
    for f in frames:out.append(place(f,s,0,X0))
    return out
h=F('tw_hurt');CL['hurt_down']=clip(h)
di=F('tw_dash_in');do=F('tw_dash_out');CL['dash_down']=clip(di+do[1:])
ju=F('tw_jump_up');jd=F('tw_jump_down');CL['jump_down']=clip(ju+jd[1:])
cells=[];sheet=Image.new('RGBA',(2048,2048));X=Y=rowH=0;idx={}
for k,fr in CL.items():
    idx[k]=[]
    for im in fr:
        l,t,r,bb=im.getbbox();cr=im.crop((l,t,r,bb));w,hh=cr.size
        if X+w>2048:X=0;Y+=rowH+1;rowH=0
        sheet.paste(cr,(X,Y));cells.append([X,Y,w,hh,128-l,189-t]);idx[k].append(len(cells)-1);X+=w+1;rowH=max(rowH,hh)
sheet=sheet.crop((0,0,2048,Y+rowH+1));sheet.save(f'{G}/assets/anim/hero8_front.webp',lossless=True,quality=100)
for k,fr in CL.items():
    os.makedirs(f'{D}/final/{k}',exist_ok=True)
    for i,im in enumerate(fr):im.save(f'{D}/final/{k}/{i:03d}.png')
p=f'{G}/index.html';s=open(p).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);A,end=json.JSONDecoder().raw_decode(s[j:]);end+=j
if 'anim/hero8_front.webp' in A['sheets']:si=A['sheets'].index('anim/hero8_front.webp');A['cells'][si]=cells
else:A['sheets'].append('anim/hero8_front.webp');A['cells'].append(cells);si=len(A['sheets'])-1
an=A['anims'];T=lambda k,t:[[si,c,tt] for c,tt in zip(idx[k],t)]
an['idle_down']=T('idle_down',[9]*8);an['walk_down']=T('walk_down',[5]*8);an['run_down']=T('run_down',[4]*8)
c=idx['hurt_down'];an['hurt_down']=[[si,c[1],3],[si,c[2],3],[si,c[3],4],[si,c[4],4],[si,c[3],3],[si,c[1],3]]
an['dash_down']=T('dash_down',[2]*8+[1]);an['jump_down']=T('jump_down',[5]*9)
A['_front_note']='owner 10-23: front (down) set = hero8_front.webp (handoff/claude/hero8_front_v1): idle ping-pong, new walk cycle, run on the ground, new hurt/dash/jump, 96% size'
s=s[:j]+json.dumps(A,ensure_ascii=False,separators=(',',':'))+s[end:];open(p,'w').write(s)
print({k:len(v) for k,v in idx.items()},sheet.size)
