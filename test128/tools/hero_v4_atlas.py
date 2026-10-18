# hero_v4_atlas.py — PixelLab v3 character fb140a07 (v3gen_20261018) -> assets/anim/hero8_*.webp + hero8.json (H8 format, v3:1 v4:1, real 'left' dir)
# ONE PLACE per motion: SRC below. To swap a motion (e.g. hurt -> hurt_v2, dash -> dash_v2) change its path here, then re-run:
#   python3 tools/anim/hero_v4_atlas.py && python3 tools/anim/patch_hero_v4.py
# Source frames: <SRC[slot]>/<south|north|east|west>/NNN.png, 256x256 RGBA, 8 frames each. south=down north=up east=right west=left.
# Crop: each frame trimmed to its alpha bbox; anchor = FIXED feet root ROOT=(128,189) of the 256 canvas for every motion/dir/frame (no per-frame
# re-centering -> no jitter). Scale 1:1 (no resampling): new standing height 124 px (down) vs the current test128 hero 121 px (down) / 121 (right).
# Cast: new moves_v1/cast body frames; the old magic-circle fx layers (hero8_castfx.webp) are re-timed onto the new phases (S1/S2/S3 by skill slot).
# Guard + jump: no game input/mechanic -> shipped as anims guard_* / jump_* (debug preview: __game.heroPose('guard'|'jump')).
import json,os,glob,shutil,numpy as np
from PIL import Image
G='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; OUT='/workspace/town-demo/assets/anim'
OLDDIR='/workspace/town-demo/_backup_hero8_pre_v4_20261018/assets_anim'; OLD=json.load(open(OLDDIR+'/hero8.json'))
SRC={'idle':G+'/moves_v1/idle','walk':G+'/moves_v1/walk','run':G+'/moves_v1/run',
     'dash':G+'/moves_v1/dash',    # glide dash_v2 handled by another worker
     'hurt':G+'/moves_v1/hurt',    # <- to be redone (hurt_v2)
     'death':G+'/cast_death_guard_v2/death','cast':G+'/cast_death_guard_v2/cast','jump':G+'/moves_v1/jump',   # death v2 (9f, blood) + cast v2 (7f) approved 23:35; guard removed (owner)
     'hit1':G+'/combo3_final/hit1','hit2':G+'/combo3_final/hit2','hit3':G+'/combo3_final/hit3'}   # combo3_final: east = combo3_v3 (bigger, lunging), west = mirror of it, south hit3 flash removed, others combo3_v2
