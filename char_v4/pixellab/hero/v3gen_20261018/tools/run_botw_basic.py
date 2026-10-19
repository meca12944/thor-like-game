#!/usr/bin/env python3
"""botw_basic_v1 (owner 2026-10-19 08:55 KST): BotW-style one-handed basic 4-hit combo x 4 dirs. Preview only.
usage: run_botw_basic.py [tag] h:dir[:seed] ...   -> candidates in botw_basic_v1/_cand/<tag>/hit<h>/<dir>_s<seed>/ (seed in path: retries never overwrite)
Budget: hard cap 300 generations summed from own job records in botw_basic_v1/_raw/job_*.json. Key from env only; never printed."""
import os, sys, json, time, glob, threading, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=O+'/botw_basic_v1'; RAW=C+'/_raw'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
CAP=300; FC=int(os.environ.get('FC','8'))
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
COMMON=(" One-handed longsword in the right hand. Snappy, grounded, readable basic sword combo in the style of Zelda Breath of the Wild's one-handed sword standard attack: "
 "a very short windup, a FAST swing, a clear follow-through pose with the sword arm extended, then settle. Feet stay on the same ground line, knees bent, weight low. "
 "The body stays facing the attack direction. Same character throughout: long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron, "
 "same face and same size as the idle. Bold outline, clean pixels. A clean thin white crescent slash trail follows the sword tip during the swing only. No sparks, dust or other effects.")
HIT={1:"Basic attack 1 of 4: a quick horizontal slash: small windup with the sword to the right side, then a fast flat slash across the front from right to left, arm extended at the end.",
     2:"Basic attack 2 of 4: a quick backhand slash the other way: from the left side, a fast flat backhand slash across the front from left to right, arm extended at the end.",
     3:"Basic attack 3 of 4: a small step forward with a fast diagonal slash from high on one side down across the front to low on the other side, arm extended at the end.",
     4:"Basic attack 4 of 4, finisher: pull the sword back at the hip, then a strong forward lunge with a straight THRUST (stab), the arm and blade fully extended straight forward in the facing direction, hold the lunge, then recover."}
FACE={'south':" Front view facing the camera the whole time; the sword swings and stabs toward the camera/down.",
 'east':(" STRICT SIDE VIEW every frame: facing RIGHT in profile, face in profile looking right, chest never turns toward the camera; "
         "the swings and the thrust go toward the RIGHT. Do not rotate toward the viewer."),
 'west':(" STRICT SIDE VIEW every frame: facing LEFT in profile, face in profile looking left, chest never turns toward the camera; "
         "the swings and the thrust go toward the LEFT. Do not rotate toward the viewer."),
 'north':(" BACK VIEW every frame, facing away from the camera, attacking upward/away; face never shown, we see the back of the head and hair. "
          "The sword and sword arm stay clearly visible beside or above the body, never hidden by the body or cape; the cape is pushed to the side.")}
EXTRA={}
if os.environ.get('STRICT'):
    EXTRA['north']=(" IMPORTANT: the character NEVER turns around: every frame, including the last frames, is the back of the character seen from behind, "
                    "back of the head and long hair toward the camera, no face, no chest. Only the right arm and the sword move out to the side and forward (up the screen).")
    EXTRA['south']=(" IMPORTANT: front view, the thrust goes straight TOWARD the camera: the sword tip points at the viewer, the arm reaches forward toward the camera, foreshortened blade; "
                    "the character keeps facing the camera.") if os.environ.get('STRICT')=='thrust' else ''
if os.environ.get('STRICT')=='thrust2':
    EXTRA['south']=(" Top-down game, character faces DOWN the screen: the thrust stabs straight DOWNWARD on the screen in front of the feet, "
                    "blade pointing down the screen, arm straight and extended below the chest, front foot stepping down-screen; keep facing the camera.")
    EXTRA['north']=(" Top-down game, character faces UP the screen, seen from behind (back of head, hair, cape, no face in any frame): "
                    "the thrust stabs straight UPWARD on the screen, the blade sticking up above the head-line in front of him, arm extended upward-forward, "
                    "the sword visible beside the right shoulder. Never turn around.")
if os.environ.get('STRICT')=='side':
    EXTRA['east']=(" Draw it like a 2D side-scroller sprite: pure side view from the right side in EVERY frame, only ONE eye visible, nose pointing right, "
                   "the back of the cape on the left; the torso stays turned 90 degrees to the camera; the sword moves in front of him on the right side.")
usage=[]; T0=time.time(); lock=threading.Lock()
def log(*a):
    s=f'[{time.strftime("%H:%M:%S")}] '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
def gen(tag,h,d,seed):
    name=f'botw_{tag}_hit{h}_{d}_s{seed}'
    desc=HIT[h]+FACE[d]+EXTRA.get(d,'')+COMMON
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
