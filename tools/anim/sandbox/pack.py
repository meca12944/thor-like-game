# pack the hero frames for the left/right-only sandbox: idle/run/hurt from the game atlas (right), attacks from the new combo
# (hit1 = skeleton slash, hit2 = horizontal slash h2b, hit3 = Linette-style thrust). frames cropped, anchor = feet (128,189).
# usage: pack.py <atk3 clean dir> <thrust frames dir> <out dir>
import json,sys,os
from PIL import Image
cl,th,out=sys.argv[1:4];A='test128/assets/';H=json.load(open(A+'anim/hero8.json'));SH={}
def cell(s,c):
    if s not in SH: SH[s]=Image.open(A+H['sheets'][s]).convert('RGBA')
    x,y,w,h,ax,ay=H['cells'][s][c];im=Image.new('RGBA',(256,256));im.paste(SH[s].crop((x,y,x+w,y+h)),(128-ax,189-ay));return im
F=[];AN={}
def add(name,ims,ticks):
    AN[name]=[]
    for im,t in zip(ims,ticks): AN[name].append([len(F),t]);F.append(im)
for n in ('idle','run','hurt'): add(n,[cell(e[0],e[1]) for e in H['anims'][n+'_right']],[e[2] for e in H['anims'][n+'_right']])
L=lambda d,ix:[Image.open(f'{d}/{i:03d}.png').convert('RGBA') for i in ix]
add('hit1',L(cl+'/h1_e_s71',range(0,13)),[1,1,1,2,2,2,1,1,1,2,2,3,4])
add('hit2',L(cl+'/h2b_e_s74',range(1,15)),[2,2,1,1,1,1,1,2,2,2,2,2,3,4])
add('hit3',L(th,[6,7,8,8,7,6]),[2,2,14,1,4,4])
# shelf-pack cropped frames
cells=[];X=Y=RH=0;W=2048;crops=[]
for im in F:
    b=im.getbbox();c=im.crop(b);w,h=c.size
    if X+w>W: X=0;Y+=RH+1;RH=0
    cells.append([X,Y,w,h,128-b[0],189-b[1]]);crops.append((c,X,Y));X+=w+1;RH=max(RH,h)
sheet=Image.new('RGBA',(W,Y+RH));[sheet.paste(c,(x,y)) for c,x,y in crops]
os.makedirs(out,exist_ok=True);sheet.save(out+'/hero_lr.png',optimize=True)
json.dump({'cells':cells,'anims':AN,
  'hit':{'hit1':9,'hit2':6,'hit3':2},'cancel':{'hit1':10,'hit2':10,'hit3':5}},open(out+'/hero_lr.json','w'))
print(len(F),'frames',sheet.size)
