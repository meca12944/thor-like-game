# replace walk_down / run_down in test128 with PixelLab character-generated south cycles (frames 1-7; frame 0 = idle pose, dropped for a clean loop)
import json,glob,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';C='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/move/_cand/'
PICK={'walk_down':('m/hit1/south_s6102','anim/hero8_walk.webp',1),'run_down':('n/hit2/south_s6301','anim/hero8_run.webp',3)}
d=json.load(open(T+'assets/anim/hero8.json'))
for k,(src,sheetp,f0) in PICK.items():
    SHI=d['sheets'].index(sheetp);sheet=Image.open(T+'assets/'+sheetp).convert('RGBA')
    fs=sorted(glob.glob(C+src+'/*.png'))[f0:]
    ims=[Image.open(p).convert('RGBA') for p in fs]
    fy=[np.nonzero((np.array(i)[...,3]>200)&(np.array(i)[...,:3].min(-1)<150))[0].max() for i in ims];off=int(np.median(fy))-189  # one shift per clip keeps the natural bob
    add=[]
    for im in ims:
        a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
        add.append((im.crop((x0,y0,x1,y1)),128-x0,189-y0+off))
    x=0;y0=sheet.height+1;rowh=0;pos=[];yy=0
    for im,ax,ay in add:
        if x+im.width>sheet.width:x=0;yy+=rowh+1;rowh=0
        pos.append((x,y0+yy));x+=im.width+1;rowh=max(rowh,im.height)
    S2=Image.new('RGBA',(sheet.width,y0+yy+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI]);t=d['anims'][k][0][2]
    for (im,ax,ay),(px,py) in zip(add,pos):S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay])
    S2.save(T+'assets/'+sheetp,'WEBP',lossless=True,quality=100,method=6)
    d['anims'][k]=[[SHI,base+i,t] for i in range(len(add))];print(k,len(add),'feet shift',off)
d['src']['move_down']='move_v1: walk_down = PixelLab character animation south s6102, run_down = s6301 forward-lean sprint (frames 3-7)'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s)
