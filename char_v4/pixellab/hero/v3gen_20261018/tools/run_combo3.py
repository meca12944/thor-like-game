#!/usr/bin/env python3
"""Chained 3-hit combo. variant 'noeffect' or 'trailB'. Per direction: hit1 -> hit2 (custom_start_frame=hit1[-1]) -> hit3 (start=hit2[-1]).
Key from env only; never printed."""
import os, sys, json, time, base64, threading, urllib.request, urllib.error, shutil
V=sys.argv[1]
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=O+'/combo3_v1'+('' if V=='noeffect' else '/trailB')
ATK=O+'/atk1_v1'; RAW=C+'/_raw'; os.makedirs(RAW,exist_ok=True)
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
D=['south','east','north','west']  # owner: 4 dirs only
BACKD={'north','north-east','north-west'}
def scrub(o): return json.dumps(o,indent=2,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,
        headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for a in range(5):
        try:
            with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
        except urllib.error.HTTPError as e:
            b2=e.read()
            if e.code in (429,500,502,503,504) and a<4: time.sleep(10*(a+1)); continue
            try: return e.code,json.loads(b2)
            except Exception: return e.code,{'raw':b2.decode(errors='replace')[:2000]}
        except Exception as e:
            if a<4: time.sleep(5); continue
            return 0,{'err':str(e)}
COMMON=(" Sword in the right hand. Front foot forward, back foot braced, NO bow-legged or crab stance. The cape flows with the body. "
 "Long straight hair, only the ends sway. Gold pauldron on the left shoulder. Face and outfit identical to the idle. Bold outlines, no flickering pixels.")
NOFX=" NO slash trail, glow, sparks or any effects."
TRAIL=" A thin, faint, semi-transparent white-to-lavender crescent slash trail following the sword tip along the full blade length; no other glow or sparks."
FX = NOFX if V=='noeffect' else TRAIL
HIT1=("Powerful forward-stepping sword slash with the sword in the right hand: quick windup, big slash, follow-through. "
 "The sword reaches far out in front of the body and keeps its full length.")
HIT2=("Continue from the follow-through of the first slash: a quick reverse backhand horizontal slash the other way, stepping forward again, "
 "the sword reaching far out in front at full length.")
HIT3="Finisher: a big powerful overhead downward slash with a strong forward lunge, the heaviest hit, then hold the recovery pose."
BACK=" Seen from behind: the sword must never be hidden behind the body; keep it visible above or out to the sides."
def action(hit,d):
    a={1:HIT1,2:HIT2,3:HIT3}[hit]+COMMON+FX
    if hit==1: a+=" Timing: windup, then slash, then follow-through."
    if hit==1 and V=='noeffect': a+=" No glow, sparks, flashes or energy effects."
    if d=='west': a+=" Keep facing left in profile the whole time."
    if d in BACKD: a+=BACK
    return a
# which dirs need a generated hit1
H1GEN = ['west'] if V=='noeffect' else D
gids={}; glock=threading.Lock(); gev={h:threading.Event() for h in (1,2,3)}; owner={}
RESUME={}  # (hit,dir) -> job id from an earlier interrupted run
if V=='noeffect':
    gids={1:'64f0bbd2-ec46-4337-95e8-418415a7dd88',2:'7e91ba62-3fb0-4295-8c75-7a7138e65dce'}; owner={1:'x',2:'x'}; gev[1].set(); gev[2].set()
    for h,d in [(1,'west'),(2,'south'),(2,'north'),(2,'east')]:
        RESUME[(h,d)]=json.load(open(f'{RAW}/submit_hit{h}_{d}.json'))['body']['background_job_ids'][0]
usage=[]; ulock=threading.Lock()
def log(*a): print(f'[{int(time.time()-T0)}s]',*a,flush=True)
def b64(path): return {'type':'base64','base64':base64.b64encode(open(path,'rb').read()).decode(),'format':'png'}
def gen(hit,d,start):
    if (hit,d) in RESUME: j=RESUME[(hit,d)]; log('resume hit',hit,d); return poll(hit,d,j)
    body={'character_id':CID,'mode':'v3','action_description':action(hit,d),'frame_count':8,'directions':[d],
          'animation_name':f'combo3_{V}_hit{hit}','keep_first_frame':False,'seed':202}
    with glock:
        first = hit not in owner
        if first: owner[hit]=d
    if not first:
        gev[hit].wait(600)
        if gids.get(hit): body['animation_group_id']=gids[hit]
    if start: body['custom_start_frame']=b64(start)
    st,r=req('POST','/characters/animations',body)
    rb=dict(body); rb.pop('custom_start_frame',None); rb['custom_start_frame_path']=start
    open(f'{RAW}/submit_hit{hit}_{d}.json','w').write(scrub({'request':rb,'http_status':st,'body':r}))
    if first:
        if st==200: gids[hit]=r.get('animation_group_id')
        gev[hit].set()
    if st!=200: log('SUBMIT FAIL',hit,d,st,scrub(r)[:400]); return None
    j=r['background_job_ids'][0]; log('submitted hit',hit,d)
    return poll(hit,d,j)
def poll(hit,d,j):
    while True:
        time.sleep(6); st,r=req('GET',f'/background-jobs/{j}')
        if r.get('status') in ('completed','failed'): break
    open(f'{RAW}/job_hit{hit}_{d}.json','w').write(scrub(r))
    if r['status']!='completed': log('JOB FAIL',hit,d,scrub(r)[:400]); return None
    with ulock: usage.append((hit,d,(r.get('usage') or {}).get('generations')))
    out=f'{C}/hit{hit}/{d}'; os.makedirs(out,exist_ok=True)
    for i,u in enumerate(r['last_response']['storage_urls']['frames']):
        open(f'{out}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})).read())
    log('done hit',hit,d,len(r['last_response']['storage_urls']['frames']),'frames',r.get('usage'))
    return f'{out}/{len(os.listdir(out))-1:03d}.png'
def chain(d):
    if d in H1GEN: last=gen(1,d,None)
    else:
        out=f'{C}/hit1/{d}'; os.makedirs(out,exist_ok=True)
        for f in sorted(os.listdir(f'{ATK}/{d}')): shutil.copy(f'{ATK}/{d}/{f}',out)
        last=f'{out}/007.png'
    if not last: return
    last=gen(2,d,last)
    if not last: return
    gen(3,d,last)
T0=time.time()
st,b=req('GET','/balance'); open(C+('/balance_before.json' if not os.path.exists(C+'/balance_before.json') else '/balance_resume.json'),'w').write(scrub(b)); log('before',b['subscription']['generations'])
# order threads so a hit-2 group creator submits early (dirs with copied hit1 first)
order=sorted(D,key=lambda d: d in H1GEN)
ts=[threading.Thread(target=chain,args=(d,)) for d in order]
for t in ts: t.start(); time.sleep(0.5)
for t in ts: t.join()
st,b=req('GET','/balance'); open(C+'/balance_after.json','w').write(scrub(b)); log('after',b['subscription']['generations'])
json.dump({'groups':gids,'usage':usage,'job_usage_sum':sum(u[2] or 0 for u in usage),'elapsed_s':int(time.time()-T0)},open(C+'/summary.json','w'),indent=2)
log('summary',gids,'sum',sum(u[2] or 0 for u in usage))
