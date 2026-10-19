#!/usr/bin/env python3
"""remake_v1 (owner 2026-10-19): hero 3-hit combo remade from the current character fb140a07, NO baked effects (engine draws the trails), strict per-dir views, compact stance. Preview only.
usage: run_remake.py [tag] h:dir[:seed] ...   -> candidates in remake/_cand/<tag>/hit<h>/<dir>/
Budget: cap env CAP (default 200) generations summed from own job records in remake/_raw/job_*.json. Key from env only; never printed."""
import os, sys, json, time, glob, threading, urllib.request, urllib.error
C='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/move'; RAW=C+'/_raw'; os.makedirs(RAW,exist_ok=True)
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
CAP=int(os.environ.get('CAP','40')); FC=int(os.environ.get('FC','8'))
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
COMMON=(" Same character in every frame exactly as the idle image: same face and eyes, same long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron, same proportions and same size. "
 "The longsword is held LOW in the RIGHT hand at his side, blade pointing down and slightly outward. The cape and hair hang and flow BEHIND and beside him, never rising over his head. "
 "Feet on the same ground line, clean pixels, no effects.")
HIT={1:("Walk cycle, 8 frames, seamless loop: a natural walk toward the camera. The legs clearly alternate with visible steps (left foot forward, passing, right foot forward, passing), "
        "knees bend, the free left arm swings opposite to the legs, slight up-and-down body bob of 1-2 pixels."),
     2:("Run cycle, 8 frames, seamless loop: a fast run toward the camera. Body leans slightly forward, legs pump with high knees and long strides, one frame with both feet off the ground, "
        "the free left arm swings strongly, hair and cape stream back behind the shoulders.")}
FACE={'south':" TRUE FRONT VIEW every frame: he faces the camera and moves DOWN the screen toward the viewer; he never turns sideways or away."}
FACE4=FACE
usage=[]; T0=time.time(); lock=threading.Lock()
def log(*a):
    s=f'[{time.strftime("%H:%M:%S")}] '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
def gen(tag,h,d,seed):
    name=f'move_{tag}_hit{h}_{d}_s{seed}'
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
