# Load the final saved hero 3-hit (main test128/sandbox atlas: hit1, hit2, hit3s) for all 6 directions and strip the baked trails:
#  - sky-blue hit3 crescent: semi-transparent (62%) tinted pixels -> alpha < 250, or opaque pixels tinted sky blue
#  - white crescents / speed streaks: thick neutral-light blobs (blade is 1-3 px wide, so it does not survive a 2 px erosion)
# usage: strip.py <sbx assets dir> <out dir>   -> out/<hit>_<dir>/NN.png (256 canvas, feet 128,189) + clips.json (ticks)
import json,sys,os,numpy as np
from PIL import Image
from scipy import ndimage
src,out=sys.argv[1:3];A=json.load(open(src+'/hero_sbx.json'));SH={}
def cell(s,c):
    if s not in SH: SH[s]=Image.open(src+'/'+A['sheets'][s]).convert('RGBA')
    x,y,w,h,ax,ay=A['cells'][s][c];im=Image.new('RGBA',(256,256));im.paste(SH[s].crop((x,y,x+w,y+h)),(128-ax,189-ay));return im
def strip(im):
    a=np.array(im);r,g,b,al=[a[...,i].astype(int) for i in range(4)];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    cut=(al>0)&(al<250)                                        # translucent trail layer
    cut|=(al>0)&(b>r+45)&(g>r+25)&(mn>100)                     # sky-blue tint
    m=(al>0)&(mx-mn<24)&(mn>150)                               # neutral light: blade + white trails
    core=ndimage.binary_erosion(m,iterations=2);lab,n=ndimage.label(core)
    for i in range(1,n+1):
        c=lab==i
        if c.sum()>25: cut|=ndimage.binary_dilation(c,iterations=3)&m
    a[cut]=0
    # drop specks left floating
    al2=a[...,3]>0;l2,n2=ndimage.label(al2,structure=np.ones((3,3)))
    if n2>1:
        sz=ndimage.sum(al2,l2,range(1,n2+1));big=np.argmax(sz)+1
        for i in range(1,n2+1):
            if i!=big and sz[i-1]<200: a[l2==i]=0      # floating speed lines / crescent crumbs
    return Image.fromarray(a),int(cut.sum())
clips={}
for h,name in (('hit1','hit1'),('hit2','hit2'),('hit3','hit3s')):
    for d in ('right','left','down','downl','up','upl'):
        L=A['anims'][f'{name}_{d}'];o=f'{out}/{h}_{d}';os.makedirs(o,exist_ok=True);cuts=[]
        for i,e in enumerate(L):
            raw=cell(e[0],e[1]);raw.save(f'{o}/raw{i:02d}.png');cl,k=strip(raw)
            if k>400 and h!='hit3': cl,_=strip(cell(e[0],e[1]-1));k=-k   # white glow over the whole blade (side lunge end): use the previous cell of the same lunge
            if h=='hit3' and d in('right','left'):            # side hit3: white crumbs of the old crescent left at the boots
                q=np.array(cl);r_,g_,b_=[q[...,j].astype(int) for j in range(3)];mn_=np.minimum(np.minimum(r_,g_),b_);mx_=np.maximum(np.maximum(r_,g_),b_)
                yy=np.arange(256)[:,None];q[(q[...,3]>0)&(mn_>150)&(mx_-mn_<30)&(yy>165)]=0;cl=Image.fromarray(q)
            cl.save(f'{o}/{i:02d}.png');cuts.append(k)
        clips[f'{h}_{d}']=[e[2] for e in L];print(h,d,'cut px',cuts)
json.dump(clips,open(out+'/clips.json','w'))
