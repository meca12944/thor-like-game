#!/usr/bin/env python3
"""Linette (PixelLab 7e26e0f3, 117px confirmed) key motions, modelled on the hero v4 set (idle/walk/run/dash/hurt/death/cast/atk1-3), 4 drawn directions.
usage: run_moves.py motion:dir[:seed] ...   (or 'all')   -> <motion>/<dir>/NNN.png
Budget: env CAP (default 350) generations summed from own job records in _raw/job_*.json. Key from env only; never printed or logged."""
import os,sys,json,time,glob,threading,urllib.request,urllib.error
C=os.path.dirname(os.path.abspath(__file__)); RAW=C+'/_raw'; os.makedirs(RAW,exist_ok=True)
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='7e26e0f3-b375-4384-b955-3304cacebff3'
CAP=int(os.environ.get('CAP','350')); SEM=threading.Semaphore(6)
def scrub(o): return json.dumps(o,indent=1,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,
        headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for a in range(25):
        try:
            with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
        except urllib.error.HTTPError as e:
            b2=e.read()
            if e.code in (429,500,502,503,504) and a<24: time.sleep(30); continue
            try: return e.code,json.loads(b2)
            except Exception: return e.code,{'raw':b2.decode(errors='replace')[:2000]}
        except Exception as e:
            if a<12: time.sleep(5); continue
            return 0,{'err':str(e)}
def spent():
    s=0
    for f in glob.glob(RAW+'/job_*.json'):
        try: s+=(json.load(open(f)).get('usage') or {}).get('generations') or 0
        except Exception: pass
    return s
COMMON=(" Same character in every frame exactly as the reference image: petite adult woman, pale blonde long ponytail with a blue ribbon, red bikini top, "
 "red pleated mini skirt, brown belt with a purple pouch, brown gloves, brown thigh-high boots with silver knee guards, a long thin silver sewing needle "
 "held in EACH hand like a rapier. Same face, same proportions and same size as the reference; feet stay on the same ground line. Bold outline, clean pixels. "
 "No effects, no trails, no glow on the body.")
MOT={ # name: (frames, action)  -- frame counts follow the hero set (256 canvas max 8)
 'idle':(8,"Idle breathing loop: she stands relaxed in a light ready stance, needles held low at her sides, chest rises and falls gently, ponytail sways slightly. Loops seamlessly."),
 'walk':(8,"Walking loop: light bouncy steps, legs clearly stepping, arms swing naturally with the needles pointed down, ponytail bobs. Loops seamlessly."),
 'run':(8,"Running loop: fast sprint, body leaning forward, long strides with a clear airborne moment, arms pumping with the needles held back, ponytail streams behind. Loops seamlessly."),
 'dash':(4,"Quick dash: a short crouch, then she bursts forward low and fast with both needles held back, then lands and stops."),
 'hurt':(4,"Hit reaction: she is struck, flinches backward with the head snapped back and arms thrown out, then recovers to the stance."),
 'death':(8,"Death: she is struck hard, staggers, drops to her knees, then collapses onto the ground and lies still. No blood."),
 'cast':(8,"Skill cast: she crosses both needles in front of her chest, gathers, then flings both arms forward as if releasing threads, holds the pose, then returns to the stance."),
 'atk1':(8,"Attack 1 of 3: a quick straight thrust with the right-hand needle, stepping forward with full arm extension, brief hold, then pull back to the stance."),
 'atk2':(8,"Attack 2 of 3: a quick straight thrust with the left-hand needle, the other needle pulled back, brief hold, then pull back to the stance."),
 'atk3':(8,"Attack 3 of 3, the finisher: a big lunging double thrust with both needles together, long step forward with full extension, hold the final pose, then recover."),
}
FACE={'south-east':" Three-quarter FRONT view facing down-right every frame; she never turns away or sideways.",
 'north-east':" Three-quarter BACK view facing up-right every frame, face mostly hidden; arms and needles stay visible. She never turns around.",
 'south':" TRUE FRONT VIEW every frame: she faces the camera, chest and face toward the viewer; forward movement and attacks go DOWN the screen toward the camera; she never turns sideways or away.",
 'north':" TRUE BACK VIEW every frame: seen from directly behind, back of the head and ponytail visible, face never shown; forward movement and attacks go UP the screen; arms and needles stay visible beside the body. She never turns around.",
 'east':" STRICT SIDE VIEW every frame: facing RIGHT in profile, chest never turns toward the camera; everything moves toward the RIGHT. She never turns around.",
 'west':" STRICT SIDE VIEW every frame: facing LEFT in profile, chest never turns toward the camera; everything moves toward the LEFT. She never turns around."}
def log(*a):
    s=f'[{time.strftime("%H:%M:%S")}] '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
def gen(m,d,seed):
    with SEM:
        fc,act=MOT[m]; name=f'lin_{m}_{d}_s{seed}'
        body={'character_id':CID,'mode':'v3','action_description':act+FACE[d]+COMMON,'frame_count':fc,'directions':[d],
              'animation_name':name,'keep_first_frame':True,'seed':seed}
        st,r=req('POST','/characters/animations',body)
        open(f'{RAW}/submit_{name}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
        if st!=200: log('SUBMIT FAIL',name,st,scrub(r)[:300]); return
        j=r['background_job_ids'][0]; log('submitted',name)
        while True:
            time.sleep(10); st,r=req('GET',f'/background-jobs/{j}')
            if r.get('status') in ('completed','failed'): break
        open(f'{RAW}/job_{name}.json','w').write(scrub(r))
        if r['status']!='completed': log('JOB FAIL',name,scrub(r)[:300]); return
        out=f'{C}/{m}/{d}'; os.makedirs(out,exist_ok=True)
        for i,u in enumerate(r['last_response']['storage_urls']['frames']):
            for a in range(6):
                try: open(f'{out}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read()); break
                except Exception: time.sleep(5)
        log('done',name,r.get('usage'))
args=sys.argv[1:]
if args==['all']: args=[f'{m}:{d}' for m in MOT for d in FACE]
jobs=[]
for a in args:
    p=a.split(':'); jobs.append((p[0],p[1],int(p[2]) if len(p)>2 else 5100))
s0=spent(); need=sum(MOT[m][0] for m,_,_ in jobs)
log(f'jobs={len(jobs)} est={need} spent_so_far={s0} cap={CAP}')
if s0+need>CAP: log('BUDGET STOP'); sys.exit(2)
ts=[threading.Thread(target=gen,args=jd) for jd in jobs]
for t in ts: t.start(); time.sleep(1.0)
for t in ts: t.join()
log('spent total from job records:',spent())
