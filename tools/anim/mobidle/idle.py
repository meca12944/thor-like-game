# Idle "breathing" loops for the static monster sheets (art/mobs/mobs_0N.jpg 3x2 cells, left = idle pose; town/assets_src/world/mobs_field.jpg
# 5 in a row). Each idle pose is keyed out of the #FF00FF ground and animated in code with pixel-safe moves (whole-row resampling,
# no blur): breathe = small squash/stretch about the feet, blob = stronger squash, float = bob up and down (flyers/ghosts/jelly),
# sway = top leans side to side (plants/trees), hover = float + slight breathe. 8 frames per loop.
# usage: idle.py <sheet dir> <INDEX.md> <out dir>
import sys,os,re,json,math,numpy as np
from PIL import Image
from scipy import ndimage
src,index,out=sys.argv[1:4];os.makedirs(out+'/sheets',exist_ok=True)
def key(im):
    a=np.array(im.convert('RGB')).astype(int);r,g,b=a[...,0],a[...,1],a[...,2]
    bg=np.median(np.concatenate([a[:8].reshape(-1,3),a[-8:].reshape(-1,3)]),0)   # ground colour from the top/bottom strips (magenta or pink)
    mag=(np.abs(a-bg).sum(-1)<120)|((r>150)&(b>110)&(g<110)&(r-g>90)&(b-g>40))   # ground incl. jpeg fringe
    al=(~mag).astype(np.uint8)*255;rgba=np.dstack([a.astype(np.uint8),al]);return rgba,~mag
def pick(mask,x0,x1,y0,y1):
    sub=mask[y0:y1,x0:x1].copy();w=x1-x0;c=sub.sum(0);lo,hi=int(w*.38),int(w*.62);cut=lo+int(np.argmin(c[lo:hi]));sub[:,cut:]=False   # idle = left of the emptiest column mid-cell
    lab,n=ndimage.label(sub,structure=np.ones((3,3)))
    if n==0:return None
    sz=ndimage.sum(sub,lab,range(1,n+1));cm=ndimage.center_of_mass(sub,lab,range(1,n+1))
    mid=(x1-x0)/2;cands=[i for i in range(n) if cm[i][1]<mid and sz[i]>200]
    if not cands:return None
    big=max(cands,key=lambda i:sz[i]);ys,xs=np.nonzero(lab==big+1);bx0,bx1,by0,by1=xs.min(),xs.max(),ys.min(),ys.max()
    keep=lab==big+1
    for i in range(n):                                  # small bits touching the main body (antennae, sparkles) join it
        if i==big or sz[i]>sz[big]:continue
        yy,xx=np.nonzero(lab==i+1)
        if xx.min()>=bx0-6 and xx.max()<=bx1+6 and yy.min()>=by0-6 and yy.max()<=by1+6 and cm[i][1]<mid:keep|=lab==i+1
    ys,xs=np.nonzero(keep);return keep,(x0+xs.min(),y0+ys.min(),x0+xs.max()+1,y0+ys.max()+1),(x0,y0)
# categories from the name (Korean/English)
CAT=[('float',r'bat|vulture|seagull|wasp|jelly|ghost|wisp|spirit|bird|owl|eagle|fly|moth|bee|butterfly|phantom|wraith|해파리|망령|정령|독수리|갈매기|박쥐|말벌|유령|새'),
     ('blob',r'slime|ooze|blob|puffer|슬라임|복어'),
     ('sway',r'sprout|tree|plant|flower|cactus|vine|kelp|coral|mushroom|새싹|나무|덩굴|선인장|산호|버섯|꽃'),
     ('still',r'statue|golem|jar|slab|armor|석상|골렘|항아리|석판|갑옷')]
OVR={'a1_08_spirit_sprout':'sway','a6_08_pirate_parrot':'breathe','a6_02_seagull':'breathe','a3_04_bald_vulture':'breathe','a9_06_void_eye':'float','a2_06_glow_worm':'breathe'}
def cat(name):
    for k,v in OVR.items():
        if k in name:return v
    for c,rx in CAT:
        if re.search(rx,name,re.I):return c
    return 'breathe'
