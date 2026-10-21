# Polish step (1번 방 노하우): per-clip constant offset so frame 0 feet sit at root (128,189) in every direction (no per-frame re-centering -> no jitter),
# one size for all clips (re-scale clips whose standing frame 0 is >3% off the idle height), and baked bob/sway on front/back walk/run.
# Reads frames/ (from assemble.py) and writes frames_polished/.
import glob,json,os,shutil,math
import numpy as np
from PIL import Image
from measure import body
from pxscale import pxscale
H=os.path.dirname(os.path.abspath(__file__)); IN=H+'/frames'; OUT=H+'/frames_polished'
man=json.load(open(H+'/manifest.json'))
STAND={'idle','walk','dash','hurt','death','cast','atk1','atk3','jump'}   # atk2 starts in the atk1 lunge -> takes atk1's offset/scale (SAME_AS)
SAME_AS={'atk2':'atk1'}
kept={}   # clips whose frame 0 is a standing pose (run starts mid-stride)
BOB={('walk','down'):(2,1),('walk','up'):(2,1),('run','down'):(3,1),('run','up'):(3,1)}   # (bob px, sway px): two steps per clip
shutil.rmtree(OUT,ignore_errors=True); log={}
for m,dd in man['motions'].items():
    for d in dd:
        fs=sorted(glob.glob(f'{IN}/{m}/{d}/*.png')); t0,b0,c0=body(fs[0]); ref=sorted(glob.glob(f'{IN}/idle/{d}/*.png')) or sorted(glob.glob(f'{IN}/idle/right/*.png')); ti,bi,ci=body(ref[0])
        sc=1.0
        if m in STAND and abs((bi-ti)/(b0-t0)-1)>0.03: sc=(bi-ti)/(b0-t0)
        if m in SAME_AS:   # continue exactly where atk1's lunge frame was drawn
            sc,c0,b0=kept[(SAME_AS[m],d)]
        kept[(m,d)]=(sc,c0,b0)
        os.makedirs(f'{OUT}/{m}/{d}',exist_ok=True); n=len(fs)
        for i,f in enumerate(fs):
            im=Image.open(f).convert('RGBA')
            if sc!=1.0:   # scale about frame-0 feet, nearest to keep pixels
                im=pxscale(im,sc); fx,fy=c0*sc,b0*sc
            else: fx,fy=c0,b0
            dx,dy=128-fx,189-fy
            if (m,d) in BOB:
                bob,sway=BOB[(m,d)]; ph=2*math.pi*i/n
                dy-=round(bob*abs(math.sin(ph)))   # up twice per cycle (once per step)
                dx+=round(sway*math.sin(ph))
            c=Image.new('RGBA',(256,256)); c.alpha_composite(im,(0,0)) if False else c.paste(im,(round(dx),round(dy)),im)
            c.save(f'{OUT}/{m}/{d}/{i:03d}.png')
        log[f'{m}_{d}']={'scale':round(sc,3),'offset':[round(128-c0*sc),round(189-b0*sc)]}
# front/back runs (hero skeleton, foreshortened legs): snap every frame's lowest pixel to the ground line, then a 2px run bob,
# so she neither floats nor sinks (owner 10-20 "다리가 왜이래")
# owner 10-21 "캐릭 크기가 방향별로 틀려지네" / "뛸때 좌우 크기가 훨씬 커": size = head-to-skirt length (blue ribbon top -> lowest red skirt pixel),
# which legs and crouching do not change (full height made crouched runs look too big). Every idle / walk / run clip is scaled about the feet
# so its median head-to-skirt = the side idle's.
def upper(f):
    a=np.array(Image.open(f).convert('RGBA')).astype(int);al=a[:,:,3]>0
    by=np.where(al&(a[:,:,2]>a[:,:,0]+40)&(a[:,:,2]>120))[0];ry=np.where(al&(a[:,:,0]>150)&(a[:,:,1]<70)&(a[:,:,2]<80))[0]
    return ry.max()-by.min() if len(by) and len(ry) else None
