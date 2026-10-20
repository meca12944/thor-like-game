# hero running jump v1 (owner OK 2026-10-20): 10 side frames from handoff/claude/hero_runjump_v1/frames (CMU 127_25 skeleton ->
# PixelLab animate-with-skeleton-v3, palette locked, feet on y=189), appended to hero8_jump.webp as rjump_right / rjump_left (mirrored).
# Played over the jump time by progress (heroCell8), so the 3-tick values are only relative weights.
import json,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';R='/home/user/thor-like-game/handoff/claude/hero_runjump_v1/frames/'
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_jump.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
add=[]
for side in ['right','left']:
    for i in range(10):
        im=Image.open(R+f'rjump_{i:02d}.png').convert('RGBA')
        if side=='left':im=im.transpose(Image.FLIP_LEFT_RIGHT)
        a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
        add.append((f'rjump_{side}',im.crop((x0,y0,x1,y1)),128-x0,189-y0))
W=max(sheet.width,sum(im.width+1 for _,im,_,_ in add[:10]));x=0;y=sheet.height+1;rowh=0;pos=[]
for n,im,ax,ay in add:
    if x+im.width>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=im.width+1;rowh=max(rowh,im.height)
S2=Image.new('RGBA',(W,y+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI]);idx={}
for k,((n,im,ax,ay),(px,py)) in enumerate(zip(add,pos)):
    S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay]);idx.setdefault(n,[]).append(base+k)
S2.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
for n,cs in idx.items():d['anims'][n]=[[SHI,c,3] for c in cs]
d['src']['runjump_v1']='rjump_right/left = running jump v1 (tools/anim/apply_runjump_v1.py), CMU 127_25, left mirrored'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s);print('ok',S2.size,{n:len(c) for n,c in idx.items()})
