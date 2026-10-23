# run_down = lean edit C of seed 7102 frames 2,4,6,1 (left foot up / pass / right foot up / pass) -> legs alternate
import json,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';L='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/move/lean/outC/'
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_run.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
ims=[Image.open(L+f'{i:03d}.png').convert('RGBA') for i in (2,4,6,1)]
fy=[np.nonzero((np.array(i)[...,3]>200)&(np.array(i)[...,:3].min(-1)<150))[0].max() for i in ims];off=int(np.median(fy))-189
add=[]
for im in ims:
    a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1;add.append((im.crop((x0,y0,x1,y1)),128-x0,189-y0+off))
x=0;y0=sheet.height+1;rowh=0;pos=[]
for im,ax,ay in add:pos.append((x,y0));x+=im.width+1;rowh=max(rowh,im.height)
S2=Image.new('RGBA',(sheet.width,y0+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI])
for (im,ax,ay),(px,py) in zip(add,pos):S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay])
S2.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
t=d['anims']['run_right'][0][2];d['anims']['run_down']=[[SHI,base+i,t] for i in range(4)]
d['src']['move_down']='move_v3: walk_down = s6102; run_down = Ys8 sprint s7102 frames 2,4,6,1 + PixelLab lean edit C (legs kept, alternate), legs x1.2; run_left = mirror of run_right'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s);print('ok off',off)
