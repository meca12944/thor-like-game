# run_down = lean edit (outB 004-007, 4-frame loop), run_left = mirror of the in-game run_right; down run legs cross 20% faster (own gait phase hero.gpd)
import json,numpy as np
from PIL import Image,ImageOps
T='/home/user/thor-like-game/test128/';L='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/move/lean/outB/'
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_run.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
add=[]
ims=[Image.open(L+f'{i:03d}.png').convert('RGBA') for i in (4,5,6,7)]
fy=[np.nonzero((np.array(i)[...,3]>200)&(np.array(i)[...,:3].min(-1)<150))[0].max() for i in ims];off=int(np.median(fy))-189
for im in ims:
    a=np.array(im);ys,xs=np.nonzero(a[...,3]>0);x0,x1,y0,y1=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1;add.append(('down',im.crop((x0,y0,x1,y1)),128-x0,189-y0+off))
for e in d['anims']['run_right']:
    x,y,w,h,ax,ay=d['cells'][e[0]][e[1]];im=ImageOps.mirror(sheet.crop((x,y,x+w,y+h)));add.append(('left',im,w-1-ax+1,ay))
x=0;y0=sheet.height+1;rowh=0;pos=[];yy=0
for _,im,ax,ay in add:
    if x+im.width>sheet.width:x=0;yy+=rowh+1;rowh=0
    pos.append((x,y0+yy));x+=im.width+1;rowh=max(rowh,im.height)
S2=Image.new('RGBA',(sheet.width,y0+yy+rowh));S2.paste(sheet,(0,0));base=len(d['cells'][SHI])
for (_,im,ax,ay),(px,py) in zip(add,pos):S2.paste(im,(px,py));d['cells'][SHI].append([px,py,im.width,im.height,ax,ay])
S2.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
t=d['anims']['run_right'][0][2]
d['anims']['run_down']=[[SHI,base+i,t] for i in range(4)]
d['anims']['run_left']=[[SHI,base+4+i,e[2]] for i,e in enumerate(d['anims']['run_right'])]
d['gait']['downRunMul']=1.2
d['src']['move_down']='move_v2: walk_down = s6102; run_down = Ys8 sprint s7102 + PixelLab lean edit (4 frames), legs x1.2; run_left = mirror of run_right'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
def rep(o,n):
    global s
    assert s.count(o)==1,o[:60];s=s.replace(o,n)
rep("if(hero.moving||hero.skid)hero.gp=((hero.gp||0)+sp*dt/(hero.run?H8T.runCyc:H8T.walkCyc))%1",
    "if(hero.moving||hero.skid){hero.gp=((hero.gp||0)+sp*dt/(hero.run?H8T.runCyc:H8T.walkCyc))%1;hero.gpd=((hero.gpd||0)+sp*dt*((H8&&H8.gait&&H8.gait.downRunMul)||1)/(hero.run?H8T.runCyc:H8T.walkCyc))%1;}")
rep("const L=A(h.run||(touchRun&&h.moving)?'run':'walk');e=L[Math.floor((h.gp||0)*L.length)%L.length]",
    "const R=h.run||(touchRun&&h.moving),L=A(R?'run':'walk');e=L[Math.floor(((R&&d==='down'?h.gpd:h.gp)||0)*L.length)%L.length]")
open(T+'index.html','w',encoding='utf-8').write(s);print('ok',len(add),'off',off)
