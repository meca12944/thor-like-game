#!/usr/bin/env python3
"""character_to_portrait via POST /v2/portrait-character-pro, one job at a time.
Key read from env PIXELLAB_API_KEY; never written anywhere."""
import os, sys, json, time, base64, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'
D=f'{O}/portrait_v1'
API='https://api.pixellab.ai/v2'
KEY=os.environ['PIXELLAB_API_KEY']
def scrub(o): return json.dumps(o,indent=2,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(method,path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    r=urllib.request.Request(API+path,data=data,method=method,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
    except urllib.error.HTTPError as e:
        b=e.read()
        try: return e.code,json.loads(b)
        except Exception: return e.code,{'raw':b.decode(errors='replace')[:2000]}
def strip_imgs(o):
    if isinstance(o,dict): return {k:(f'<{len(v)} chars>' if k=='base64' and isinstance(v,str) else strip_imgs(v)) for k,v in o.items()}
    if isinstance(o,list): return [strip_imgs(x) for x in o]
    return o
def save_img(img,path):
    if isinstance(img,dict):
        if img.get('base64'):
            b=img['base64'].split(',',1)[-1]; open(path,'wb').write(base64.b64decode(b)); return True
        if img.get('url'): urllib.request.urlretrieve(img['url'],path); return True
    if isinstance(img,str):
        if img.startswith('http'): urllib.request.urlretrieve(img,path)
        else: open(path,'wb').write(base64.b64decode(img.split(',',1)[-1]))
        return True
    return False
# usage: run_portrait_v1.py <tag> <src relative to O> name:seed [name:seed ...]
TAG=sys.argv[1]; SRCREL=sys.argv[2]; SRC=f'{O}/{SRCREL}'
jobs=[a.split(':') for a in sys.argv[3:]]
st,b=req('GET','/balance'); open(f'{D}/balance_before_{TAG}.json','w').write(scrub(b)); print('balance before',b.get('subscription',{}).get('generations'),flush=True)
b64=base64.b64encode(open(SRC,'rb').read()).decode()
for name,seed in jobs:
    seed=int(seed)
    body={'direction':'character_to_portrait','image':{'type':'base64','base64':b64,'format':'png'},
          'view':'low top-down','result_size':128,'seed':seed}
    lg=dict(body); lg['image']={'type':'base64','format':'png','base64':f'<{SRCREL}>'}; lg['_endpoint']='POST /v2/portrait-character-pro'
    open(f'{D}/{name}_request.json','w').write(scrub(lg))
    for attempt in range(60):
        st,r=req('POST','/portrait-character-pro',body)
        if st!=429: break
        print(' 429, slots full; retry in 20s',flush=True); time.sleep(20)
    print(name,'submit',st,strip_imgs(r),flush=True)
    jid=r.get('background_job_id') or r.get('job_id') if isinstance(r,dict) else None
    if not jid: continue
    t0=time.time()
    while time.time()-t0<600:
        time.sleep(8)
        st,j=req('GET',f'/background-jobs/{jid}')
        s=j.get('status'); print(f' {int(time.time()-t0)}s',s,flush=True)
        if s in ('completed','failed','error'): break
    open(f'{D}/{name}_job.json','w').write(scrub(strip_imgs(j)))
    lr=j.get('last_response') or {}
    imgs=lr.get('images') or ([lr['image']] if lr.get('image') else [])
    if imgs and save_img(imgs[0],f'{D}/{name}.png'): print(' saved',name,flush=True)
    else: print(' no image',scrub(strip_imgs(j))[:1500],flush=True)
st,b=req('GET','/balance'); open(f'{D}/balance_after_{TAG}.json','w').write(scrub(b)); print('balance after',b.get('subscription',{}).get('generations'),flush=True)
