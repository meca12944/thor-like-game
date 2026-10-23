# Linette 3-hit thrust set via key poses: make atk2/atk3 lunge states (atk1 = states/lunge), then animate idle-rotation -> pose (end_frame) per direction.
# Down/up use the diagonal views (south-east / north-east) because pure front/back thrusts do not read. Cap via CAP (default 170, includes the 33 pilot).
import os,sys,json,glob,threading,subprocess; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from pl import *
import numpy as np
from PIL import Image
CAP=int(os.environ.get('CAP','170'))
def spent():
    s=0
    for f in glob.glob(RAW+'/job_*.json'):
        try: s+=(json.load(open(f)).get('usage') or {}).get('generations') or 0
        except Exception: pass
    return s
STATES={'atk2':"Fencing lunge thrust pose with the LEFT hand: the left arm is fully extended straight forward at chest height and the left-hand needle points straight ahead like a rapier, the right-hand needle is pulled back near the shoulder. Front knee bent, back leg straight, torso leaning forward, feet wide apart front and back on the ground. Same character, same outfit, same colors, same size.",
        'atk3':"Deep finishing lunge with BOTH needles thrust together: both arms fully extended straight forward side by side at chest height, both needles pointing straight ahead, very long step with the front knee deeply bent and the back leg stretched straight, torso low and leaning far forward, ponytail flying back. Same character, same outfit, same colors, same size."}
ACT={'atk1':"Attack 1 of 3: a quick fencing lunge with the RIGHT-hand needle. From the stance she draws the right needle back slightly, then explodes forward with a long step and thrusts the right needle straight ahead, ending exactly in the lunge pose of the end frame.",
     'atk2':"Attack 2 of 3: a quick fencing lunge with the LEFT-hand needle. She pulls the left needle back, then steps forward and thrusts the left needle straight ahead, ending exactly in the lunge pose of the end frame.",
     'atk3':"Attack 3 of 3, the finisher: she crouches and coils with both needles drawn back, then launches into a very long lunge and thrusts BOTH needles straight ahead together, ending exactly in the deep lunge pose of the end frame."}
VIEW={'east':" STRICT SIDE VIEW facing RIGHT every frame, chest never turns toward the camera; she moves toward the RIGHT.",
      'west':" STRICT SIDE VIEW facing LEFT every frame, chest never turns toward the camera; she moves toward the LEFT.",
      'south-east':" Three-quarter FRONT view facing down-right every frame; the thrust goes down-right toward the camera side. She never turns away.",
      'north-east':" Three-quarter BACK view facing up-right every frame, face mostly hidden; the thrust goes up-right. Arms and needles stay visible. She never turns around."}
TAIL=" Same character, outfit and size in every frame; no effects, no trails."
SEEDS={'atk1':11,'atk2':12,'atk3':13}
def state(name):
    if os.path.exists(f'{C}/states/{name}/east.png'): return
    subprocess.run([sys.executable,f'{C}/make_state.py',name,STATES[name],'7'],check=True)
def endframe(st,d):
    src=f'{C}/states/{st}/{d}.png'; im=Image.open(src).convert('RGBA'); a=np.asarray(im)[...,3]; ys,_=np.nonzero(a>0)
    c=Image.new('RGBA',(256,256)); c.alpha_composite(im,(0,189-int(ys.max()))); p=f'{C}/end_{st}_{d}.png'; c.save(p); return p
def anim(m,d):
    if os.path.exists(f'{C}/{m}/{d}/008.png'): return
    st='lunge' if m=='atk1' else m
    subprocess.run([sys.executable,f'{C}/anim.py',m,d,'8',endframe(st,d),ACT[m]+VIEW[d]+TAIL,str(SEEDS[m])])
s0=spent(); need=(25 if not os.path.exists(f'{C}/states/atk2/east.png') else 0)+(25 if not os.path.exists(f'{C}/states/atk3/east.png') else 0)+8*sum(1 for m in ACT for d in VIEW if not os.path.exists(f'{C}/{m}/{d}/008.png'))
log(f'run_all: spent {s0} need {need} cap {CAP}')
if s0+need>CAP: log('BUDGET STOP'); sys.exit(2)
ts=[threading.Thread(target=state,args=(n,)) for n in STATES]; [t.start() for t in ts]; [t.join() for t in ts]
ts=[threading.Thread(target=anim,args=(m,d)) for m in ACT for d in VIEW]
for t in ts: t.start(); time.sleep(1)
for t in ts: t.join()
log('run_all spent total from job records:',spent())