def frames(rgba,mask,bbox,kind,N=8):
    x0,y0,x1,y1=bbox;spr=rgba[y0:y1,x0:x1].copy();spr[...,3]=np.where(mask[y0:y1,x0:x1],255,0);h,w=spr.shape[:2]
    P=12;out=[]
    for f in range(N):
        t=2*math.pi*f/N;canvas=np.zeros((h+2*P,w+2*P,4),np.uint8)
        if kind=='float':sy,sx,dy,shear=1+.012*math.sin(t),1,round(-4*math.sin(t)),0
        elif kind=='blob':sy,sx,dy,shear=1+.05*math.sin(t),1-.035*math.sin(t),0,0
        elif kind=='sway':sy,sx,dy,shear=1+.01*math.sin(2*t),1,0,3*math.sin(t)
        elif kind=='still':sy,sx,dy,shear=1+.006*math.sin(t),1,0,0
        else:sy,sx,dy,shear=1+.022*math.sin(t),1-.01*math.sin(t),0,0
        nh=max(1,round(h*sy));nw=max(1,round(w*sx))
        ry=np.clip((np.arange(nh)*h/nh).astype(int),0,h-1);rx=np.clip((np.arange(nw)*w/nw).astype(int),0,w-1)
        s2=spr[ry][:,rx]
        top=P+(h-nh)+dy;left=P+(w-nw)//2
        for yy in range(nh):
            off=round(shear*(1-yy/max(1,nh-1)))        # top row leans most, feet stay
            Y=top+yy
            if 0<=Y<canvas.shape[0]:
                row=s2[yy];m=row[:,3]>0;xs=np.arange(nw)+left+off;ok=(xs>=0)&(xs<canvas.shape[1])&m;canvas[Y,xs[ok]]=row[ok]
        out.append(canvas)
    return out
# monster list from INDEX.md tables: per sheet, rows of (cell, id, name)
MON=[];sheet=None
for line in open(index,encoding='utf-8'):
    m=re.match(r'## (mobs_\d+)\.jpg',line)
    if m:sheet=m.group(1);continue
    m=re.match(r'\| (\d) .*?\| `([^`]+)` \| ([^|]+)\|',line)
    if m and sheet:MON.append((sheet,int(m.group(1)),m.group(2),m.group(3).strip()))
MAN=[]
for sheet,cell,mid,name in MON:
    im=Image.open(f'{src}/{sheet}.jpg');rgba,mask=key(im);W,H=im.size;c=(cell-1)%3;r=(cell-1)//3
    got=pick(mask,int(c*W/3),int((c+1)*W/3),int(r*H/2),int((r+1)*H/2))
    if not got:print('MISS',mid);continue
    keep,bbox,_=got;m2=np.zeros_like(mask);m2[bbox[1]:bbox[3],bbox[0]:bbox[2]]=keep[bbox[1]-int(r*H/2):bbox[3]-int(r*H/2),bbox[0]-int(c*W/3):bbox[2]-int(c*W/3)]
    kind=cat(mid+' '+name);fr=frames(rgba,m2,bbox,kind)
    strip=Image.new('RGBA',(fr[0].shape[1]*len(fr),fr[0].shape[0]))
    for i,f in enumerate(fr):strip.paste(Image.fromarray(f),(i*f.shape[1],0))
    strip.save(f'{out}/sheets/{mid}.png');MAN.append({'id':mid,'name':name,'kind':kind,'w':fr[0].shape[1],'h':fr[0].shape[0],'n':len(fr)})
# field sheet: 5 monsters in one row, single pose each
FIELD=[('field_mushroom','독버섯 (Poison Mushroom)'),('field_horned_rabbit','뿔토끼 (Horned Rabbit)'),('field_wasp','말벌 (Wasp)'),('field_boar','멧돼지 (Boar)'),('field_scarecrow','호박 허수아비 (Pumpkin Scarecrow)')]
fp=f'{src}/mobs_field.jpg'
if os.path.exists(fp):
    im=Image.open(fp);rgba,mask=key(im);lab,n=ndimage.label(mask,structure=np.ones((3,3)));sz=ndimage.sum(mask,lab,range(1,n+1))
    big=sorted([i for i in range(n) if sz[i]>2000],key=lambda i:ndimage.center_of_mass(mask,lab,i+1)[1])[:5]
    for (mid,name),i in zip(FIELD,big):
        ys,xs=np.nonzero(lab==i+1);bbox=(xs.min(),ys.min(),xs.max()+1,ys.max()+1);m2=lab==i+1;kind=cat(mid+' '+name)
        fr=frames(rgba,m2,bbox,kind);strip=Image.new('RGBA',(fr[0].shape[1]*len(fr),fr[0].shape[0]))
        for j,f in enumerate(fr):strip.paste(Image.fromarray(f),(j*f.shape[1],0))
        strip.save(f'{out}/sheets/{mid}.png');MAN.append({'id':mid,'name':name,'kind':kind,'w':fr[0].shape[1],'h':fr[0].shape[0],'n':len(fr)})
json.dump(MAN,open(out+'/manifest.json','w'),ensure_ascii=False,indent=0)
from collections import Counter;print(len(MAN),'monsters',Counter(m['kind'] for m in MAN))
