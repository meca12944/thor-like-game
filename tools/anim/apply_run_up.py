# run_up = cape-tightened edit (4 frames, each held 2 of 8 so the passing frames stay on 2 and 6), scaled 0.92 about the feet root so the head height matches the other runs
import json,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';U='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/move/up/out/';S=0.92
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_run.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
add=[]
for i in (0,2,4,6):
    im=Image.open(U+f'{i}.png').convert('RGBA');im=im.resize((round(256*S),round(256*S)),Image.NEAREST)
    a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1
    add.append((im.crop((x0,y0,x1,y1)),round(128*S)-x0,round(189*S)-y0))
x=0;y0=sheet.height+1;rowh=0;pos=[]
for im,ax,ay in add:pos.append((x,y0));x+=im.width+1;rowh=max(rowh,im.height)
S2=Image.new('RGBA',(sheet.width,y0+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI])
for (im,ax,ay),(px,py) in zip(add,pos):S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay])
S2.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
t=d['anims']['run_up'][0][2];d['anims']['run_up']=[[SHI,base+i,t] for i in (0,0,1,1,2,2,3,3)]
d['src']['move_up']='run_up = in-game run v2 (phase-aligned), cape tightened with PixelLab edit (4 frames), scaled 0.92'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s);print('ok')
