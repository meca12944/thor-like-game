#!/usr/bin/env python3
"""combo3_v3: owner fixes — every hit a forward-advancing lunge, BIGGER white smear following full blade length, hit3 biggest;
west truly faces left; north cape to the side, sword visible. No chaining (chaining from wrong-facing hit2 west caused left hit3 to face right).
One dir per request, new animation names. Key from env only; never printed."""
import os, json, time, threading, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=O+os.environ.get('COMBO_OUT','/combo3_v3'); RAW=C+'/_raw'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
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
            if a<6: time.sleep(5); continue
            return 0,{'err':str(e)}
COMMON=(" Sword in the right hand. Long straight black hair, black coat with gold trim, red cape lining, gold pauldron on the left shoulder only. "
 "Face, outfit and size identical to the idle. Bold outlines, no flickering pixels. No glow, sparks, smoke, dust or other effects except the slash smear.")
LUNGE=(" Every slash ADVANCES: the front foot steps forward and the body drives forward into the cut, weight shifted onto the front leg.")
SMEAR=(" A BIG crisp white crescent slash smear follows the sword tip along the full blade length, sweeping a wide arc at a large radius around the body.")
HIT={1:"Hit 1 of a sword combo: a fast forward lunging slash, the sword sweeping in a wide arc in front of the body at full arm extension.",
 2:"Hit 2 of a sword combo: a forward lunging reverse backhand slash sweeping the opposite way in a wide arc at full arm extension.",
 3:("Hit 3, the BIG finishing slash: the biggest windup with the sword drawn far back, then a strong deep forward lunge and an explosive, very wide, "
    "long sweeping cut with the sword reaching far out in front at full extension; hold the follow-through. The biggest smear of the combo.")}
FACE={'south':" Keep facing the camera the whole time.",'east':" Keep facing RIGHT in side profile the whole time, swinging to the right; never turn around.",
 'west':" Keep facing LEFT in side profile the whole time, lunging and swinging to the LEFT; never turn to the right.",
 'north':(" Back view the whole time, face never shown. The sword must never be hidden: keep it clearly visible out to the side or above. "
  "The cape swings out to the side or stays behind the legs, never over the back; the hair, the back, the sword arm stay readable, "
  "the red cape lining and gold trim visible.")}
JOBS=[(h,d) for h in (1,2,3) for d in ('south','east','west','north')]
import sys
if len(sys.argv)>1: JOBS=[(int(a[0]),a[2:]) for a in sys.argv[1:]]
usage=[]; T0=time.time()
def log(*a): print(f'[{int(time.time()-T0)}s]',*a,flush=True)
def gen(h,d,seed=304):
    name=f'combo3v3s_hit{h}_{d}'
    body={'character_id':CID,'mode':'v3','action_description':HIT[h]+LUNGE+SMEAR+COMMON+FACE[d],'frame_count':8,'directions':[d],
          'animation_name':name,'keep_first_frame':False,'seed':seed}
    if os.environ.get('START'):
        import base64; body['custom_start_frame']={'type':'base64','base64':base64.b64encode(open(O+'/v1_1x_descA/'+d+'.png','rb').read()).decode(),'format':'png'}
    st,r=req('POST','/characters/animations',body)
    body.pop('custom_start_frame',None); body['custom_start_frame_path']='v1_1x_descA/'+d+'.png' if os.environ.get('START') else None
    open(f'{RAW}/submit_hit{h}_{d}_{int(time.time())}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
    if st!=200: log('SUBMIT FAIL',h,d,st,scrub(r)[:300]); return
    j=r['background_job_ids'][0]; log('submitted',h,d)
    while True:
        time.sleep(8); st,r=req('GET',f'/background-jobs/{j}')
        if r.get('status') in ('completed','failed'): break
    open(f'{RAW}/job_hit{h}_{d}.json','w').write(scrub(r))
    if r['status']!='completed': log('JOB FAIL',h,d,scrub(r)[:300]); return
    usage.append((h,d,(r.get('usage') or {}).get('generations')))
    out=f'{C}/hit{h}/{d}'; os.makedirs(out,exist_ok=True)
    for i,u in enumerate(r['last_response']['storage_urls']['frames']):
        open(f'{out}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
    log('done',h,d,r.get('usage'))
st,b=req('GET','/balance'); open(C+'/balance_before.json','w').write(scrub(b)); log('before',b['subscription']['generations'])
ts=[threading.Thread(target=gen,args=jd) for jd in JOBS]
for t in ts: t.start(); time.sleep(1.5)
for t in ts: t.join()
st,b=req('GET','/balance'); open(C+'/balance_after.json','w').write(scrub(b)); log('after',b['subscription']['generations'])
json.dump({'usage':usage,'sum':sum(u[2] or 0 for u in usage)},open(C+'/summary.json','w'),indent=2)
