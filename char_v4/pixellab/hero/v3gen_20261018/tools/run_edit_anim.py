#!/usr/bin/env python3
"""PixelLab /v2/edit-animation-v2 on existing frames (owner 23:52: fixes via PixelLab EDIT only).
usage: run_edit_anim.py <job_name> <out_dir> <description> <frame.png> x2-4 . Key from env only; never printed. Logs usage+balance to edit_v1/run.log"""
import os,sys,json,time,base64,urllib.request,urllib.error
E=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/edit_v1'; KEY=os.environ['PIXELLAB_API_KEY']; API='https://api.pixellab.ai/v2'
name,out,desc,fr=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4:]
def scrub(o): return json.dumps(o,indent=1,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for a in range(20):
        try:
            with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
        except urllib.error.HTTPError as e:
            b2=e.read()
            if e.code in (429,500,502,503,504) and a<19: time.sleep(20); continue
            try: return e.code,json.loads(b2)
            except Exception: return e.code,{'raw':b2.decode(errors='replace')[:1500]}
        except Exception as e:
            if a<5: time.sleep(5); continue
            return 0,{'err':str(e)}
def log(*a):
    s=time.strftime('%H:%M:%S')+' '+name+' '+' '.join(map(str,a)); print(s,flush=True); open(E+'/run.log','a').write(s+'\n')
st,b=req('GET','/balance'); log('balance before',b.get('subscription',{}).get('generations'))
body={'description':desc,'frames':[{'image':{'type':'base64','base64':base64.b64encode(open(p,'rb').read()).decode(),'format':'png'},'size':{'width':256,'height':256}} for p in fr],
      'image_size':{'width':256,'height':256},'no_background':True,'seed':int(os.environ.get('SEED','77'))}
st,r=req('POST','/edit-animation-v2',body)
open(f'{E}/_raw/submit_{name}.json','w').write(scrub({'desc':desc,'frames':fr,'status':st,'resp':r}))
if st not in (200,202): log('SUBMIT FAIL',st,scrub(r)[:500]); sys.exit(1)
j=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]; log('job',j)
while True:
    time.sleep(6); st,r=req('GET',f'/background-jobs/{j}')
    if r.get('status') in ('completed','failed'): break
open(f'{E}/_raw/job_{name}.json','w').write(scrub(r)[:20000])
if r['status']!='completed': log('FAILED',scrub(r)[:400]); sys.exit(1)
lr=r['last_response']; os.makedirs(out,exist_ok=True)
imgs=lr.get('images') or lr.get('frames') or (lr.get('storage_urls') or {}).get('frames') or []
for i,im in enumerate(imgs):
    p=f'{out}/{i:03d}.png'
    if isinstance(im,str) and im.startswith('http'): data=urllib.request.urlopen(urllib.request.Request(im,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read()
    elif isinstance(im,dict) and 'base64' in im: data=base64.b64decode(im['base64'].split(',')[-1])
    elif isinstance(im,dict) and 'url' in im: data=urllib.request.urlopen(urllib.request.Request(im['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read()
    else: log('unknown image fmt',str(type(im)),str(im)[:200]); continue
    open(p,'wb').write(data)
st,b=req('GET','/balance'); log('done',len(imgs),'frames usage',r.get('usage'),'keys',list(lr.keys()),'balance after',b.get('subscription',{}).get('generations'))
