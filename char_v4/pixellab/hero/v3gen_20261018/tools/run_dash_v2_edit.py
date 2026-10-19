#!/usr/bin/env python3
"""dash_v2 EDIT pass (owner order): /v2/edit-images-v2 edit_with_reference on existing dash frames, hero base as reference.
usage: run_dash_v2_edit.py <tag> <src_var> <dir> <frames,csv> <seed> ; out -> dash_v2/edit_<tag>/<dir>/NNN.png. Key from env only."""
import os,sys,json,time,base64,urllib.request,urllib.error
A='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/dash_v2'; API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']
tag,src,d,frs,seed=sys.argv[1],sys.argv[2],sys.argv[3],[int(x) for x in sys.argv[4].split(',')],int(sys.argv[5])
DESC={'north':("Same hero seen from directly behind (back view, face never visible), body facing straight up the screen, not turned sideways. "
  "Pose: low dodge glide, torso leaning forward away from the viewer, knees bent in a wide low stance, BOTH boots flat on the ground sliding, "
  "no running step, no raised foot. Long black hair and cape flutter back toward the viewer. Sword low in his right hand. Same outfit, size and proportions as the reference. No effects."),
 'west':("Same hero in side profile facing left. Pose: low dodge glide, torso leaning forward to the left, wide low lunge with the front foot forward and the back foot trailing, "
  "BOTH boots flat on the ground sliding, no running step, no raised foot. Hair and cape stream back to the right. Sword low in his right hand. Same face, outfit, size as the reference. No effects."),
 'east':("Same hero in side profile facing right. Pose: low dodge glide, torso leaning forward to the right, wide low lunge, BOTH boots flat on the ground sliding, no running step. Same face, outfit, size as the reference. No effects."),
 'south':("Same hero facing the viewer. Pose: low dodge glide toward the viewer, torso leaning forward, wide low stance, BOTH boots flat on the ground sliding, no running step. Same face, outfit, size as the reference. No effects.")}
def b64(p): return 'data:image/png;base64,'+base64.b64encode(open(p,'rb').read()).decode()
def scrub(o): return json.dumps(o,indent=1).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=180) as f: return f.status,json.loads(f.read() or b'{}')
    except urllib.error.HTTPError as e: return e.code,{'raw':e.read().decode(errors='replace')[:1500]}
od=f'{A}/edit_{tag}/{d}'; os.makedirs(od,exist_ok=True); jobs={}
ref=f'{A}/../v1_1x_descA/{d}.png'
for i in frs:
    body={'method':'edit_with_reference','edit_images':[{'image':{'base64':b64(f'{A}/{src}/{d}/{i:03d}.png')},'width':256,'height':256}],
          'image_size':{'width':256,'height':256},'reference_image':{'image':{'base64':b64(ref)},'width':256,'height':256},
          'description':DESC[d],'seed':seed+i,'no_background':True}
    s,r=req('POST','/edit-images-v2',body)
    log={k:v for k,v in body.items() if k not in('edit_images','reference_image')}; log['src']=f'{src}/{d}/{i:03d}.png'
    open(f'{A}/_raw/edit_{tag}_{d}_{i:03d}_submit.json','w').write(scrub({'request':log,'http_status':s,'body':r}))
    print('submit',d,i,s,str(r)[:300],flush=True)
    if s in (200,202): jobs[i]=r['background_job_id']
t0=time.time()
while jobs and time.time()-t0<900:
    time.sleep(6)
    for i,j in list(jobs.items()):
        s,r=req('GET',f'/background-jobs/{j}'); st=r.get('status')
        if st=='completed':
            open(f'{A}/_raw/edit_{tag}_{d}_{i:03d}_job.json','w').write(scrub({k:v for k,v in r.items() if k!='last_response'}|{'lr_keys':list((r.get('last_response') or {}).keys())}))
            lr=r['last_response']; imgs=lr.get('images') or lr.get('edited_images') or []
            if imgs:
                im=imgs[0]; data=im.get('base64') if isinstance(im,dict) else im
                if isinstance(data,str) and data.startswith('http'): raw=urllib.request.urlopen(urllib.request.Request(data,headers={'User-Agent':'Mozilla/5.0'})).read()
                elif data: raw=base64.b64decode(data.split(',')[-1])
                else: raw=None
                if raw: open(f'{od}/{i:03d}.png','wb').write(raw)
            else:
                urls=(lr.get('storage_urls') or {}); print('urls',str(urls)[:300])
            print('done',d,i,'usage',r.get('usage'),flush=True); del jobs[i]
        elif st=='failed': print('failed',i,str(r)[:300]); del jobs[i]
