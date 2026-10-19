#!/usr/bin/env python3
"""dash_v2 north redo: 2 jobs x 8 frames (16 gens) -> total dash_v2 spend 80. Key from env only."""
import os,json,time,urllib.request,urllib.error
A='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/dash_v2'; API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']
CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
def scrub(o): return json.dumps(o,indent=2).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=180) as f: return f.status,json.loads(f.read() or b'{}')
    except urllib.error.HTTPError as e: return e.code,{'raw':e.read().decode(errors='replace')[:1500]}
BASE=("Back view only, seen from directly behind for the entire animation: he faces straight away from the viewer, up the screen, "
 "his back, long straight black hair and black cape fill the view and his face is NEVER visible; he never turns sideways or toward the camera. "
 "Evasive dodge dash as a smooth low glide away from the viewer, like sliding on ice: frame 1 he crouches with knees bent; frames 2-6 he holds one low "
 "wide stance leaning forward away from the viewer, both boots flat on the ground and sliding, legs do NOT step, lift or alternate; the hair and the cape "
 "flutter back toward the viewer; sword held low at his right side. Frames 7-8 he brakes and rises back into his back-view ready stance. "
 "Sword in the right hand. Gold pauldron on the left shoulder only. Outfit and size identical to the idle. Bold outlines. "
 "NO glow, afterimages, dust, wind, speed lines, motion blur or any effects.")
JOBS={'n1':6303,'n2':6404}
t0=time.time(); st={}
for k,seed in JOBS.items():
    body={'character_id':CID,'mode':'v3','action_description':BASE,'frame_count':8,'directions':['north'],'animation_name':f'dash_v2{k}','keep_first_frame':False,'seed':seed}
    s,r=req('POST','/characters/animations',body); open(f'{A}/_raw/submit_{k}_north_{int(time.time())}.json','w').write(scrub({'request':body,'http_status':s,'body':r}))
    print(k,s,flush=True)
    if s==200: st[k]=r['background_job_ids'][0]
    time.sleep(3)
while st and time.time()-t0<1500:
    for k,j in list(st.items()):
        s,r=req('GET',f'/background-jobs/{j}')
        if r.get('status')=='completed':
            od=f'{A}/var_{k}/north'; os.makedirs(od,exist_ok=True)
            for i,u in enumerate(r['last_response']['storage_urls']['frames']):
                open(f'{od}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
            print('done',k,int(time.time()-t0),flush=True); del st[k]
        elif r.get('status')=='failed': print('failed',k,str(r.get('last_response'))[:200]); del st[k]
    time.sleep(8)
s,b=req('GET','/balance'); open(f'{A}/balance_after.json','w').write(scrub(b)); print('balance after',b.get('subscription',{}).get('generations'))
