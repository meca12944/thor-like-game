# add the true front/back attacks (C = 3D-projected thrusts, D = front slash) to the sandbox atlas as sheet hero_ud.webp:
#   C: chit<n>_down / chit<n>_up ; D: dhit1 = slash, dhit2 = mirrored slash (backhand), dhit3 = C hit 3 (down/up thrust)
#   'udthr' = strike tick per clip. usage: pack_ud.py <ud dir (cl/<clip>/NNN.png)> <atlas json> <out png>
import json,sys,os
from PIL import Image,ImageOps
src,aj,op=sys.argv[1:4];A=json.load(open(aj))
if os.path.basename(op).replace('.png','.webp') in A['sheets']:
    i=A['sheets'].index(os.path.basename(op).replace('.png','.webp'));A['sheets'].pop(i);A['cells'].pop(i)
    A['anims']={k:v for k,v in A['anims'].items() if not k[:4] in('chit','dhit')}
TK={'h1':[1,1,2,2,2,1,1,3,3,3,2,2,2],'h2':[1,2,2,2,2,1,1,3,3,3,2,2,2,2],'h3':[1,2,2,2,3,3,1,1,4,4,4,4,3,3,3],'D':[1,1,2,2,2,1,1,2,2,2,2,2,2]}
HIT={'h1':9,'h2':10,'h3':14,'D':9}
CL={}
for v,d in (('s','down'),('n','up')):
    for n in (1,2,3): CL[f'chit{n}_{d}']=(f'C_{v}_h{n}',TK[f'h{n}'],HIT[f'h{n}'],0)
    CL[f'dhit1_{d}']=(f'D_{v}',TK['D'],HIT['D'],0);CL[f'dhit2_{d}']=(f'D_{v}',TK['D'],HIT['D'],1);CL[f'dhit3_{d}']=(f'C_{v}_h3',TK['h3'],HIT['h3'],0)
s=len(A['sheets']);cells=[];crops=[];X=Y=RH=0;W=2048;cache={}
A['udthr']={}
for k,(clip,T,hit,mir) in CL.items():
    A['anims'][k]=[]
    for i,t in enumerate(T):
        key=(clip,i,mir)
        if key not in cache:
            im=Image.open(f'{src}/cl/{clip}/{i:03d}.png').convert('RGBA');im=ImageOps.mirror(im) if mir else im;b=im.getbbox();c=im.crop(b);w,h=c.size
            if X+w>W: X=0;Y+=RH+1;RH=0
            cells.append([X,Y,w,h,128-b[0],189-b[1]]);crops.append((c,X,Y));X+=w+1;RH=max(RH,h);cache[key]=len(cells)-1
        A['anims'][k].append([s,cache[key],t])
    A['udthr'][k]=hit
sheet=Image.new('RGBA',(W,Y+RH));[sheet.paste(c,(x,y)) for c,x,y in crops];wp=op.replace('.png','.webp');sheet.save(wp,lossless=True,method=6)
A['sheets'].append(os.path.basename(wp));A['cells'].append(cells)
A['_doc']+=' | hero_ud.webp = true front/back attacks: chit (C, 3D-projected thrusts) and dhit (D, front slash x2 + C hit 3); udthr = strike tick'
json.dump(A,open(aj,'w'));print(len(cells),'frames',sheet.size)
