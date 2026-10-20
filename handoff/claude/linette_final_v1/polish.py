# Polish step (1번 방 노하우): per-clip constant offset so frame 0 feet sit at root (128,189) in every direction (no per-frame re-centering -> no jitter),
# one size for all clips (re-scale clips whose standing frame 0 is >3% off the idle height), and baked bob/sway on front/back walk/run.
# Reads frames/ (from assemble.py) and writes frames_polished/.
import glob,json,os,shutil,math
import numpy as np
from PIL import Image
from measure import body
H=os.path.dirname(os.path.abspath(__file__)); IN=H+'/frames'; OUT=H+'/frames_polished'
man=json.load(open(H+'/manifest.json'))
STAND={'idle','walk','dash','hurt','death','cast','atk1','atk2','atk3'}   # clips whose frame 0 is a standing pose (run starts mid-stride)
BOB={('walk','down'):(2,1),('walk','up'):(2,1),('run','down'):(3,1),('run','up'):(3,1)}   # (bob px, sway px): two steps per clip
shutil.rmtree(OUT,ignore_errors=True); log={}
for m,dd in man['motions'].items():
    for d in dd:
        fs=sorted(glob.glob(f'{IN}/{m}/{d}/*.png')); t0,b0,c0=body(fs[0]); ti,bi,ci=body(sorted(glob.glob(f'{IN}/idle/{d}/*.png'))[0])
        sc=1.0
        if m in STAND and abs((bi-ti)/(b0-t0)-1)>0.03: sc=(bi-ti)/(b0-t0)
        os.makedirs(f'{OUT}/{m}/{d}',exist_ok=True); n=len(fs)
        for i,f in enumerate(fs):
            im=Image.open(f).convert('RGBA')
            if sc!=1.0:   # scale about frame-0 feet, nearest to keep pixels
                im=im.resize((round(256*sc),round(256*sc)),Image.NEAREST); fx,fy=c0*sc,b0*sc
            else: fx,fy=c0,b0
            dx,dy=128-fx,189-fy
            if (m,d) in BOB:
                bob,sway=BOB[(m,d)]; ph=2*math.pi*i/n
                dy-=round(bob*abs(math.sin(ph)))   # up twice per cycle (once per step)
                dx+=round(sway*math.sin(ph))
            c=Image.new('RGBA',(256,256)); c.alpha_composite(im,(0,0)) if False else c.paste(im,(round(dx),round(dy)),im)
            c.save(f'{OUT}/{m}/{d}/{i:03d}.png')
        log[f'{m}_{d}']={'scale':round(sc,3),'offset':[round(128-c0*sc),round(189-b0*sc)]}
json.dump(log,open(H+'/polish_log.json','w'),indent=1); print(json.dumps({k:v for k,v in log.items() if v['scale']!=1.0}))
