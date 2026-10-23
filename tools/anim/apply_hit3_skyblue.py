# test128 town demo: hit3 = thin sky-blue trail (owner 2026-10-20 "하늘색으로 세팅"). Cells come from the sandbox atlas
# (test128/sandbox/assets, built by tools/anim/hit3_skyblue_build.py: original crescent, 40% thinner, 5 px past the blade tip,
# light sky blue at 62% alpha; ↘/↗ rebuilt from the clean diagonal frames). Copied to anim/hero8_h3s.webp; ticks unchanged.
import json
from PIL import Image
T='/home/user/thor-like-game/test128/';S=T+'sandbox/assets/'
d=json.load(open(T+'assets/anim/hero8.json'));s=json.load(open(S+'hero_sbx.json'));ssh={}
crops=[];names={}
for dr in ['right','left','down','up']:
    L=[]
    for e in s['anims'][f'hit3s_{dr}']:
        if e[0] not in ssh:ssh[e[0]]=Image.open(S+s['sheets'][e[0]]).convert('RGBA')
        x,y,w,h,ax,ay=s['cells'][e[0]][e[1]];crops.append((ssh[e[0]].crop((x,y,x+w,y+h)),ax,ay));L.append((len(crops)-1,e[2]))
    names[dr]=L
W=2048;x=y=rowh=0;pos=[]
for im,ax,ay in crops:
    if x+im.width>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=im.width+1;rowh=max(rowh,im.height)
sh=Image.new('RGBA',(W,y+rowh))
for (im,_,_),p in zip(crops,pos):sh.paste(im,p)
sp='anim/hero8_h3s.webp'
if sp not in d['sheets']:d['sheets'].append(sp);d['cells'].append([])
SHI=d['sheets'].index(sp);d['cells'][SHI]=[[px,py,im.width,im.height,int(ax),int(ay)] for (im,ax,ay),(px,py) in zip(crops,pos)]
sh.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
for dr,L in names.items():
    old=d['anims'][f'hit3_{dr}'];assert len(old)==len(L)
    d['anims'][f'hit3_{dr}']=[[SHI,c,o[2]] for (c,t),o in zip(L,old)]
d['src']['hit3_skyblue']='hit3 = thin sky-blue trail 5px past the blade tip (tools/anim/apply_hit3_skyblue.py)'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s2=open(T+'index.html',encoding='utf-8').read();a=s2.index("/*H8*/const H8=");b=s2.index(";/*/H8*/");pre=s2[a:b];k=pre.index('?null:')+6;s2=s2[:a]+pre[:k]+js+s2[b:]
open(T+'index.html','w',encoding='utf-8').write(s2);print('ok',sh.size)