_r=[upper(f) for f in sorted(glob.glob(f'{OUT}/idle/right/*.png'))];UTGT=sorted(v for v in _r if v)[len(_r)//2]
for m in ('idle','walk','run'):
    for d in os.listdir(f'{OUT}/{m}'):
        fs=sorted(glob.glob(f'{OUT}/{m}/{d}/*.png'));us=sorted(v for v in (upper(f) for f in fs) if v);med=us[len(us)//2];sc=UTGT/med
        if abs(sc-1)<0.015:continue
        for f in fs:
            im=Image.open(f);b=im.getbbox();cx,fy=(b[0]+b[2])/2,b[3];im2=pxscale(im,sc)
            c=Image.new('RGBA',(256,256));c.paste(im2,(round(cx-cx*sc),round(fy-fy*sc)),im2);c.save(f)
        log[f'{m}_{d}_size']={'upper_median':int(med),'target':int(UTGT),'scale':round(sc,3)}
for m,d in (('run','south'),('run','north'),('run','down'),('run','downl'),('run','up'),('run','upl'),('run','right'),('run','left')):   # key-pose runs: keep the drawn ground, but cap the airborne lift at 4px (more reads as hopping)
    fs=sorted(glob.glob(f'{OUT}/{m}/{d}/*.png'));n=len(fs)
    for i,f in enumerate(fs):
        im=Image.open(f);b=im.getbbox();dy=max(0,186-b[3]) if b[3]<186 else min(0,190-b[3])   # no more than 4px up, never below the ground
        c=Image.new('RGBA',(256,256));c.paste(im,(0,dy),im);c.save(f)
for m,d in (('walk','down'),('walk','downl'),('walk','up'),('walk','upl'),('walk','right'),('walk','left'),('walk','south'),('walk','north')):   # key-pose diagonal walks: a walk never leaves the ground -> lowest pixel on the ground line (1px bob)
    fs=sorted(glob.glob(f'{OUT}/{m}/{d}/*.png'));n=len(fs)
    for i,f in enumerate(fs):
        im=Image.open(f);b=im.getbbox();dy=190-b[3]-(1 if i%4==2 else 0)
        c=Image.new('RGBA',(256,256));c.paste(im,(0,dy),im);c.save(f)
# circle check (owner 10-21): centre every idle / walk / run clip on her body, not her feet - per clip one constant x shift so the median
# skirt centre sits at x=128 (wide first-frame stances had pushed some clips sideways, so she jumped left/right when turning)
def skirt_cx(f):
    a=np.array(Image.open(f).convert('RGBA')).astype(int);al=a[:,:,3]>0;xs=np.where((al&(a[:,:,0]>150)&(a[:,:,1]<70)&(a[:,:,2]<80)).any(axis=0))[0]
    return (xs.min()+xs.max())/2 if len(xs) else None
for m in ('idle','walk','run'):
    for d in os.listdir(f'{OUT}/{m}'):
        fs=sorted(glob.glob(f'{OUT}/{m}/{d}/*.png'));cs=sorted(v for v in (skirt_cx(f) for f in fs) if v is not None)
        if not cs:continue
        dx=round(128-cs[len(cs)//2])
        if dx==0:continue
        for f in fs:
            im=Image.open(f);c=Image.new('RGBA',(256,256));c.paste(im,(dx,0),im);c.save(f)
        log[f'{m}_{d}_center']={'scale':1.0,'dx':dx}
json.dump(log,open(H+'/polish_log.json','w'),indent=1); print(json.dumps({k:v for k,v in log.items() if v['scale']!=1.0}))
# owner 10-21 "리네트 몸이 마법진 밖으로 나간다": the throw cast steps forward -> every cast frame is centred on its own skirt (x=128),
# so her body stays in the middle of the magic circle the whole cast (feet slide a little, the lunge still reads in the legs)
for d in os.listdir(f'{OUT}/cast'):
    for f in sorted(glob.glob(f'{OUT}/cast/{d}/*.png')):
        c0=skirt_cx(f)
        if c0 is None:continue
        dx=round(128-c0)
        if dx:im=Image.open(f);c=Image.new('RGBA',(256,256));c.paste(im,(dx,0),im);c.save(f)
