# hero side hit1/hit2 = thrust v1 (owner OK 2026-10-20): 8 frames each from handoff/claude/hero_attack_thrust_v1/frames (lance streak baked
# on the thrust frames), appended to hero8_atk.webp; hit*_left = mirrored. Ticks and frame count unchanged, so H8.combo timings stay.
import json,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';R='/home/user/thor-like-game/handoff/claude/hero_attack_thrust_v1/frames/'
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_atk.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
add=[]
for h in ['hit1','hit2']:
    for side in ['right','left']:
        for i in range(8):
            im=Image.open(R+f'{h}_{i:02d}.png').convert('RGBA')
            if side=='left': im=im.transpose(Image.FLIP_LEFT_RIGHT)
            a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
            add.append((f'{h}_{side}',im.crop((x0,y0,x1,y1)),128-x0,189-y0))
W=sheet.width;x=0;y=sheet.height+1;rowh=0;pos=[]
for n,im,ax,ay in add:
    if x+im.width>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=im.width+1;rowh=max(rowh,im.height)
S2=Image.new('RGBA',(W,y+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI]);idx={}
for k,((n,im,ax,ay),(px,py)) in enumerate(zip(add,pos)):
    S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay]);idx.setdefault(n,[]).append(base+k)
S2.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
for n,cs in idx.items():
    old=d['anims'][n];d['anims'][n]=[[SHI,c,e[2]] for c,e in zip(cs,old)]
d['src']['thrust_v1']='hit1/hit2 side = thrust v1 (tools/anim/apply_thrust_v1.py), left mirrored'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s);print('ok',S2.size,{n:len(c) for n,c in idx.items()})
