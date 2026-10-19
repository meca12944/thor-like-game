#!/usr/bin/env python3
"""Submit PixelLab create-character-v3 jobs, poll, download rotations.
Key is read from env PIXELLAB_API_KEY (source ~/.config/pixellab/env); never written anywhere."""
import os, sys, json, time, base64, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'
API='https://api.pixellab.ai/v2'
KEY=os.environ['PIXELLAB_API_KEY']
def scrub(o):
    s=json.dumps(o,indent=2,ensure_ascii=False)
    return s.replace(KEY,'<REDACTED>')
def req(method,path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    r=urllib.request.Request(API+path,data=data,method=method,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
    except urllib.error.HTTPError as e:
        b=e.read()
        try: return e.code,json.loads(b)
        except Exception: return e.code,{'raw':b.decode(errors='replace')[:2000]}
DA=("adult male swordsman hero, long straight black hair falling down his back with only the ends flowing, "
    "black high-collar coat with gold trim, black cape with red lining, single gold pauldron on his left shoulder only, "
    "longsword, dark-brown eyes, bold dark outline, top-down 3/4 RPG view")
DB=("pixel art RPG hero, adult man about 5 heads tall, long straight black hair (not wavy, only the tips flow), "
    "dark-brown eyes, black high-collared coat with gold trim and a red gem clasp, long black cape with crimson lining, "
    "one gold shoulder pauldron on his LEFT shoulder only (the right shoulder is bare cloth), steel longsword, brown boots, "
    "bold dark outline, consistent face and hair in the diagonal 3/4 views, low top-down RPG view")
DC=("high-resolution pixel art adult male swordsman hero, long STRAIGHT black hair falling straight down his back, "
    "hair is sleek and straight, only the very ends slightly wavy (NOT big wavy hair, no curls), dark-brown eyes, "
    "black long high-collared coat with gold trim, black cape with red lining, "
    "a single gold pauldron on the character's LEFT shoulder only (appears on screen-right in the south view; "
    "in east-facing views it is on the far shoulder and mostly hidden; the right shoulder has no armor), "
    "holding a steel longsword in his right hand, bold dark outlines, same palette and outline weight as the reference, "
    "low top-down RPG view")
VARIANTS={
 'v2_2x_hires':dict(ref='ref_256_2x.png',desc=DC,seed=101),
}
def dl(u,path):
    for h in ({'User-Agent':'Mozilla/5.0'},{'User-Agent':'Mozilla/5.0','Authorization':'Bearer '+KEY}):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=120) as f: open(path,'wb').write(f.read()); return
        except urllib.error.HTTPError as e: print('dl err',e.code,flush=True)
    print('DOWNLOAD FAILED',path,flush=True)
def submit(name,v):
    d=f'{O}/{name}'; os.makedirs(d,exist_ok=True)
    b64=base64.b64encode(open(f'{O}/inputs/{v["ref"]}','rb').read()).decode()
    body={'description':v['desc'],'reference_image':{'type':'base64','base64':b64,'format':'png'},
          'n_directions':8,'image_size':{'width':256,'height':256},'view':'low top-down',
          'template_id':'mannequin','name':f'pilmyeolja_hero_{name}','seed':v['seed'],'no_background':True}
    logged=dict(body); logged['reference_image']={'type':'base64','format':'png','base64':f'<{len(b64)} chars of inputs/{v["ref"]}>'}
    logged['_endpoint']='POST '+API+'/create-character-v3'
    open(f'{d}/request_params.json','w').write(scrub(logged))
    st,r=req('POST','/create-character-v3',body)
    open(f'{d}/create_response.json','w').write(scrub({'http_status':st,'body':r}))
    print(name,st,{k:r.get(k) for k in ('character_id','status','usage','background_job_id')} if isinstance(r,dict) else r,flush=True)
    return r.get('character_id') if st==200 else None
def main():
    ids={}
    for n,v in VARIANTS.items():
        cid=submit(n,v)
        if cid: ids[n]=cid
    json.dump(ids,open(f'{O}/v2_2x_hires/character_ids.json','w'),indent=2)
    pending=dict(ids); t0=time.time()
    while pending and time.time()-t0<1800:
        time.sleep(10)
        for n,cid in list(pending.items()):
            st,r=req('GET',f'/characters/{cid}')
            rots=r.get('rotation_urls') or r.get('rotations') or {}
            status=r.get('status') or r.get('state')
            print(f'{int(time.time()-t0)}s',n,st,status,len(rots) if hasattr(rots,'__len__') else rots,flush=True)
            if st==200 and ( (isinstance(rots,dict) and len(rots)>=8 and all(rots.values())) or status in ('completed','failed') ):
                open(f'{O}/{n}/character_response.json','w').write(scrub({'http_status':st,'body':r}))
                if isinstance(rots,dict):
                    for dirn,url in rots.items():
                        if url:
                            u=url if isinstance(url,str) else url.get('url')
                            dl(u,f'{O}/{n}/{dirn}.png')
                del pending[n]
            elif st not in (200,423,404,202):
                print('unexpected',scrub(r)[:500])
    print('remaining pending',pending)
if __name__=='__main__': main()
