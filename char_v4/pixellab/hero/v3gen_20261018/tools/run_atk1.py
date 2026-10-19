#!/usr/bin/env python3
"""Submit sword attack (v3 custom, 8 frames) for all 8 dirs; poll; save raw job responses. Key from env only."""
import os, json, time, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/atk1_v1'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']
CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
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
ACT=("Powerful forward-stepping sword slash with the sword in the right hand: quick windup, big slash, follow-through. "
 "The front foot steps forward and the back foot braces (NO bow-legged or crab stance). The sword reaches far out in front "
 "of the body and keeps its full length. The cape flows with the body. Long straight hair, only the ends sway. Gold pauldron "
 "stays on the left shoulder. Face and outfit identical to the idle. Bold outlines, no flickering pixels. No slash trail or effect.")
BACK=(" Timing: windup, then slash, then follow-through. Seen from behind: the sword must never be hidden behind the body; "
 "it stays visible above the body or out to the sides.")
FRONT=" Timing: windup, then slash, then follow-through."
GROUPS=[(['south','south-east','east','west','south-west'],FRONT),(['north','north-east','north-west'],BACK)]
t0=time.time()
st,b=req('GET','/balance'); open(A+'/balance_before.json','w').write(scrub(b)); print('before',b,flush=True)
jobs={}; gid=None
for dirs,extra in GROUPS:
    body={'character_id':CID,'mode':'v3','action_description':ACT+extra,'frame_count':8,'directions':dirs,
          'animation_name':'atk1_forward_slash','keep_first_frame':False,'seed':202}
    if gid: body['animation_group_id']=gid
    st,r=req('POST','/characters/animations',body)
    open(A+f'/_raw/submit_{dirs[0]}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
    print('submit',st,scrub(r)[:600],flush=True)
    if st!=200: continue
    gid=gid or r.get('animation_group_id')
    for d,j in zip(r['directions'],r['background_job_ids']): jobs[d]=j
json.dump({'animation_group_id':gid,'jobs':jobs},open(A+'/_raw/jobs.json','w'),indent=2)
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
