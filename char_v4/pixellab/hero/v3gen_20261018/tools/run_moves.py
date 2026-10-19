#!/usr/bin/env python3
"""RUN/DASH/JUMP, v3 mode 8 frames, 4 dirs, all 12 jobs submitted concurrently. Key from env only; responses scrubbed."""
import os, json, time, urllib.request, urllib.error, subprocess
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/moves_v1'
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
    except Exception as e: return -1,{'error':str(e)}
COMMON=("Sword in the right hand. Long straight black hair, only the ends sway. The cape flows with the body. "
 "Gold pauldron on the left shoulder. Face and outfit identical to the idle. Bold outlines, no flickering pixels. "
 "NO glow, sparks, dust, flashes or any effects. Keep facing the same direction the whole time.")
SIDE=" Stay in side profile."
MOT={'run':"Fast running cycle, looping: upper body leaning forward, sword held low trailing behind, arms swinging opposite the legs, the cape streaming behind. ",
     'dash':"Quick evasive forward dash: crouch, burst forward low with the body leaning hard, the cape and hair flaring back, then recover to stance. ",
     'jump':"Jump in place: crouch to anticipate, spring up with knees tucked, the cape and hair lifting, land with a knee bend, recover. "}
SEED={'run':411,'dash':412,'jump':413}
def log(*a): print(f'[{int(time.time()-t0)}s]',*a,flush=True)
t0=time.time()
st,b=req('GET','/balance'); open(A+'/balance_before.json','w').write(scrub(b)); log('before',b.get('subscription',{}).get('generations'))
jobs={}
for m,act in MOT.items():
    gid=None
    for dirs,extra in ((['south','north'],''),(['east','west'],SIDE)):
        body={'character_id':CID,'mode':'v3','action_description':act+COMMON+extra,'frame_count':8,'directions':dirs,
              'animation_name':f'{m}_v1','keep_first_frame':False,'seed':SEED[m]}
        if gid: body['animation_group_id']=gid
        st,r=req('POST','/characters/animations',body)
        open(A+f'/_raw/submit_{m}_{dirs[0]}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
        log('submit',m,dirs,st,scrub(r)[:300] if st!=200 else '')
        if st!=200: continue
        gid=gid or r.get('animation_group_id')
        for d,j in zip(r['directions'],r['background_job_ids']): jobs[(m,d)]=j
json.dump({f'{m}/{d}':j for (m,d),j in jobs.items()},open(A+'/_raw/jobs.json','w'),indent=2)
pending=dict(jobs); done={m:0 for m in MOT}; total=0
while pending and time.time()-t0<3000:
    time.sleep(8)
    for (m,d),j in list(pending.items()):
        st,r=req('GET',f'/background-jobs/{j}')
        s=r.get('status')
        if s not in ('completed','failed'): continue
        open(A+f'/_raw/job_{m}_{d}.json','w').write(scrub(r)); del pending[(m,d)]
        if s=='completed':
            urls=r['last_response']['storage_urls']['frames']; os.makedirs(f'{A}/{m}/{d}',exist_ok=True)
            for i,u in enumerate(urls):
                open(f'{A}/{m}/{d}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
            g=(r.get('usage') or {}).get('generations',0); total+=g
            log('done',m,d,len(urls),'frames usage',g)
        else: log('FAILED',m,d,scrub(r)[:400])
        done[m]+=1
        if done[m]==4:
            log('MOTION COMPLETE',m, subprocess.run(['python3',O+'/tools/sheet_moves.py',m],capture_output=True,text=True).stdout.strip())
st,b=req('GET','/balance'); open(A+'/balance_after.json','w').write(scrub(b)); log('after',b.get('subscription',{}).get('generations'),'usage sum',total)
log('pending left',list(pending))
