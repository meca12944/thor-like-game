# v2 (hero proportions, owner 10-23): bases rot_<n>/, every clip first brought back to its base height (edit keys come out ~25% bigger), then one scale per NPC.
# Felt NPC atlas: per NPC one sheet + json in the hero atlas format (cells [x,y,w,h,ax,ay], anims "<motion>_<dir>" = [[sheet,cell,ticks]]).
# dirs: down = south, up = north, right = east, left = mirrored east. Frames are scaled once per NPC (pxscale) to the game height and placed with the
# feet on (128,189), one constant offset per clip (from that clip's first frame), so the body bob/sway in the clip is kept.
import os,sys,json,glob
from PIL import Image,ImageOps
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from pxscale import pxscale
D=os.path.dirname(os.path.abspath(__file__));OUT=D+'/atlas';os.makedirs(OUT,exist_ok=True)
TH={'martha':118,'oswald':120,'sera':116,'bart':118,'rom':124,'gas':122,'luca':120,'toby':86,'ben':120}  # hero figure = 124
V={'s':'down','e':'right','n':'up'}
def noglow(ims):
    # PixelLab sometimes paints a white puff (steam/sparkle) into in-betweens: drop near-white pixels that are empty in frame 0 (textbook: effects in code, not art)
    import numpy as np;a0=np.array(ims[0]);out=[ims[0]]
    for im in ims[1:]:
        a=np.array(im);m=(a[...,:3].min(-1)>200)&(a[...,3]>0)&(a0[...,3]==0);a[m]=0;out.append(Image.fromarray(a))
    return out
def whites(f):
    import numpy as np;a=np.array(Image.open(f).convert('RGBA'));return int(((a[...,:3].min(-1)>200)&(a[...,3]>0)).sum())
def breathe(im,k):
    # shift everything above the waist down by k px (rows between are squeezed): chest/head drop on the out-breath
    if not k:return im
    b=im.getbbox();cut=b[1]+int((b[3]-b[1])*.5);out=im.copy();top=im.crop((0,0,256,cut));out.paste((0,0,0,0),(0,0,256,cut));out.paste(top,(0,k),top)
    return out
def place(fs,s,bh):
    raw=noglow([Image.open(f).convert('RGBA') for f in fs]);b0=raw[0].getbbox();s=s*bh/(b0[3]-b0[1])
    ims=[pxscale(im,s) for im in raw];b=ims[0].getbbox();dx,dy=128-(b[0]+b[2])//2,189-b[3]
    out=[]
    for im in ims:c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im);out.append(c)
    return out
for n,th in TH.items():
    if not os.path.isdir(f'{D}/rot_{n}'):continue
    h=max((lambda b:b[3]-b[1])(Image.open(f'{D}/rot_{n}/{d}.png').getbbox()) for d in ('south','north'));s=th/h
    clips={}
    for k,d in V.items():
        bb=Image.open(f'{D}/rot_{n}/'+{'s':'south','e':'east','n':'north'}[k]+'.png').getbbox();bh=bb[3]-bb[1]
        wf=sorted(glob.glob(f'{D}/tw8_{n}_{k}/*.png'))[:8];idf=sorted(glob.glob(f'{D}/idle_{n}_{k}/*.png'))[:4]
        if wf:clips[f'walk_{d}']=(place(wf,s,bh),[7]*8)
        if idf:
            idf=[f for i,f in enumerate(idf) if i==0 or whites(f)<=whites(idf[0])+3]  # idle in-betweens with a painted puff/sparkle are dropped (v2: 9 of 27 clips)
            fr=place(idf,s,bh)
            if len(fr)<3:fr=[breathe(fr[0],k) for k in (0,1,2)]  # not enough clean in-betweens: code breathing (upper body sinks 1-2 px), no effects possible
            seq=fr+fr[-2:0:-1];clips[f'idle_{d}']=(seq,[14]*len(seq))
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
