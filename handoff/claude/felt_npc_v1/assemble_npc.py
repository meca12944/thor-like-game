# Felt NPC atlas: per NPC one sheet + json in the hero atlas format (cells [x,y,w,h,ax,ay], anims "<motion>_<dir>" = [[sheet,cell,ticks]]).
# dirs: down = south, up = north, right = east, left = mirrored east. Frames are scaled once per NPC (pxscale) to the game height and placed with the
# feet on (128,189), one constant offset per clip (from that clip's first frame), so the body bob/sway in the clip is kept.
import os,sys,json,glob
from PIL import Image,ImageOps
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from pxscale import pxscale
D=os.path.dirname(os.path.abspath(__file__));OUT=D+'/atlas';os.makedirs(OUT,exist_ok=True)
TH={'martha':118,'oswald':120,'sera':116,'bart':118,'rom':126,'gas':124,'luca':122,'toby':84,'ben':122}
V={'s':'down','e':'right','n':'up'}
def noglow(ims):
    # PixelLab sometimes paints a white puff (steam/sparkle) into in-betweens: drop near-white pixels that are empty in frame 0 (textbook: effects in code, not art)
    import numpy as np;a0=np.array(ims[0]);out=[ims[0]]
    for im in ims[1:]:
        a=np.array(im);m=(a[...,:3].min(-1)>200)&(a[...,3]>0)&(a0[...,3]==0);a[m]=0;out.append(Image.fromarray(a))
    return out
def place(fs,s):
    ims=[pxscale(im,s) for im in noglow([Image.open(f).convert('RGBA') for f in fs])];b=ims[0].getbbox();dx,dy=128-(b[0]+b[2])//2,189-b[3]
    out=[]
    for im in ims:c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im);out.append(c)
    return out
for n,th in TH.items():
    if not os.path.isdir(f'{D}/{n}_s11'):continue
    h=max((lambda b:b[3]-b[1])(Image.open(f'{D}/{n}_s11/{d}.png').getbbox()) for d in ('south','north'));s=th/h
    clips={}
    for k,d in V.items():
        wf=sorted(glob.glob(f'{D}/tw8_{n}_{k}/*.png'))[:8];idf=sorted(glob.glob(f'{D}/idle_{n}_{k}/*.png'))[:4]
        if wf:clips[f'walk_{d}']=(place(wf,s),[7]*8)
        if idf:fr=place(idf,s);clips[f'idle_{d}']=([fr[0],fr[1],fr[2],fr[3],fr[2],fr[1]],[12]*6)
    for m in ('walk','idle'):
        if f'{m}_right' in clips:fr,t=clips[f'{m}_right'];clips[f'{m}_left']=([ImageOps.mirror(f) for f in fr],t)
    cells=[];anims={};x=0;row=[]
    for name,(fr,t) in clips.items():
        anims[name]=[]
        for f,tt in zip(fr,t):
            b=f.getbbox();cr=f.crop(b);row.append((cr,x));cells.append([x,0,cr.width,cr.height,128-b[0],189-b[1]]);anims[name].append([0,len(cells)-1,tt]);x+=cr.width+1
    if not row:continue
    H=max(c.height for c,_ in row);sh=Image.new('RGBA',(x,H))
    for c,xx in row:sh.paste(c,(xx,0))
    sh.save(f'{OUT}/felt_{n}.webp',lossless=True)
    json.dump({'_doc':f'Felt NPC {n} (owner 10-23), hero atlas format, 60 ticks = 1 s','sheets':[f'felt_{n}.webp'],'cells':[cells],'anims':anims,'scale':round(s,3)},open(f'{OUT}/felt_{n}.json','w'),separators=(',',':'))
    print(n,round(s,3),{k:len(v) for k,v in anims.items()})
