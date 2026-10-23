# run v4: right = mocap sprint (12 frames, skeleton from CMU 09_01), left = its mirror,
# down/up = in-game keys + PixelLab skeleton in-betweens (8 frames), head height matched, up scaled 0.9,
# bob (passing up 3px, contact down 2px) and a 1.5px side sway baked in. Sequences rotated so the
# passing frames line up with the side run (12-frame passing at 1 and 7).
import json,math,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';R='/home/user/thor-like-game/handoff/claude/run_v4/'
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_run.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
def fit(p,top,s,sx):
    im=Image.open(p).convert('RGBA');b=im.getbbox();im=im.crop(b);cx=128-b[0]
    if s!=1:im=im.resize((round(im.width*s),round(im.height*s)),Image.NEAREST);cx*=s
    o=Image.new('RGBA',(256,256));o.paste(im,(round(128-cx)+sx,top),im);return o
def ud(dr,bobs,s,start):
    fs=[];[fs.extend([f'{R}{dr}/key{i}.png',f'{R}{dr}/mid{i}.png']) for i in range(4)]
    out=[]
    for k in range(8):
        j=(k+start)%8;out.append(fit(fs[j],70+bobs[j],s,round(1.5*math.sin(k/8*2*math.pi))))
    return out
side=[Image.open(f'{R}side/{i:03d}.png').convert('RGBA') for i in range(12)]
clips={'run_right':side,'run_left':[f.transpose(Image.FLIP_LEFT_RIGHT) for f in side],
       'run_down':ud('down',[-3,0,2,0,-3,0,2,0],1.0,7),'run_up':ud('up',[2,0,-3,0,2,0,-3,0],0.9,1)}
add=[]
for n,fr in clips.items():
    for im in fr:
        a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
        add.append((n,im.crop((x0,y0,x1,y1)),128-x0,189-y0))
W=sheet.width;x=0;y=sheet.height+1;rowh=0;pos=[]
for n,im,ax,ay in add:
    if x+im.width>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=im.width+1;rowh=max(rowh,im.height)
S2=Image.new('RGBA',(W,y+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI]);idx={}
for k,((n,im,ax,ay),(px,py)) in enumerate(zip(add,pos)):
    S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay]);idx.setdefault(n,[]).append(base+k)
S2.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
for n,cs in idx.items():
    t=3 if len(cs)==12 else 4;d['anims'][n]=[[SHI,c,t] for c in cs]
d['src']['run_v4']='run v4: side = CMU mocap sprint via PixelLab skeleton (12f, left mirrored); down/up = in-game keys + skeleton in-betweens (8f), see tools/anim/apply_run_v4.py'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s);print('ok',{n:len(c) for n,c in idx.items()},S2.size)
