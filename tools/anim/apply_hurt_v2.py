# hurt v2 (feel=ys): designed recoil drawn with PixelLab skeleton from the in-game standing frame -> anims hurtys_<dir> (7 frames, 30 ticks: impact held 8, then recover). left = mirror of right
import json,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';R='/home/user/thor-like-game/handoff/claude/hurt_v2/'
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_hurt.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
TK=[8,3,3,4,4,4,4]
fr={dr:[Image.open(f'{R}{dr}/{i:03d}.png').convert('RGBA') for i in range(1,8)] for dr in ['right','down','up']}
fr['left']=[f.transpose(Image.FLIP_LEFT_RIGHT) for f in fr['right']]
add=[]
for n,fs in fr.items():
    for im in fs:
        a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
        add.append((n,im.crop((x0,y0,x1,y1)),128-x0,189-y0))
W=max(sheet.width,1024);x=0;y=sheet.height+1;rowh=0;pos=[]
for n,im,ax,ay in add:
    if x+im.width>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=im.width+1;rowh=max(rowh,im.height)
S2=Image.new('RGBA',(W,y+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI]);idx={}
for k,((n,im,ax,ay),(px,py)) in enumerate(zip(add,pos)):
    S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay]);idx.setdefault(n,[]).append(base+k)
S2.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
for n,cs in idx.items(): d['anims'][f'hurtys_{n}']=[[SHI,c,t] for c,t in zip(cs,TK)]
d['src']['hurt_v2']='hurtys_<dir>: feel=ys hurt, designed recoil via PixelLab skeleton (tools/anim/apply_hurt_v2.py)'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s);print('ok',S2.size)
