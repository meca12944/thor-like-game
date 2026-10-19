#!/usr/bin/env python3
"""big4hit_v1 (owner 2026-10-19 08:37 KST): 4 separate VERY BIG full-arm longsword swings x 4 dirs. Preview only.
usage: run_big4hit.py [tag] h:dir[:seed] ...   -> candidates in big4hit_v1/_cand/<tag>/hit<h>/<dir>/
Budget: hard cap 400 generations summed from own job records in big4hit_v1/_raw/job_*.json. Key from env only; never printed."""
import os, sys, json, time, glob, threading, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=O+'/big4hit_v1'; RAW=C+'/_raw'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
CAP=400; FC=int(os.environ.get('FC','8'))
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
            if a<6: time.sleep(5); continue
            return 0,{'err':str(e)}
def spent():
    s=0
    for f in glob.glob(RAW+'/job_*.json'):
        try: s+=(json.load(open(f)).get('usage') or {}).get('generations') or 0
        except Exception: pass
    return s
COMMON=(" Longsword held in the right hand, swung at FULL ARM LENGTH with the arm completely straight and extended, the blade reaching as far from the body as possible. "
 "Shoulders and hips twist hard into the swing; the front foot steps forward and plants. Feet stay on the same ground line. "
 "Same character throughout: long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron, same face and same size as the idle. "
 "Bold outline, clean pixels. A big crisp white-cyan crescent slash smear trails the sword tip along the whole arc. No sparks, dust or other effects.")
HIT={1:("Attack 1 of 4: a VERY BIG, WIDE horizontal slash. Snap instantly into a windup with the sword pulled far back over the right shoulder, body coiled, "
        "then sweep the sword in a huge flat horizontal arc from right to left across the front of the body at full arm extension, ending with the arm stretched far out to the left side; hold."),
     2:("Attack 2 of 4: a VERY BIG backhand RETURN slash. Starting from the left side with the arm crossed over the chest, whip the sword back in a huge wide horizontal arc "
        "from left to right at full arm extension, torso unwinding, ending with the arm stretched far out to the right side; hold."),
     3:("Attack 3 of 4: a VERY BIG OVERHEAD diagonal CLEAVE. Raise the sword high above and behind the head with both arms fully stretched up, body arched back, "
        "then chop down in a huge diagonal arc from high over the head to low in front at the feet, deep lunge forward, blade ending near the ground; hold."),
     4:("Attack 4 of 4, the FINISHER: a VERY BIG full 360 degree SPINNING slash. Crouch and coil, then spin the whole body around one full turn with the sword "
        "held straight out at full arm length, the blade sweeping a giant circle all around the character, finishing with a rising upward slash, sword raised high; hold the final pose.")}
FACE={'south':" Facing the camera (front view) at the start and the end of the animation.",
 'east':" Facing RIGHT in side profile; lunge and swing toward the RIGHT; end facing right.",
 'west':" Facing LEFT in side profile; lunge and swing toward the LEFT; end facing left.",
 'north':(" Back view, facing away from the camera, face never shown; we see the back of the head and hair. The sword and sword arm must stay clearly visible beside or above the body, "
  "never hidden by the body or cape; the cape flares out to the side so the arm and the blade are readable.")}
FACE4={**FACE,'south':" Front view at the start and end (spins through the back mid-swing).",'north':FACE['north']+" Ends in back view again after the spin.",
 'east':" Starts and ends facing RIGHT in side profile, swinging toward the right.",'west':" Starts and ends facing LEFT in side profile, swinging toward the left."}
if os.environ.get('STRICT'):
    SIDE=(" STRICT SIDE VIEW for every frame: the camera sees the character from the {s} side only, face always in profile looking {d}, chest never turns toward the camera, "
          "the swing happens in the side plane, the blade sweeping up, out in front toward the {d} and back. Do not rotate toward the viewer.")
    FACE['east']=" Facing RIGHT."+SIDE.format(s='right',d='right'); FACE['west']=" Facing LEFT."+SIDE.format(s='left',d='left')
    FACE4['east']=FACE['east'].replace('Do not rotate toward the viewer.','For the spin, turn quickly through the back and come back to the right-facing profile; the final frames face right in profile.')
    FACE4['west']=FACE['west'].replace('Do not rotate toward the viewer.','For the spin, turn quickly through the back and come back to the left-facing profile; the final frames face left in profile.')
    FACE4['north']=FACE['north']+" The final three frames are a BACK VIEW again (back of the head, cape, no face visible), sword raised high and visible."
usage=[]; T0=time.time(); lock=threading.Lock()
def log(*a):
    s=f'[{time.strftime("%H:%M:%S")}] '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
def gen(tag,h,d,seed):
    name=f'big4hit_{tag}_hit{h}_{d}_s{seed}'
    desc=HIT[h]+(FACE4 if h==4 else FACE)[d]+COMMON
    body={'character_id':CID,'mode':'v3','action_description':desc,'frame_count':FC,'directions':[d],
          'animation_name':name,'keep_first_frame':False,'seed':seed}
    st,r=req('POST','/characters/animations',body)
    open(f'{RAW}/submit_{name}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
    if st!=200: log('SUBMIT FAIL',name,st,scrub(r)[:300]); return
    j=r['background_job_ids'][0]; log('submitted',name)
    while True:
        time.sleep(10); st,r=req('GET',f'/background-jobs/{j}')
        if r.get('status') in ('completed','failed'): break
    open(f'{RAW}/job_{name}.json','w').write(scrub(r))
    if r['status']!='completed': log('JOB FAIL',name,scrub(r)[:300]); return
    out=f'{C}/_cand/{tag}/hit{h}/{d}_s{seed}'; os.makedirs(out,exist_ok=True)
    for i,u in enumerate(r['last_response']['storage_urls']['frames']):
        open(f'{out}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
    log('done',name,r.get('usage'))
tag=sys.argv[1]; jobs=[]
for a in sys.argv[2:]:
    p=a.split(':'); jobs.append((int(p[0]),p[1],int(p[2]) if len(p)>2 else 4100+int(p[0])))
s0=spent(); need=len(jobs)*FC
log(f'tag={tag} jobs={len(jobs)} est={need} spent_so_far={s0} cap={CAP}')
if s0+need>CAP: log('BUDGET STOP'); sys.exit(2)
ts=[threading.Thread(target=gen,args=(tag,)+jd) for jd in jobs]
for t in ts: t.start(); time.sleep(1.5)
for t in ts: t.join()
log('spent total from job records:',spent())
