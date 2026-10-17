"""World/field/dungeon asset pipeline (area 1+).
Sources (assets_src/world/*_raw.jpg = generated 16-bit sheets on #FF00FF, mob/boss/champion sheets in src/ and art/)
-> assets/world/{tiles_field,tiles_dungeon,props,mobs,hero_s}.png + world_atlas.json
Run:  python3 tools/world_assets.py      (idempotent)
Scale (DQ6-like): 16x16 tiles, hero ~16x26, trees 2-3 hero heights, doors ~1.5 hero heights.
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'   # town/ (or the town-demo working copy)
_up=os.path.dirname(os.path.dirname(R))+'/'
REPO=os.environ.get('THOR_REPO') or (_up if os.path.isdir(_up+'art') else '/workspace/thor-like-game/')  # repo root (art/, data/)
SRC=R+'assets_src/world/'; OUT=R+'assets/world/'
os.makedirs(OUT,exist_ok=True)

def bgmask(a):
    r,g,b=a[...,0].astype(int),a[...,1].astype(int),a[...,2].astype(int)
    return (g<80)&(r>140)&(b>85)&((r-g)>110)&((b-g)>60)

def rgba(path):
    a=np.array(Image.open(path).convert('RGB'))
    m=bgmask(a)
    m=ndimage.binary_opening(~m,iterations=1)  # content mask
    out=np.dstack([a,(m*255).astype(np.uint8)])
    return out

def bands(prof,thr,minlen=8):
    on=prof>thr;res=[];s=None
    for i,v in enumerate(list(on)+[False]):
        if v and s is None:s=i
        if not v and s is not None:
            if i-s>=minlen:res.append((s,i))
            s=None
    return res

def slice_grid(path,cols,rows,inset=4):
    a=rgba(path);m=a[...,3]>0
    cb=bands(m.mean(0),0.25);rb=bands(m.mean(1),0.25)
    # merge spurious: keep the 'cols' widest
    cb=sorted(sorted(cb,key=lambda b:b[1]-b[0])[-cols:]);rb=sorted(sorted(rb,key=lambda b:b[1]-b[0])[-rows:])
    cells={}
    for j,(y0,y1) in enumerate(rb):
        for i,(x0,x1) in enumerate(cb):
            # square crop centred in the cell
            w,h=x1-x0-2*inset,y1-y0-2*inset;s=min(w,h)
            cx,cy=(x0+x1)//2,(y0+y1)//2
            c=a[cy-s//2:cy-s//2+s,cx-s//2:cx-s//2+s]
            cells[(i,j)]=Image.fromarray(c)
    return cells

def tile16(im,full=True):
    t=im.convert('RGBA').resize((16,16),Image.LANCZOS)
    if full:
        t=t.convert('RGB').convert('RGBA')
    else:
        A=np.array(t);A[...,3]=np.where(A[...,3]>110,255,0);t=Image.fromarray(A)
    return t

def comps(path,minarea=1500,box=None):
    a=rgba(path)
    if box: x0,y0,x1,y1=box;a=a[y0:y1,x0:x1]
    m=a[...,3]>0
    lab,n=ndimage.label(ndimage.binary_dilation(m,iterations=6))
    objs=[]
    for k,sl in enumerate(ndimage.find_objects(lab)):
        ys,xs=sl;area=(lab[sl]==k+1).sum()
        if area<minarea:continue
        sub=a[sl].copy();sub[...,3]=np.where(lab[sl]==k+1,sub[...,3],0)
        objs.append(((xs.start,ys.start),Image.fromarray(sub)))
    objs.sort(key=lambda o:(round(o[0][1]/150),o[0][0]))
    return objs

def fit(im,h=None,w=None):
    W,H=im.size
    if h: w2=max(1,round(W*h/H));h2=h
    else: h2=max(1,round(H*w/W));w2=w
    t=im.resize((w2,h2),Image.LANCZOS)
    A=np.array(t);A[...,3]=np.where(A[...,3]>120,255,0)
    r,g,b=A[...,0].astype(int),A[...,1].astype(int),A[...,2].astype(int)
    spill=(r-g>70)&(b-g>40)&(g<110)            # magenta fringe / pink drop-shadow from the #FF00FF sheets
    A[...,3]=np.where(spill,0,A[...,3])
    return Image.fromarray(A)

def crop_alpha(im):
    bb=im.getbbox();return im.crop(bb) if bb else im

atlas={'tile':16,'sheets':{}}
# ---------------- field tiles: 8x6 grid ----------------
F=slice_grid(SRC+'tiles_field_raw.jpg',8,6)
FIELD_NAMES={ # (col,row) -> name  (see assets_src/world/tiles_field_raw.jpg)
 (0,0):'grass',(1,0):'grass_flowers',(2,0):'grass_tuft',(3,0):'grass_tuft2',(4,0):'grass_dark',
 (0,1):'dirt',(1,1):'dirt_pebble',(2,1):'dirt2',(3,1):'dirt3',
 (0,2):'water',(1,2):'water2',(2,2):'water3',(3,2):'water4',
 (1,3):'cliff',(2,3):'cliff_rock',(3,3):'cliff2',
 (2,4):'stones',(3,4):'stones2',(4,4):'tallgrass',(5,4):'tallgrass2',(6,4):'bush_t',(7,4):'bush_flower_t',
 (0,5):'paving',(1,5):'paving2',(2,5):'sand',(3,5):'sand2',(4,5):'mud',(5,5):'soil',(6,5):'forest_floor',(7,5):'forest_floor2',
 (0,4):'bridge_h',(1,4):'bridge_h2',
}
def build_sheet(cells,names,fname,extra=None):
    items=list(names.items())+(extra or [])
    cols=8;rows=(len(items)+cols-1)//cols
    sh=Image.new('RGBA',(cols*16,rows*16),(0,0,0,0));idx={}
    for k,(key,name) in enumerate(items):
        t=key if isinstance(key,Image.Image) else tile16(cells[key])
        sh.paste(t,((k%cols)*16,(k//cols)*16));idx[name]=k
    sh.save(OUT+fname,optimize=True)
    return {'src':'world/'+fname,'cols':cols,'index':idx}

# derived field tiles (procedural edges so paths/water/cliffs join cleanly)
def mix(a,b,mask):
    A=np.array(a).astype(float);B=np.array(b).astype(float);m=mask[...,None]
    return Image.fromarray((A*(1-m)+B*m).astype(np.uint8))
g=tile16(F[(0,0)]);d=tile16(F[(0,1)]);w=tile16(F[(0,2)]);snd=tile16(F[(2,5)]);cl=tile16(F[(1,3)])
yy,xx=np.mgrid[0:16,0:16]
rng=np.random.RandomState(3)
jit=rng.rand(16,16)*2.2
extra=[]
for nm,cond in [('n',yy<4+jit),('s',yy>11-jit),('w',xx<4+jit),('e',xx>11-jit)]:
    extra.append((mix(w,snd,cond.astype(float)),'water_shore_'+nm))   # water tile with sand rim on side nm
# snow + dark grass variants for world map
def tint(im,mul,add=(0,0,0)):
    A=np.array(im).astype(float);A[...,:3]=np.clip(A[...,:3]*np.array(mul)+np.array(add),0,255);return Image.fromarray(A.astype(np.uint8))
gray=lambda im:Image.fromarray(np.dstack([np.repeat(np.array(im.convert('L'))[...,None],3,2),np.array(im)[...,3]]))
extra.append((tint(gray(g),(1.15,1.2,1.3),(40,40,50)),'snow'))
extra.append((tint(g,(0.85,0.62,1.0),(18,0,22)),'grass_cursed'))
extra.append((tint(snd,(1.0,0.85,0.6)),'desert'))
extra.append((tint(d,(0.7,0.45,0.35),(20,0,0)),'ash'))
extra.append((tint(w,(0.6,0.7,1.0)),'water_deep'))
extra.append((tint(w,(0.6,1.05,1.0),(0,10,0)),'water_shallow'))
atlas['sheets']['field']=build_sheet(F,FIELD_NAMES,'tiles_field.png',extra)

# ---------------- dungeon tiles ----------------
D=slice_grid(SRC+'tiles_dungeon_raw.jpg',8,6)
DUN_NAMES={(0,0):'floor',(1,0):'floor_crack',(2,0):'floor_moss',(3,0):'floor_moss2',(4,0):'floor_crystal',(7,0):'floor2',
 (0,1):'wall',(1,1):'wall_moss',(2,1):'wall_vine',(3,1):'wall_vine2',(4,1):'wall_crack',(5,1):'wall_crack2',(6,1):'wall_moss2',
 (0,2):'walltop',(1,2):'walltop2',(4,2):'walltop3',(5,2):'walltop4',
 (0,3):'door',(1,3):'gate',(2,3):'doorway',(3,3):'stairs_down',(4,3):'stairs_up',(5,3):'plate_up',(6,3):'plate_down',(7,3):'spikes',
 (0,4):'torch',(1,4):'torch_off',(5,4):'pit',(6,4):'key_floor',
 (0,5):'carpet',(1,5):'channel',(2,5):'rune',(3,5):'grate'}
# walltop: darken a floor sample so top-of-wall reads as a solid mass in 3/4 view
wt=tint(tile16(D[(0,2)]),(0.75,0.75,0.8))
atlas['sheets']['dungeon']=build_sheet(D,DUN_NAMES,'tiles_dungeon.png',[(wt,'walltop_dark'),(tint(tile16(D[(0,0)]),(0.4,0.4,0.5)),'void')])

# ---------------- props (sprites with alpha, anchored bottom-centre) ----------------
props={};spr_imgs=[]
P=comps(SRC+'props_field_raw.jpg',minarea=3000)
PN=[('tree',56),('pine',58),('stump',20),('boulder',28),('rocks',16),('bush',20),('sign',20),('chest',16),('chest_open',16),('fence',16),('mushrooms',18),('rail',22)]
for (pos,im),(nm,h) in zip(P,PN):
    spr_imgs.append((nm,fit(crop_alpha(im),h=h)))
# dungeon props from the dungeon sheet: torch, crystal, pillar, rubble, tablet (alpha-keyed cell contents)
def cellsprite(c,h):
    A=np.array(c);return fit(crop_alpha(Image.fromarray(A)),h=h)
for key,nm,h in [((2,4),'crystal',22),((3,4),'pillar',30),((4,4),'rubble',16),((7,4),'tablet',20)]:
    spr_imgs.append((nm,cellsprite(D[key],h)))
# door sprites ~1.5 hero heights (hero ~26px) -> 36px tall, 32 wide
for key,nm in [((0,3),'door_big'),((1,3),'gate_big'),((2,3),'doorway_big')]:
    c=D[key].convert('RGBA').resize((32,36),Image.LANCZOS).convert('RGB').convert('RGBA');spr_imgs.append((nm,c))
# ---------------- mobs ----------------
MOB=[]
mf=comps(SRC+'mobs_field.jpg',minarea=4000)
for (pos,im),(nm,h) in zip(mf,[('mushroom',20),('rabbit',22),('wasp',20),('boar',20),('scarecrow',30)]):
    MOB.append((nm,fit(crop_alpha(im),h=h)))
m1=comps(REPO+'art/mobs/mobs_01.jpg',minarea=3000,box=(0,0,1280,330))
# expected order: slime idle, slime attack(+blobs), squirrel idle, squirrel attack(+acorn), sprout idle, sprout attack(+roots)
m1=[o for o in m1]
names1=['slime','slime_atk','squirrel','squirrel_atk','sprout','sprout_atk']
for (pos,im),nm in zip(m1[:6],names1):
    MOB.append((nm,fit(crop_alpha(im),h=18 if 'slime' in nm else 22)))
def gridcell(path,cols,rows,i,j):
    a=Image.open(path).convert('RGB');W,H=a.size;cw,ch=W//cols,H//rows
    tmp='/tmp/wld/_cell.png';a.crop((i*cw,j*ch,(i+1)*cw,(j+1)*ch)).save(tmp)
    o=comps(tmp,minarea=3000);o.sort(key=lambda t:-(t[1].size[0]*t[1].size[1]));return crop_alpha(o[0][1])
os.makedirs('/tmp/wld',exist_ok=True)
C1=REPO+'art/champions/champ01.jpg';C2=REPO+'art/champions/champ02.jpg'
MOB.append(('champ_boar',fit(gridcell(C1,4,3,3,1),h=38)))
MOB.append(('champ_boar_run',fit(gridcell(C1,4,3,1,0),h=38)))
MOB.append(('champ_boar_rage',fit(gridcell(C1,4,3,0,2),h=40)))
MOB.append(('champ_wasp',fit(gridcell(C2,4,3,0,0),h=40)))
MOB.append(('champ_wasp_atk',fit(gridcell(C2,4,3,1,1),h=40)))
bossim=comps(SRC+'boss_1_2.jpg',minarea=20000,box=(0,0,640,720))
MOB.append(('golem',fit(crop_alpha(max(bossim,key=lambda o:o[1].size[0]*o[1].size[1])[1]),h=72)))
spr_imgs+=MOB
# ---------------- small hero (from the town walk sheets) ----------------
spr=json.load(open(R+'assets/sprites.json'))
for d_ in ['down','up','right']:
    m=spr['hero_walk_'+d_];im=Image.open(R+'assets/'+m['src']).convert('RGBA')
    for f in range(m['n']):
        fr=im.crop((f*m['w'],0,(f+1)*m['w'],m['h']))
        spr_imgs.append(('hero_%s_%d'%(d_,f),fit(fr,h=27)))
# ---------------- field NPCs (town NPC art, shrunk to the DQ6 adult height ~26) ----------------
for nm,src in [('npc_bard','a_bard.png'),('npc_old','h_old.png')]:
    im=Image.open(R+'assets/npcs/'+src).convert('RGBA');spr_imgs.append((nm,fit(crop_alpha(im),h=26)))
# ---------------- pack sprite atlas (shelf) ----------------
W=512;x=y=0;rowh=0;rects={}
for nm,im in spr_imgs:
    if x+im.width>W:x=0;y+=rowh+1;rowh=0
    rects[nm]=[x,y,im.width,im.height];x+=im.width+1;rowh=max(rowh,im.height)
sheet=Image.new('RGBA',(W,y+rowh),(0,0,0,0))
for nm,im in spr_imgs:sheet.paste(im,tuple(rects[nm][:2]))
sheet.save(OUT+'sprites.png',optimize=True)
atlas['sprites']={'src':'world/sprites.png','rects':rects}
json.dump(atlas,open(OUT+'world_atlas.json','w'),ensure_ascii=False,indent=0)
# preview (x4)
for f in ['tiles_field.png','tiles_dungeon.png','sprites.png']:
    im=Image.open(OUT+f);bg=Image.new('RGBA',im.size,(40,40,60,255));bg.alpha_composite(im)
    bg.resize((im.width*3,im.height*3),Image.NEAREST).save('/tmp/wld/prev_'+f)
print('ok',len(rects),'sprites', {k:len(v['index']) for k,v in atlas['sheets'].items()})
