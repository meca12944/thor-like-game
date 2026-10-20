# pack every clip the showcase plays into a hero8-style atlas for the sandbox: sheets + json (cells [x,y,w,h,ax,ay], anims name_dir = [[sheet,cell,ticks]])
import os,json
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
os.environ['ATKDIR']='a5';exec(open(P+'dg/showcase.py').read().split('SCRIPT=')[0])
from PIL import Image
DIRS=['right','left','down','downl','up','upl']
names=[]
for m in ['idle','walk','run','dash','hit1','hit2','hit3']: names+= [(m,d) for d in DIRS]
for m in ['hurt','death','cast']: names+= [(m,d) for d in ('right','left')]
frames=[];anims={}
for m,d in names:
    L=[]
    for im,t in clip(m,d):
        bb=im.getbbox()
        if not bb: im=Image.new('RGBA',(256,256));bb=(127,188,129,190)
        c=im.crop(bb);frames.append((c,128-bb[0],189-bb[1]));L.append([len(frames)-1,t])
    anims[f'{m}_{d}']=L
W=2048;sheets=[];cells=[];x=y=rowh=0;cur=[]
def flush():
    global cur
    if not cur: return
    H=max(py+im.height for im,px,py in cur);S=Image.new('RGBA',(W,H))
    for im,px,py in cur: S.paste(im,(px,py))
    sheets.append(S);cur=[]
sid=0;sheetcells=[[]];idx={}
for i,(im,ax,ay) in enumerate(frames):
    if x+im.width>W: x=0;y+=rowh+1;rowh=0
    if y+im.height>2048: flush();sid+=1;sheetcells.append([]);x=y=rowh=0
    cur.append((im,x,y));sheetcells[sid].append([x,y,im.width,im.height,ax,ay]);idx[i]=(sid,len(sheetcells[sid])-1);x+=im.width+1;rowh=max(rowh,im.height)
flush()
out={'_doc':'hero sandbox atlas (built from dg/showcase.py clips): side = in-game (+fixes), diagonal = 3/4 clips, left variants mirrored','sheets':[],'cells':sheetcells,'anims':{}}
for k,L in anims.items(): out['anims'][k]=[[*idx[f],t] for f,t in L]
os.makedirs(P+'sandbox/assets',exist_ok=True)
for i,S in enumerate(sheets):
    n=f'hero_sbx_{i}.webp';S.save(P+'sandbox/assets/'+n,'WEBP',lossless=True,quality=100,method=6);out['sheets'].append(n)
json.dump(out,open(P+'sandbox/assets/hero_sbx.json','w'),separators=(',',':'))
print(len(frames),'frames',len(sheets),'sheets',[os.path.getsize(P+'sandbox/assets/'+n)//1024 for n in out['sheets']],'KB')
