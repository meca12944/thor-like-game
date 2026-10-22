# Pack the new hero8 clips (owner 10-22: run_down, walk_up, walk_down legs, 9-frame side dash, hurt front/back) into
# test128/assets/anim/hero8_fix.webp and patch the H8 atlas in test128/index.html. Size/feet are matched to the old frames:
# body height = hair top (first dark row, the light sword ignored) -> boot bottom; every frame scaled to the clip's source height, feet on y 189.
import sys,os,glob,json,numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from pxscale import pxscale
D=os.path.dirname(os.path.abspath(__file__));G=os.path.join(D,'../../../test128')
def body(im):
    a=np.array(im.convert('RGBA')).astype(int);al=a[...,3]>0;v=a[...,:3].max(2);dark=al&(v<150)
    ys,xs=np.nonzero(dark);return ys.min(),ys.max(),float(np.median(xs))
def norm(im,refH,refX=None):
    t,b,cx=body(im);s=refH/(b-t)
    if abs(s-1)>.01:
        im2=pxscale(im,s);c=Image.new('RGBA',(256,256));c.paste(im2,(round(cx-cx*s),round(b-b*s)),im2);im=c;t,b,cx=body(im)
    c=Image.new('RGBA',(256,256));dx=0 if refX is None else round(refX-cx);c.paste(im,(dx,189-b),im);return c
F=lambda d:[Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'{D}/{d}/*.png'))]
def ref(p):t,b,cx=body(Image.open(f'{D}/src/{p}.png'));return b-t,cx
CL={}
h,x=ref('walk_down_0');CL['walk_down']=[norm(f,h,x) for f in F('cyc_walk_down')[:8]]
CL['run_down']=[norm(f,h*.97,x) for f in F('cyc_run_down')[:8]]          # slight forward lean
h,x=ref('walk_up_2');CL['walk_up']=[norm(f,h,x) for f in F('cyc_walk_up')[:8]]
a=F('tw_dash_a');b=F('tw_dash_b');dh=[body(Image.open(f'{D}/src/dash_right_{k}.png')) for k in range(4)]
keep=lambda im,k:norm(im,dh[k][1]-dh[k][0],dh[k][2])
mid=lambda p,q:(dh[p][1]-dh[p][0]+dh[q][1]-dh[q][0])/2
CL['dash_right']=[keep(a[0],0)]+[norm(f,mid(0,1)) for f in a[1:4]]+[keep(a[4],1),keep(b[0],2)]+[norm(f,mid(2,3)) for f in b[1:4]]+[keep(b[4],3)]
h,x=ref('idle_down_0');CL['hurt_down']=[norm(f,h*(1-.04*k/4),x) for k,f in enumerate(F('tw_hurt_down'))]   # flinch: up to 4% lower
h,x=ref('idle_up_0');CL['hurt_up']=[norm(f,h*(1-.04*k/4),x) for k,f in enumerate(F('tw_hurt_up'))]
# pack: crop each frame to its bbox, keep the feet anchor (128,189)
cells=[];sheet=Image.new('RGBA',(2048,1024));X=Y=rowH=0;idx={}
for k,fr in CL.items():
    idx[k]=[]
    for im in fr:
        l,t,r,bb=im.getbbox();cr=im.crop((l,t,r,bb));w,hh=cr.size
        if X+w>2048:X=0;Y+=rowH+1;rowH=0
        sheet.paste(cr,(X,Y));cells.append([X,Y,w,hh,128-l,189-t]);idx[k].append(len(cells)-1);X+=w+1;rowH=max(rowH,hh)
sheet=sheet.crop((0,0,2048,Y+rowH+1));sheet.save(f'{G}/assets/anim/hero8_fix.webp',lossless=True,quality=100)
for k,fr in CL.items():
    os.makedirs(f'{D}/final/{k}',exist_ok=True)
    for i,im in enumerate(fr):im.save(f'{D}/final/{k}/{i:03d}.png')
# patch atlas
p=f'{G}/index.html';s=open(p).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);A,end=json.JSONDecoder().raw_decode(s[j:]);end+=j
if 'anim/hero8_fix.webp' in A['sheets']:si=A['sheets'].index('anim/hero8_fix.webp');A['cells'][si]=cells
else:A['sheets'].append('anim/hero8_fix.webp');A['cells'].append(cells);si=len(A['sheets'])-1
an=A['anims'];T=lambda k,t:[[si,c,tt] for c,tt in zip(idx[k],t)]
an['walk_down']=T('walk_down',[4]*8);an['run_down']=T('run_down',[4]*8);an['walk_up']=T('walk_up',[4]*8)
an['dash_right']=T('dash_right',[2]*7+[1]*3)
for d in('down','up'):
    c=idx['hurt_'+d];an['hurt_'+d]=[[si,c[1],3],[si,c[2],3],[si,c[3],4],[si,c[4],4],[si,c[3],3],[si,c[1],3]]
A['_fix_v1']='owner 10-22: run_down / walk_up / walk_down / dash_right / hurt_down / hurt_up redrawn (handoff/claude/hero8_fix_v1, PixelLab key pose + cycle), sheet anim/hero8_fix.webp'
s=s[:j]+json.dumps(A,ensure_ascii=False,separators=(',',':'))+s[end:];open(p,'w').write(s)
print({k:len(v) for k,v in idx.items()},sheet.size)
