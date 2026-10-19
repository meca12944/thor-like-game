#!/usr/bin/env python3
"""Trail B (cheap): per hit & direction, regenerate ONLY the slash window with PixelLab, drawing its own trail.
POST /characters/animations mode v3, one direction, custom_start_frame = no-effect frame s0-1, end_frame = no-effect frame s0+3,
frame_count 4 -> splice outputs into frames s0..s0+3; all other frames identical to no-effect. Key from env only."""
import os, json, time, base64, threading, shutil, urllib.request, urllib.error
O=os.environ.get('C3','/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/combo3_v1'); B=O+'/trailB'; RAW=B+'/_raw'; os.makedirs(RAW,exist_ok=True)
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
D=['south','east','north','west']
def scrub(o): return json.dumps(o,indent=2,ensure_ascii=False).replace(KEY,'<REDACTED>')
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
            if a<4: time.sleep(5); continue
            return 0,{'err':str(e)}
COMMON=(" Sword in the right hand. Front foot forward, back foot braced, NO bow-legged or crab stance. The cape flows with the body. "
 "Long straight hair, only the ends sway. Gold pauldron on the left shoulder. Face and outfit identical to the idle. Bold outlines, no flickering pixels.")
TRAIL=" A thin, faint, semi-transparent white-to-lavender crescent slash trail following the sword tip along the full blade length; no other glow or sparks."
HIT={1:"Powerful forward-stepping sword slash with the sword in the right hand: the fast slash part of the swing. The sword reaches far out in front of the body and keeps its full length.",
     2:"A quick reverse backhand horizontal slash the other way, stepping forward, the sword reaching far out in front at full length.",
     3:"Finisher: a big powerful overhead downward slash with a strong forward lunge, the heaviest hit."}
BACK=" Seen from behind: the sword must never be hidden behind the body; keep it visible above or out to the sides."
ONLY=[tuple((int(x.split(':')[0]),x.split(':')[1])) for x in os.environ.get('ONLY','').split(',') if x]
SFX='_retry' if ONLY else ''
meta=json.load(open(O+'/trailA/trailA_meta.json')); gid={}; glock=threading.Lock(); usage=[]
def b64(p): return {'type':'base64','base64':base64.b64encode(open(p,'rb').read()).decode(),'format':'png'}
T0=time.time()
def log(*a): print(f'[{int(time.time()-T0)}s]',*a,flush=True)
def job(h,d,first_evt):
    sl=meta[f'hit{h}/{d}']['slash_frames'] or [4]
    s0=max(1,min(min(sl),8-4)); st_i,en_i=s0-1,s0+3
    a=HIT[h]+COMMON+TRAIL+(" Keep facing left in profile the whole time." if d=='west' else '')+(BACK if d=='north' else '')
    body={'character_id':CID,'mode':'v3','action_description':a,'frame_count':4,'directions':[d],'animation_name':f'combo3_trailB_hit{h}',
          'keep_first_frame':False,'seed':202,'custom_start_frame':b64(f'{O}/hit{h}/{d}/{st_i:03d}.png'),'end_frame':b64(f'{O}/hit{h}/{d}/{en_i:03d}.png')}
    if first_evt is not None: first_evt.wait(300)
    with glock:
        if gid.get('g') and not ONLY: body['animation_group_id']=gid['g']
    st,r=req('POST','/characters/animations',body)
    rb={k:v for k,v in body.items() if k not in('custom_start_frame','end_frame')}; rb.update(start_index=st_i,end_index=en_i)
    open(f'{RAW}/submit_hit{h}_{d}.json','w').write(scrub({'request':rb,'http_status':st,'body':r}))
    if st!=200: log('SUBMIT FAIL',h,d,st,scrub(r)[:500]); return
    with glock: gid.setdefault('g',r.get('animation_group_id'))
    if first_evt is None: EV.set()
    j=r['background_job_ids'][0]; log('submitted',h,d,'window',st_i,en_i)
    while True:
        time.sleep(6); s,r=req('GET',f'/background-jobs/{j}')
        if r.get('status') in ('completed','failed'): break
    open(f'{RAW}/job_hit{h}_{d}.json','w').write(scrub(r))
    if r['status']!='completed': log('JOB FAIL',h,d,scrub(r)[:400]); return
    usage.append((h,d,(r.get('usage') or {}).get('generations')))
    us=r['last_response']['storage_urls']['frames']; gd=f'{RAW}/gen_hit{h}_{d}'; os.makedirs(gd,exist_ok=True)
    for i,u in enumerate(us): open(f'{gd}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})).read())
    od=f'{B}/hit{h}/{d}'; os.makedirs(od,exist_ok=True)
    for i in range(8): shutil.copy(f'{O}/hit{h}/{d}/{i:03d}.png',f'{od}/{i:03d}.png')
    n=len(us); take=list(range(n))[-4:] if n>=4 else list(range(n))   # last 4 outputs map to s0..s0+3
    for k,gi in enumerate(take): shutil.copy(f'{gd}/{gi:03d}.png',f'{od}/{s0+k:03d}.png')
    log('done',h,d,n,'frames -> spliced',s0,'..',s0+len(take)-1,r.get('usage'))
s,b=req('GET','/balance'); open(B+f'/balance_before{SFX}.json','w').write(scrub(b)); log('before',b['subscription']['generations'])
EV=threading.Event(); ts=[]
for k,(h,d) in enumerate(ONLY or [(h,d) for h in (1,2,3) for d in D]):
    t=threading.Thread(target=job,args=(h,d,None if (k==0 or ONLY) else EV)); t.start(); ts.append(t); time.sleep(0.3)
for t in ts: t.join()
s,b=req('GET','/balance'); open(B+f'/balance_after{SFX}.json','w').write(scrub(b)); log('after',b['subscription']['generations'])
json.dump({'group':gid.get('g'),'usage':usage,'job_usage_sum':sum(u[2] or 0 for u in usage),'elapsed_s':int(time.time()-T0)},open(B+f'/summary{SFX}.json','w'),indent=2)
log('sum',sum(u[2] or 0 for u in usage))
