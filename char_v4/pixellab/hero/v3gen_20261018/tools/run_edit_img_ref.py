#!/usr/bin/env python3
"""PixelLab /v2/edit-images-v2 edit_with_reference, one 256 frame per job. usage: name out_png ref_png desc in_png. Key from env, never printed."""
import os,sys,json,time,base64,urllib.request,urllib.error
E=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/edit_v1'; KEY=os.environ['PIXELLAB_API_KEY']; API='https://api.pixellab.ai/v2'
name,out,ref,desc,inp=sys.argv[1:6]
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
from PIL import Image
def b64(p): return {'type':'base64','base64':base64.b64encode(open(p,'rb').read()).decode(),'format':'png'}
rw,rh=Image.open(ref).size
body={'method':'edit_with_reference','edit_images':[{'image':b64(inp),'width':256,'height':256}],'image_size':{'width':256,'height':256},
      'reference_image':{'image':b64(ref),'width':rw,'height':rh},'description':desc,'no_background':True,'seed':int(os.environ.get('SEED','55'))}
st,r=req('POST','/edit-images-v2',body)
open(f'{E}/_raw/submit_{name}.json','w').write(scrub({'desc':desc,'in':inp,'ref':ref,'status':st,'resp':r}))
if st not in (200,202): log('SUBMIT FAIL',st,scrub(r)[:500]); sys.exit(1)
j=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]; log('job',j)
while True:
    time.sleep(6); st,r=req('GET',f'/background-jobs/{j}')
    if r.get('status') in ('completed','failed'): break
open(f'{E}/_raw/job_{name}.json','w').write(scrub(r)[:5000])
if r['status']!='completed': log('FAILED',scrub(r)[:400]); sys.exit(1)
im=(r['last_response'].get('images') or [None])[0]
os.makedirs(os.path.dirname(out),exist_ok=True); open(out,'wb').write(base64.b64decode(im['base64'].split(',')[-1]))
log('done usage',r.get('usage'))
