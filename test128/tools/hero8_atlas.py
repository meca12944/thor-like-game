# hero8_atlas.py — pack the NEW 8-motion x 8-direction hero (char_v4/pixellab/hero/vid/px_*) into per-motion WebP atlases
# for index128.html (test128).  Frame picks / timings follow the approved previews:
#   combo = combo_fast06.py / preview8.py (36 ticks: hit1 8, hit2 8, hit3 20), per-direction remap through the slash-trail onset
#   dash  = dash_preview.py v2 PK picks (launch 1t + 6 burst x2t + land 1t = 14t, rise 2t + rec 1t = 3t recovery)
#   walk / run = one seamless gait cycle (auto-detected period), sampled ~every 2nd source frame
#   hurt / cast = hand picks on the 49 / 73-frame clips
# Anchor = newstyle_check.anchor(frame 0 of each clip) (body-mask mean x, foot row) — same as every preview, so motions line up.
# Output: town-demo/assets/anim/hero8_<sheet>.webp + assets/anim/hero8.json (inlined into index128.html as const H8).
import glob, json, os, sys, hashlib, numpy as np
from PIL import Image
VID='/workspace/town-demo/char_v4/pixellab/hero/vid'
sys.path.insert(0,'/workspace/town-demo/char_v4/pixellab/hero/newstyle'); sys.argv=['x']
import newstyle_check as N
OUT='/workspace/town-demo/assets/anim'
DIRS=['right','down','up']   # 4-way sprites (user decision 2026-10-18 09:15): left = runtime mirror of right, diagonals use the side sprite; movement / hits / dash stay 8-way
SUF={'right':'_side','left':'_left','down':'_front','up':'_back','downright':'_downdiag','upright':'_updiag','downleft':'_downleft','upleft':'_upleft'}
def tag(a,d):
    if a in('atk1','atk2','atk3','dash'):
        if d=='right': return a
    return a+SUF[d]
_cache={}
def load(t):
    if t not in _cache: _cache[t]=[np.asarray(Image.open(p).convert('RGBA')) for p in sorted(glob.glob(f'{VID}/px_{t}/*.png'))]
    return _cache[t]
def cy(f):
    a=f[...,3]>0; r,g,b=[f[...,i].astype(int) for i in range(3)]; return int((a&(b>150)&(g>150)&(b-r>40)).sum())
def onset(P):
    c=np.array([cy(f) for f in P]); return int(np.argmax(c>0.25*c.max()))
def remap(i,src,dst): return int(round(np.interp(i,src,dst)))
def diff(a,b):
    a=a.astype(np.int16); b=b.astype(np.int16); m=(a[...,3]>0)|(b[...,3]>0)
    return float((np.abs(a[...,:3]-b[...,:3]).sum(2)*m).sum()/max(1,m.sum()))
def gait(F,lo,hi,tail=6):
    n=len(F); best=None
    for P in range(lo,hi+1):
        for a in range(2,n-P-tail):
            v=diff(F[a],F[a+P])
            if best is None or v<best[0]: best=(v,P,a)
    return best
# approved right-clip combo picks (combo_fast06.py)
H1=[(16,1),(20,1),(22,1),(25,1),(28,1),(32,1),(36,2)]
H2=[(8,1),(13,1),(15,1),(18,1),(22,1),(27,1),(32,2)]
H3=[(22,2),(32,2),(36,1),(39,1),(41,4),(45,1),(51,1),(57,2),(66,3),(72,3)]
REC={'atk1':[40,44,48],'atk2':[36,40,44,48]}   # follow-through shown only when the chain is NOT continued (cancellable)
PK={'right':(6,[8,12,16,20,26,32],40,44,46,48),'down':(14,[18,20,22,24,28,31],33,36,40,48),'up':(7,[9,10,20,22,36,38],40,44,46,48),
    'downright':(10,[14,18,22,26,30,34],38,42,44,48),'upright':(9,[10,14,18,22,28,34],42,46,47,48)}
PK['left']=PK['right']; PK['downleft']=PK['downright']; PK['upleft']=PK['upright']
HURT=[(7,2),(9,2),(11,2),(13,2),(16,2),(19,2),(22,2),(25,2),(28,2),(32,2)]          # 20 ticks = FEEL.hurtTicks
CAST=list(range(0,73,2))   # every 2nd source frame, evenly spaced; segments (windup / channel / release / recover) auto-detected per clip below
RK={a:[0,onset(load(a)),len(load(a))-1] for a in ['atk1','atk2','atk3']}
frames={}   # sheet -> list of (key, rgba-trimmed, ax, ay)
cells={}; anims={}; meta={'gait':{}}
def add(sheet,clip,i):
    F=load(clip); f=F[i]; ax,ay=N.anchor(F[0])
    a=f[...,3]>0; ys,xs=np.where(a); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    t=np.ascontiguousarray(f[y0:y1,x0:x1]); key=(sheet,clip,i)
    L=frames.setdefault(sheet,[])
    for j,(k,_,_,_) in enumerate(L):
        if k==key: return f'{sheet}:{j}'
    L.append((key,t,round(ax-x0,1),int(ay-y0))); return f'{sheet}:{len(L)-1}'
