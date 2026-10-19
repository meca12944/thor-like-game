#!/usr/bin/env python3
"""RUN cycle via POST /animate-character, template running-8-frames, all 8 dirs. Key from env only; responses scrubbed."""
import os, json, time, sys, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/run_v1'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']
CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
MODE=sys.argv[1] if len(sys.argv)>1 else 'template'
def scrub(o): return json.dumps(o,indent=2,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,
        headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
    except urllib.error.HTTPError as e:
        b=e.read()
        try: return e.code,json.loads(b)
        except Exception: return e.code,{'raw':b.decode(errors='replace')[:2000]}
ACT=("Fast running cycle, looping. The upper body leans forward, the sword is held in the right hand trailing low behind, "
 "and the arms swing opposite the legs. Long straight black hair with only the ends bouncing, the cape streaming behind "
 "with the body, and the gold pauldron on the left shoulder. Face and outfit identical to the idle. Bold outlines, no "
 "flickering pixels, no effects.")
DIRS=['south','south-east','east','north-east','north','north-west','west','south-west']
t0=time.time()
st,b=req('GET','/balance'); open(A+'/balance_before.json','w').write(scrub(b)); print('before',b,flush=True)
body={'character_id':CID,'mode':MODE,'template_animation_id':'running-8-frames','action_description':ACT,
      'directions':DIRS,'animation_name':'run_v1_running8','seed':303}
if MODE=='v3':
    body.pop('template_animation_id'); body.update(frame_count=8,keep_first_frame=False)
st,r=req('POST','/animate-character',body)
open(A+f'/_raw/submit_{MODE}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
print('submit',st,scrub(r)[:800],flush=True)
if st!=200: sys.exit(2)
jobs=dict(zip(r.get('directions',DIRS),r['background_job_ids']))
json.dump({'mode':MODE,'animation_group_id':r.get('animation_group_id'),'jobs':jobs},open(A+'/_raw/jobs.json','w'),indent=2)
pending=dict(jobs)
while pending and time.time()-t0<2400:
    time.sleep(8)
    for d,j in list(pending.items()):
        st,r=req('GET',f'/background-jobs/{j}')
        s=r.get('status')
        if s in ('completed','failed'):
            open(A+f'/_raw/job_{d}.json','w').write(scrub(r)); del pending[d]
            print(f'{int(time.time()-t0)}s',d,s,flush=True)
    print(f'{int(time.time()-t0)}s pending',list(pending),flush=True)
st,b=req('GET','/balance'); open(A+'/balance_after.json','w').write(scrub(b)); print('after',b)
st,r=req('GET',f'/characters/{CID}'); open(A+'/_raw/character_after.json','w').write(scrub(r))
print('elapsed',int(time.time()-t0))
