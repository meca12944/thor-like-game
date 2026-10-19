#!/usr/bin/env python3
"""IDLE/HURT/DEATH/CAST/GUARD, v3 8 frames, 4 dirs. Queued: only submit while MY active jobs (all moves_v1 submits) < CAP.
Key from env only; responses scrubbed."""
import os, json, time, glob, urllib.request, urllib.error, subprocess
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/moves_v1'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']
CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'; CAP=int(os.environ.get('MY_CAP','10'))
def scrub(o): return json.dumps(o,indent=2,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,
        headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=180) as f: return f.status,json.loads(f.read() or b'{}')
    except urllib.error.HTTPError as e:
        b=e.read()
        try: return e.code,json.loads(b)
        except Exception: return e.code,{'raw':b.decode(errors='replace')[:2000]}
    except Exception as e: return -1,{'error':str(e)}
COMMON=("Sword in the right hand. Long straight black hair, only the ends sway. The cape flows with the body. "
 "Gold pauldron on the left shoulder. Face and outfit identical to the idle. Bold outlines, no flickering pixels. "
 "NO glow, sparks, dust, flashes or any effects. Keep facing the same direction the whole time.")
SIDE=" Stay in side profile."
MOT={'jump':"Jump in place: crouch to anticipate, spring up with knees tucked, the cape and hair lifting, land with a knee bend, recover. ",
 'idle':"Idle loop, looping: standing ready, subtle breathing, sword in right hand lowered, cape and hair ends gently swaying. ",
 'hurt':"Getting hit: a sharp flinch backward, upper body recoils, then recover to stance. ",
 'death':"Collapsing defeated: staggers, drops to the knees, falls to the ground and lies still; the sword drops. ",
 'cast':"Skill cast: plants feet, raises the left hand forward and the sword in the right hand to the side, gathers power, then releases with a push forward. No magic effects. ",
 'guard':"Blocking: raises the sword horizontally in front of the body to block, braces, holds, then lowers. "}
SEED={'jump':413,'idle':421,'hurt':422,'death':423,'cast':424,'guard':425}
t0=time.time()
def log(*a): print(f'[{int(time.time()-t0)}s]',*a,flush=True)
status={}  # job_id -> terminal status cache
def my_active():
    ids=[]
    for f in glob.glob(A+'/_raw/submit_*.json'):
        try: ids+=json.load(open(f))['body'].get('background_job_ids',[])
        except Exception: pass
    n=0
    for j in ids:
        if j in status: continue
        st,r=req('GET',f'/background-jobs/{j}'); s=r.get('status')
        if s in ('completed','failed'): status[j]=s
        else: n+=1
    return n
st,b=req('GET','/balance'); open(A+'/balance_before_q.json','w').write(scrub(b)); log('before',b.get('subscription',{}).get('generations'))
queue=[(m,dirs,extra) for m in MOT for dirs,extra in ((['south','north'],''),(['east','west'],SIDE))]
gid={}; mine={}; done={m:0 for m in MOT}; total=0
while (queue or mine) and time.time()-t0<5400:
    if queue:
        act=my_active()
        while queue and act+2<=CAP:
            m,dirs,extra=queue[0]
            body={'character_id':CID,'mode':'v3','action_description':MOT[m]+COMMON+extra,'frame_count':8,'directions':dirs,
                  'animation_name':f'{m}_v1','keep_first_frame':False,'seed':SEED[m]}
            if m in gid: body['animation_group_id']=gid[m]
            st,r=req('POST','/characters/animations',body)
            open(A+f'/_raw/submit_{m}_{dirs[0]}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
            if st!=200:
                log('submit FAIL',m,dirs,st,scrub(r)[:300]); break  # back off, retry next loop
            queue.pop(0); act+=2; gid.setdefault(m,r.get('animation_group_id'))
            for d,j in zip(r['directions'],r['background_job_ids']): mine[(m,d)]=j
            log('submit',m,dirs,'my_active~',act,'queued',len(queue))
    time.sleep(10)
    for (m,d),j in list(mine.items()):
        st,r=req('GET',f'/background-jobs/{j}'); s=r.get('status')
        if s not in ('completed','failed'): continue
        status[j]=s; open(A+f'/_raw/job_{m}_{d}.json','w').write(scrub(r)); del mine[(m,d)]
        if s=='completed':
            urls=r['last_response']['storage_urls']['frames']; os.makedirs(f'{A}/{m}/{d}',exist_ok=True)
            for i,u in enumerate(urls):
                open(f'{A}/{m}/{d}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
            g=(r.get('usage') or {}).get('generations',0); total+=g; log('done',m,d,len(urls),'frames usage',g)
        else: log('FAILED',m,d,scrub(r)[:400])
        done[m]+=1
        if done[m]==4: log('MOTION COMPLETE',m,subprocess.run(['python3',O+'/tools/sheet_moves.py',m],capture_output=True,text=True).stdout.strip())
st,b=req('GET','/balance'); open(A+'/balance_after_q.json','w').write(scrub(b)); log('after',b.get('subscription',{}).get('generations'),'usage sum',total)
log('left queue',queue,'pending',list(mine))