DIRS={'down':'south','up':'north','right':'east','left':'west'}
ROOT=(128,189)
def even(n,k): b=[n//k]*k; [b.__setitem__(i,b[i]+1) for i in range(n%k)]; return b
# combo: existing H8.combo timing unchanged (hit1 dur14 hit@5, hit2 dur18 hit@6, hit3 dur27 hit@9). CONTACT = source frame shown from the hit tick (per dir).
CONTACT={'hit1':{'down':4,'up':3,'right':4,'left':4},'hit2':{'down':3,'up':3,'right':4,'left':4},'hit3':{'down':6,'up':3,'right':4,'left':4}}
def combo_ticks(hit,d,n=8):
    C=OLD['combo'][int(hit[-1])-1]; c=CONTACT[hit][d]; return even(C['hit'],c)+even(C['dur']-C['hit'],n-c)
# 60 fps ticks per frame: idle 7t=117ms, walk/run = gait (distance) ~90/~70 ms at 215/408 px/s, dash 4 frames 4-5t (67-83ms) in the unchanged 17-tick dash,
# hurt 4 frames x5t=83ms in the unchanged 20-tick hurt, death 8x6t=100ms then last frame held (deathTicks 110), guard/jump 5t=83ms, cast 5t/frame (H8.castTpf).
R8=list(range(8))
PLAN={'idle':(R8,[7]*8),'walk':(R8,[5]*8),'run':(R8,[4]*8),'dash':([1,3,5,7],[4,4,4,5]),'hurt':([1,3,5,7],[5]*4),
      'death':(list(range(9)),[6]*9),'jump':(R8,[5]*8)}
CASTSEQ=[0,1,2,2,2,2,3,4,5,6,6]; CASTM={'a':3,'rs':6,'e':8,'n':11}; CAST_TPF=5   # windup 0-2, channel 3-5, release 6-7, recover 4,1,0
GAIT={'walkCyc':round(215*8*0.090),'runCyc':round(408*8*0.070)}
SHEET={'idle':'idle','walk':'walk','run':'run','dash':'dash','hurt':'hurt','death':'death','jump':'jump','cast':'cast','hit1':'atk','hit2':'atk','hit3':'atk'}
frames={}; cache={}
def add(sheet,path):
    k=(sheet,path)
    if k in cache: return cache[k]
    f=np.asarray(Image.open(path).convert('RGBA')); a=f[...,3]>0; ys,xs=np.where(a); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    L=frames.setdefault(sheet,[]); L.append((path,np.ascontiguousarray(f[y0:y1,x0:x1]),int(ROOT[0]-x0),int(ROOT[1]-y0))); cache[k]=[sheet,len(L)-1]; return cache[k]
def src(m,pd):
    fs=sorted(glob.glob(f'{SRC[m]}/{pd}/*.png')); assert len(fs)>=7,(m,pd,len(fs)); return fs
anims={}
for d,pd in DIRS.items():
    for m,(pick,ticks) in PLAN.items():
        fs=src(m,pd); anims[f'{m}_{d}']=[add(SHEET[m],fs[i])+[t] for i,t in zip(pick,ticks)]
    for h in ('hit1','hit2','hit3'):
        fs=src(h,pd); anims[f'{h}_{d}']=[add('atk',fs[i])+[t] for i,t in zip(R8,combo_ticks(h,d))]
    anims['rec1_'+d]=[anims['hit1_'+d][-1][:2]+[12]]; anims['rec2_'+d]=[anims['hit2_'+d][-1][:2]+[12]]; anims['hold_'+d]=[anims['hit3_'+d][0][:2]+[1]]
    fs=src('cast',pd); anims['_cast_'+d]=[add('cast',fs[i])+[CAST_TPF] for i in CASTSEQ]
CV2=G+'/cast_death_guard_v2/cast'; STYLE={'s1':'cyan','s2':'red','s3':'gold'}
FXC={}
for st in set(STYLE.values()):
    for pd in DIRS.values():
        for f in range(7):
            for lay in ('magic_circle','hand_flash'):
                q=f'{CV2}/{lay}/{st}/{pd}/{f:03d}.png'
                if np.asarray(Image.open(q))[...,3].any(): FXC[q]=add('castfx',q)[1]
sheets={}; cells={}; total=0
for sh,L in frames.items():
    order=sorted(range(len(L)),key=lambda j:-L[j][1].shape[0]); x=y=rowh=0; pos={}
    for j in order:
        h,w=L[j][1].shape[:2]
        if x+w>2048: x=0; y+=rowh+1; rowh=0
        pos[j]=(x,y); x+=w+1; rowh=max(rowh,h)
    im=Image.new('RGBA',(max(p[0]+L[j][1].shape[1] for j,p in pos.items()),y+rowh))
    for j,(px,py) in pos.items(): im.paste(Image.fromarray(L[j][1]),(px,py))
    fn=f'hero8_{sh}.webp'; im.save(f'{OUT}/{fn}','WEBP',lossless=True,quality=100,method=6); total+=os.path.getsize(f'{OUT}/{fn}')
    cells[sh]=[[pos[j][0],pos[j][1],L[j][1].shape[1],L[j][1].shape[0],L[j][2],L[j][3]] for j in range(len(L))]; sheets[sh]=f'anim/{fn}'; print(sh,len(L),im.size)
SH=list(sheets)
# old magic-circle fx sheet (castfx) kept as is
FX=SH.index('castfx')   # cast v2 layers (magic circle under / hand flash over), packed above
A={k:[[SH.index(e[0]),e[1],e[2]] for e in v] for k,v in anims.items() if not k.startswith('_')}
# cast_s{1,2,3}_{dir}: new body frames + old S1/S2/S3 magic circle (back/front) at the same phase; left uses the right fx (mirrored at runtime)
OM=OLD['cast']['s1_right']; OPH=[(0,OM['a']),(OM['a'],OM['rs']),(OM['rs'],OM['e']),(OM['e'],OM['n'])]
NPH=[(0,CASTM['a']),(CASTM['a'],CASTM['rs']),(CASTM['rs'],CASTM['e']),(CASTM['e'],CASTM['n'])]
def oldidx(j):
    for (n0,n1),(o0,o1) in zip(NPH,OPH):
        if n0<=j<n1: return o0+(round((j-n0)*(o1-o0-1)/max(1,n1-n0-1)) if n1-n0>1 else 0)
cast={}
for s in ('s1','s2','s3'):
    for d,pd in DIRS.items():
        out=[]
        for j,e in enumerate(anims['_cast_'+d]):
            f=CASTSEQ[j]; mb=f'{CV2}/magic_circle/{STYLE[s]}/{pd}/{f:03d}.png'; hf=f'{CV2}/hand_flash/{STYLE[s]}/{pd}/{f:03d}.png'
            out.append([SH.index(e[0]),e[1],e[2]]+([FX,FXC[mb]] if mb in FXC else [-1,-1])+([FX,FXC[hf]] if hf in FXC else [-1,-1]))
        A[f'cast_{s}_{d}']=out; cast[f'{s}_{d}']=dict(CASTM)
for s in ():
    for d in DIRS:
        od='right' if d=='left' else d; OL=OLD['anims'][f'cast_{s}_{od}']; out=[]
        for j,e in enumerate(anims['_cast_'+d]):
            o=OL[oldidx(j)]; fb=[FX,o[4]] if len(o)>=7 and o[3]>=0 else [-1,-1]; ff=[FX,o[6]] if len(o)>=7 and o[5]>=0 else [-1,-1]
            out.append([SH.index(e[0]),e[1],e[2]]+fb+ff)
        A[f'cast_{s}_{d}']=out; cast[f'{s}_{d}']=dict(CASTM)
for f in glob.glob(f'{OUT}/hero8_*.webp'):
    if os.path.basename(f)[6:-5] not in SH: os.remove(f); print('removed',f)
out={'_doc':'GENERATED by tools/anim/hero_v4_atlas.py (PixelLab v3 char fb140a07, v3gen_20261018: moves_v1 idle/walk/run/hurt/jump, dash_v2, death+cast v2 (cast_death_guard_v2, magic circle/hand flash layers S1 cyan/S2 red/S3 gold), combo3_final hit1-3; no guard). anims[<name>_<dir>] = [[sheet,cell,ticks(,fxb sheet,cell,fxf sheet,cell)]]; dirs incl. real left. anchor = fixed feet root (128,189) of the 256 canvas, scale 1:1.',
     'v3':1,'v4':1,'left':1,'fxMirrorLeft':0,'figH':124,'castTpf':CAST_TPF,'dirs':list(DIRS),'sheets':[sheets[s] for s in SH],'cells':[cells[s] for s in SH],'anims':A,'cast':cast,'combo':OLD['combo'],'gait':GAIT,
     'src':{k:os.path.relpath(v,G) for k,v in SRC.items()}}
json.dump(out,open(f'{OUT}/hero8.json','w'),separators=(',',':'))
print('total KB',total//1024,'gait',GAIT,'anims',len(A))
