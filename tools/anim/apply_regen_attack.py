# put the regenerated up/down 3-hit clips (character fb140a07, PixelLab animations v3) into test128: frames 1-8 of each 9-frame clip,
# feet re-anchored per frame to y=189, up hit3 recovery frames replaced by back-view frames; contact frames -> base ticks + FEELYS CT table
import json,glob,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/'
PICK={('down','south',1):('51',[1,2,3,4,5,6,7,8],3),('down','south',2):('51',[1,2,3,4,5,6,7,8],4),('down','south',3):('51',[1,2,3,4,5,6,7,8],4),
      ('up','north',1):('51',[1,2,3,4,5,6,7,8],2),('up','north',2):('52',[1,2,3,4,5,6,7,8],2),('up','north',3):('52',[1,2,3,4,4,2,1,0],2)}
d=json.load(open(T+'assets/anim/hero8.json'));SHI=d['sheets'].index('anim/hero8_atk.webp');sheet=Image.open(T+'assets/anim/hero8_atk.webp').convert('RGBA')
OC=[(14,5),(18,6),(27,9)]
def even(n,k):b=[n//k]*k;[b.__setitem__(i,b[i]+1) for i in range(n%k)];return b
add=[];CT={}
def put(im):
    a=np.array(im);op=a[...,3]>0;body=(a[...,3]>200)&(a[...,:3].min(-1)<150);fy=int(np.nonzero(body)[0].max());ys,xs=np.nonzero(op)
    x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
    add.append((im.crop((x0,y0,x1,y1)),128-x0,189-y0-(fy-189)));return len(d['cells'][SHI])+len(add)-1
for (dr,pd,h),(s,idx,c) in PICK.items():
    fs=sorted(glob.glob(f'_cand/r/hit{h}/{pd}_s{s}0{h}/*.png'));dur,hit=OC[h-1];t=even(hit,c)+even(dur-hit,8-c)
    d['anims'][f'hit{h}_{dr}']=[[SHI,put(Image.open(fs[i]).convert('RGBA')),t[j]] for j,i in enumerate(idx)]
    CT.setdefault(f'hit{h}',{})[dr]=c
    d['anims'][f'rec{h}_{dr}']=[d['anims'][f'hit{h}_{dr}'][-1][:2]+[12]] if h<3 else d['anims'].get(f'rec{h}_{dr}')
    if h==3:d['anims'][f'hold_{dr}']=[d['anims'][f'hit3_{dr}'][0][:2]+[1]]
d['anims']={k:v for k,v in d['anims'].items() if v is not None}
x=y=rowh=0;y0=sheet.height+1;pos=[]
for im,ax,ay in add:
    w,h=im.size
    if x+w>sheet.width:x=0;y+=rowh+1;rowh=0
    pos.append((x,y0+y));x+=w+1;rowh=max(rowh,h)
S2=Image.new('RGBA',(sheet.width,y0+y+rowh));S2.paste(sheet,(0,0))
for (im,ax,ay),(px,py) in zip(add,pos):S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay])
S2.save(T+'assets/anim/hero8_atk.webp','WEBP',lossless=True,quality=100,method=6)
d['src']['hit_ud']='regen_v1: up/down 3-hit regenerated from character fb140a07 (PixelLab animations v3, keep_first_frame, white crescent); down = seed 51xx, up = hit1 51xx / hit2-3 52xx, up hit3 recovery = back-view frames'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
old="const CT={hit1:{down:4,up:3,right:4,left:4},hit2:{down:3,up:3,right:4,left:4},hit3:{down:5,up:2,right:4,left:4}};"
new="const CT={hit1:{down:%d,up:%d,right:4,left:4},hit2:{down:%d,up:%d,right:4,left:4},hit3:{down:%d,up:%d,right:4,left:4}};"%(CT['hit1']['down'],CT['hit1']['up'],CT['hit2']['down'],CT['hit2']['up'],CT['hit3']['down'],CT['hit3']['up'])
assert s.count(old)==1;s=s.replace(old,new)
open(T+'index.html','w',encoding='utf-8').write(s);print('added',len(add),CT)
