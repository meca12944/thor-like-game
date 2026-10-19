#!/usr/bin/env python3
"""dash_v2: redo hero DODGE DASH as a low GLIDE (no stepping), v3 mode, 8 frames, 4 dirs x 2 variants,
one direction per request. New animation names/groups (dash_v2a, dash_v2b). Key from env only; responses scrubbed.
Resumable: state in dash_v2/_raw/state.json. Hard budget cap on submitted generations."""
import os, json, time, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/dash_v2'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']
CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'; MAXTRY=2; BUDGET=80; PERJOB=8
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
COMMON=("Sword in the right hand. Long straight black hair. Black coat with gold trim, red cape lining. "
 "Gold pauldron on the left shoulder only. Face, outfit and size identical to the idle. Bold outlines, no flickering pixels. "
 "NO glow, afterimages, dust, wind, speed lines, motion blur or any effects. Keep facing the same direction the whole time, never turn toward the camera.")
DIRH={'south':" He faces the viewer the whole time and glides toward the viewer (down the screen); the cape and hair stream back behind him.",
 'north':" Back view the whole time, he faces away from the viewer and his face is never shown; he glides away up the screen and the cape and hair stream back toward the viewer.",
 'east':" Stay in side profile facing right the whole time; he glides to the right and the cape and hair stream back to the left.",
 'west':" Stay in side profile facing left the whole time; he glides to the left and the cape and hair stream back to the right."}
VAR={
 'a':{'seed':6101,'text':("Evasive dodge dash that is a smooth low glide, like sliding on ice, not running. "
   "Frame 1: quick crouch, knees bent, pushing off. Frames 2-6: hold one low forward-leaning glide pose, "
   "both feet staying flat on the ground, one foot forward and one foot trailing behind, the legs do NOT step or alternate, no jumping; "
   "hair and cape streaming back, sword held low and back behind him. Frames 7-8: braking slide, the front foot plants and he rises back into the ready stance. ")},
 'b':{'seed':6202,'text':("Low gliding dodge dash: he crouches and pushes off, then slides forward in one frozen low lunge, "
   "leaning forward, front foot forward and back foot trailing, both feet skimming the ground without any steps, "
   "the long hair and cape blown straight back, the sword held low and pointing back. "
   "He then brakes with a short skid and straightens up into his combat-ready stance. ")}}
DIRS=['south','north','east','west']
t0=time.time()
def log(*a): print(f'[{int(time.time()-t0)}s]',*a,flush=True)
SP=A+'/_raw/state.json'
if os.path.exists(SP): S=json.load(open(SP))
else: S={'jobs':{f'{v}/{d}':{'job':None,'tries':0,'status':'queued'} for v in VAR for d in DIRS},'gid':{},'total':0,'submitted':0}
def save(): json.dump(S,open(SP,'w'),indent=2)
if not os.path.exists(A+'/balance_before.json'):
    st,b=req('GET','/balance'); open(A+'/balance_before.json','w').write(scrub(b)); log('balance before',b.get('subscription',{}).get('generations'))
save()
def submit(v,d):
    sfx=S.get('suffix',{}).get(v,'')
    body={'character_id':CID,'mode':'v3','action_description':VAR[v]['text']+COMMON+DIRH[d],'frame_count':8,'directions':[d],
          'animation_name':f'dash_v2{v}{sfx}','keep_first_frame':False,'seed':VAR[v]['seed']}
    if S['gid'].get(v+sfx): body['animation_group_id']=S['gid'][v+sfx]
    st,r=req('POST','/characters/animations',body)
    open(A+f'/_raw/submit_{v}_{d}_{int(time.time())}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
    if st!=200:
        msg=str(r.get('detail',r))[:200]; log('submit FAIL',v,d,st,msg)
        if 'already' in msg.lower(): S.setdefault('suffix',{})[v]='_r'+str(int(time.time())%10000)
        save(); return False
    S['gid'].setdefault(v+sfx,r.get('animation_group_id'))
    k=f'{v}/{d}'; S['jobs'][k].update(job=r['background_job_ids'][0],status='running'); S['jobs'][k]['tries']+=1; S['submitted']+=PERJOB
    save(); log('submit',v,d,r.get('animation_group_id')); return True
backoff=0
while time.time()-t0<5400:
    J=S['jobs']
    for k,v in J.items():
        if v['status']!='running': continue
        st,r=req('GET',f'/background-jobs/{v["job"]}'); s=r.get('status')
        if s not in ('completed','failed'): continue
        var,d=k.split('/'); open(A+f'/_raw/job_{var}_{d}_t{v["tries"]}.json','w').write(scrub(r))
        if s=='completed':
            urls=r['last_response']['storage_urls']['frames']; od=f'{A}/var_{var}/{d}'; os.makedirs(od,exist_ok=True)
            for i,u in enumerate(urls):
                open(f'{od}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
            g=(r.get('usage') or {}).get('generations',0); S['total']+=g; v['status']='completed'
            log('done',k,len(urls),'frames usage',g,'total',S['total'])
        else:
            S['submitted']-=PERJOB  # failed jobs are not charged
            err=str((r.get('last_response') or {}).get('error'))[:160]
            v['status']='queued' if v['tries']<MAXTRY else 'gaveup'; log('FAILED',k,'try',v['tries'],err,'->',v['status'])
        save()
    if time.time()>=backoff:
        for k,v in J.items():
            if v['status']!='queued': continue
            if S['submitted']+PERJOB>BUDGET: log('budget cap, skip',k); v['status']='gaveup'; save(); continue
            var,d=k.split('/')
            if not submit(var,d): backoff=time.time()+20; break
    if all(v['status'] in ('completed','gaveup') for v in J.values()): break
    time.sleep(10)
st,b=req('GET','/balance'); open(A+'/balance_after.json','w').write(scrub(b)); log('balance after',b.get('subscription',{}).get('generations'),'usage sum',S['total'])
log('final',{k:v['status'] for k,v in S['jobs'].items()})