for d in DIRS:
    W=load(tag('walk',d)); R=load(tag('run',d))
    anims['idle_'+d]=[[add('walk',tag('walk',d),0),1]]
    for a,F,lo,hi in (('walk',W,16,26),('run',R,10,16)):
        v,P,s=gait(F,lo,hi); K=P; idx=[s+k for k in range(P)]   # FULL gait cycle, every source frame (no decimation)
        anims[a+'_'+d]=[[add(a,tag(a,d),i),1] for i in idx]; meta['gait'][a+'_'+d]={'period':P,'start':s,'diff':round(v,1),'n':K}
    P={a:load(tag(a,d)) for a in ['atk1','atk2','atk3']}
    K={a:[0,onset(P[a]),len(P[a])-1] for a in P}
    for name,a,seq in (('hit1','atk1',H1),('hit2','atk2',H2),('hit3','atk3',H3)):
        anims[name+'_'+d]=[[add('atk',tag(a,d),remap(i,RK[a],K[a])),k] for i,k in seq]
    for name,a in (('rec1','atk1'),('rec2','atk2')):
        anims[name+'_'+d]=[[add('atk',tag(a,d),remap(i,RK[a],K[a])),3] for i in REC[a]]
    anims['hold_'+d]=[[add('atk',tag('atk3',d),remap(22,RK['atk3'],K['atk3'])),1]]
    L_,B,land,rise,rec,fin=PK[d]; D=tag('dash',d)
    anims['dash_'+d]=[[add('dash',D,L_),1]]+[[add('dash',D,f),2] for f in B]+[[add('dash',D,land),1],[add('dash',D,rise),2],[add('dash',D,rec),1]]
    anims['hurt_'+d]=[[add('hurt',tag('hurt',d),i),k] for i,k in HURT]
    anims['cast_'+d]=[[add('cast',tag('cast',d),i),1] for i in CAST]
    C=np.array([cy(f) for f in load(tag('cast',d))]); mx=C.max(); n=len(C)
    a=int(np.argmax(C>=.15*mx)); pk=int(n//3+np.argmax(C[n//3:])); e=int(np.where(C>=.1*mx)[0].max())+1; rs=max(a+2,pk-6)
    meta.setdefault('cast',{})[d]={'a':a//2,'rs':rs//2,'e':min(len(CAST)-1,(e+1)//2),'n':len(CAST),'src':[a,rs,pk,e]}
# pack each sheet (shelf packing, sorted by height), 1px gap
sheets={}; total=0
for sh,L in frames.items():
    order=sorted(range(len(L)),key=lambda j:-L[j][1].shape[0]); maxw=2048
    x=y=rowh=0; pos={}
    for j in order:
        h,w=L[j][1].shape[:2]
        if x+w>maxw: x=0; y+=rowh+1; rowh=0
        pos[j]=(x,y); x+=w+1; rowh=max(rowh,h)
    H=y+rowh; Wd=max(p[0]+L[j][1].shape[1] for j,p in pos.items())
    im=Image.new('RGBA',(Wd,H),(0,0,0,0))
    for j,(px,py) in pos.items(): im.paste(Image.fromarray(L[j][1]),(px,py))
    fn=f'hero8_{sh}.webp'; im.save(f'{OUT}/{fn}','WEBP',lossless=True,quality=100,method=6)
    sz=os.path.getsize(f'{OUT}/{fn}'); total+=sz
    cells[sh]=[[pos[j][0],pos[j][1],L[j][1].shape[1],L[j][1].shape[0],L[j][2],L[j][3]] for j in range(len(L))]
    sheets[sh]=f'anim/{fn}'; print(sh,len(L),'frames',im.size,sz//1024,'KB')
# resolve 'sheet:idx' refs -> [sheetIndex, cellIndex]
SH=list(sheets); A={k:[[SH.index(r.split(':')[0]),int(r.split(':')[1]),t] for r,t in v] for k,v in anims.items()}
out={'_doc':'GENERATED by tools/anim/hero8_atlas.py from char_v4/pixellab/hero/vid/px_* (8 motions x 8 dirs). sheets[i] = atlas; cells[sheet][j] = [x,y,w,h,ax,ay] art px = 1080p render px (ax,ay = foot anchor from clip frame 0). anims[<name>_<dir>] = [[sheetIdx, cellIdx, ticks@60fps], ...]. names: idle walk run hit1 hit2 hit3 rec1 rec2 hold dash hurt cast. dirs right/down/up (left = mirror of right). cast[dir] = atlas-frame segment starts a (channel) rs (release) e (recover).',
     'figH':117,'dirs':DIRS,'sheets':[sheets[s] for s in SH],'cells':[cells[s] for s in SH],'anims':A,'gait':meta['gait'],'cast':meta['cast']}
json.dump(out,open(f'{OUT}/hero8.json','w'),separators=(',',':'))
print('total',total//1024,'KB, json',os.path.getsize(f'{OUT}/hero8.json')//1024,'KB')
