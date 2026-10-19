#!/usr/bin/env python3
"""Supervisor for moves_v1: adopts already-submitted jobs, queues the rest under MY_CAP active jobs,
retries failures (heavy load) per direction up to 3 times, downloads frames, builds sheets per motion.
Key from env only; responses scrubbed. State in _raw/state.json (resumable)."""
import os, json, time, glob, urllib.request, urllib.error, subprocess
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/moves_v1'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']
CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'; CAP=int(os.environ.get('MY_CAP','12')); MAXTRY=4
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
MOT={'run':"Fast running cycle, looping: upper body leaning forward, sword held low trailing behind, arms swinging opposite the legs, the cape streaming behind. ",
 'dash':"Quick evasive forward dash: crouch, burst forward low with the body leaning hard, the cape and hair flaring back, then recover to stance. ",
 'walk':"Calm walking cycle, looping: relaxed upright posture, sword held in the right hand low at the side, arms swinging gently opposite the legs, the cape swaying with the stride, hair ends swaying. ",
 'jump':"Jump in place: crouch to anticipate, spring up with knees tucked, the cape and hair lifting, land with a knee bend, recover. ",
 'idle':"Idle loop, looping: standing ready, subtle breathing, sword in right hand lowered, cape and hair ends gently swaying. ",
 'hurt':"Getting hit: a sharp flinch backward, upper body recoils, then recover to stance. ",
 'death':"Collapsing defeated: staggers, drops to the knees, falls to the ground and lies still; the sword drops. ",
 'cast':"Skill cast: plants feet, raises the left hand forward and the sword in the right hand to the side, gathers power, then releases with a push forward. No magic effects. ",
 'guard':"Blocking: raises the sword horizontally in front of the body to block, braces, holds, then lowers. "}
SEED={'run':411,'dash':412,'jump':413,'walk':414,'idle':421,'hurt':422,'death':423,'cast':424,'guard':425}
GROUPS=[['south','north'],['east','west']]
t0=time.time()
def log(*a): print(f'[{int(time.time()-t0)}s]',*a,flush=True)
SP=A+'/_raw/state.json'
if os.path.exists(SP): S=json.load(open(SP))
else:
    S={'jobs':{},'gid':{},'total':0}
    for m in MOT:
        for d in ['south','north','east','west']: S['jobs'][f'{m}/{d}']={'job':None,'tries':0,'status':'queued'}
    for f in glob.glob(A+'/_raw/submit_*.json'):
        x=json.load(open(f))
        if x['http_status']!=200: continue
        m=x['request']['animation_name'].split('_')[0]; S['gid'].setdefault(m,x['body'].get('animation_group_id'))
        for d,j in zip(x['body']['directions'],x['body']['background_job_ids']):
            S['jobs'][f'{m}/{d}']={'job':j,'tries':1,'status':'running'}
def save(): json.dump(S,open(SP,'w'),indent=2)
save()
if not os.path.exists(A+'/balance_before_sup.json'):
    st,b=req('GET','/balance'); open(A+'/balance_before_sup.json','w').write(scrub(b)); log('balance now',b.get('subscription',{}).get('generations'))
def submit(m,dirs):
    extra=SIDE if dirs[0] in ('east','west') else ''
    body={'character_id':CID,'mode':'v3','action_description':MOT[m]+COMMON+extra,'frame_count':8,'directions':dirs,
          'animation_name':f'{m}_v1','keep_first_frame':False,'seed':SEED[m]}
    if S['gid'].get(m): body['animation_group_id']=S['gid'][m]
    st,r=req('POST','/characters/animations',body)
    open(A+f'/_raw/submit_{m}_{"-".join(dirs)}_{int(time.time())}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
    if st!=200: log('submit FAIL',m,dirs,st,str(r.get('detail',r))[:160]); return False
    S['gid'].setdefault(m,r.get('animation_group_id'))
    for d,j in zip(r['directions'],r['background_job_ids']):
        k=f'{m}/{d}'; S['jobs'][k].update(job=j,status='running'); S['jobs'][k]['tries']+=1
    save(); log('submit',m,dirs); return True
def motion_done(m):
    if all(S['jobs'][f'{m}/{d}']['status'] in ('completed','gaveup') for d in ['south','north','east','west']):
        if not S.setdefault('sheet',{}).get(m):
            out=subprocess.run(['python3',O+'/tools/sheet_moves.py',m],capture_output=True,text=True)
            S['sheet'][m]=True; save(); log('MOTION COMPLETE',m,out.stdout.strip(),out.stderr.strip()[-300:])
backoff=0
while time.time()-t0<7200:
    J=S['jobs']
    # poll running
    for k,v in J.items():
        if v['status']!='running': continue
        st,r=req('GET',f'/background-jobs/{v["job"]}'); s=r.get('status')
        if s not in ('completed','failed'): continue
        m,d=k.split('/'); open(A+f'/_raw/job_{m}_{d}.json','w').write(scrub(r))
        if s=='completed':
            urls=r['last_response']['storage_urls']['frames']; os.makedirs(f'{A}/{m}/{d}',exist_ok=True)
            for i,u in enumerate(urls):
                open(f'{A}/{m}/{d}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
            g=(r.get('usage') or {}).get('generations',0); S['total']+=g; v['status']='completed'; v['elapsed_s']=int(time.time()-t0)
            log('done',k,len(urls),'frames usage',g)
        else:
            err=str((r.get('last_response') or {}).get('error'))[:120]
            v['status']='queued' if v['tries']<MAXTRY else 'gaveup'; log('FAILED',k,'try',v['tries'],err,'->',v['status'])
        save(); motion_done(m)
    # submit queued
    active=sum(1 for v in J.values() if v['status']=='running')
    if time.time()>=backoff:
        for m in MOT:
            for g in GROUPS:
                q=[d for d in g if J[f'{m}/{d}']['status']=='queued']
                if not q: continue
                if active+len(q)>CAP: q=q[:max(0,CAP-active)]
                if not q: continue
                if submit(m,q): active+=len(q)
                else: backoff=time.time()+20; break
            if time.time()<backoff: break
    if all(v['status'] in ('completed','gaveup') for v in J.values()): break
    time.sleep(10)
st,b=req('GET','/balance'); open(A+'/balance_after.json','w').write(scrub(b)); log('after',b.get('subscription',{}).get('generations'),'usage sum',S['total'])
log('final',{k:v['status'] for k,v in S['jobs'].items()})
