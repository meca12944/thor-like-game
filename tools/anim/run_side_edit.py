#!/usr/bin/env python3
"""side_v1: PixelLab /edit-animation-v2 on the in-game trail_front_v1 right (east) frames that turn toward the camera -> strict side view.
usage: run_trail_front.py <tag> <job_name> <dir> <seed> <hit:frame>...   (2-4 frames, 256px)
Output: notrail_v1/_cand/<tag>/<job_name>_s<seed>/hit<h>_<frame>.png (seed in path). Budget cap 600 from notrail_v1/_raw/job_*.json. Key from env only."""
import os,sys,json,time,glob,base64,urllib.request,urllib.error
G='/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018'; C='/tmp/claude-0/-home-user/605da03e-2542-5329-b23f-a50876f99780/scratchpad/side'; RAW=C+'/_raw'; os.makedirs(RAW,exist_ok=True); SRC=os.environ.get('SRCDIR',G+'/trail_front_v1')
KEY=os.environ['PIXELLAB_API_KEY']; API='https://api.pixellab.ai/v2'; CAP=int(os.environ.get('CAP','100')); EST=25
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
def spent():
    s=0
    for f in glob.glob(RAW+'/job_*.json'):
        try: s+=(json.load(open(f)).get('usage') or {}).get('generations') or 0
        except Exception: pass
    return s
SIDE=("STRICT SIDE VIEW in EVERY frame: the swordsman is seen in profile facing RIGHT. His chest, face and body NEVER turn toward the camera and he NEVER faces left; "
      "we always see his right side profile like the first and last frames. Keep the same arm and sword motion and the same sword positions, the same white slash trail, "
      "the same feet position on the ground line, same size. Same character: long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron, same face.")
DESC={'east':SIDE}
tag,name,d,seed=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]); fr=[tuple(map(int,a.split(':'))) for a in sys.argv[5:]]
def log(*a):
    s=time.strftime('%H:%M:%S')+f' {tag}/{name}_s{seed} '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
s0=spent()
if s0+EST>CAP: log('BUDGET STOP',s0); sys.exit(2)
paths=[f'{SRC}/hit{h}/{d}/{i:03d}.png' for h,i in fr]
DK=os.environ.get('DESC',d)
body={'description':DESC[DK],'frames':[{'image':{'type':'base64','base64':base64.b64encode(open(p,'rb').read()).decode(),'format':'png'},'size':{'width':256,'height':256}} for p in paths],
      'image_size':{'width':256,'height':256},'no_background':True,'seed':seed}
st,r=req('POST','/edit-animation-v2',body); an=f'{tag}_{name}_s{seed}'
open(f'{RAW}/submit_{an}.json','w').write(scrub({'desc':DESC[DK],'frames':paths,'status':st,'resp':r}))
if st not in (200,202): log('SUBMIT FAIL',st,scrub(r)[:500]); sys.exit(1)
j=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]; log('job submitted; spent_before',s0)
while True:
    time.sleep(8); st,r=req('GET',f'/background-jobs/{j}')
    if r.get('status') in ('completed','failed'): break
rr=dict(r); lr=rr.get('last_response') or {}
imgs=lr.get('images') or lr.get('frames') or (lr.get('storage_urls') or {}).get('frames') or []
small=dict(rr); small['last_response']={k:v for k,v in lr.items() if k not in ('images','quantized_images','frames')}
open(f'{RAW}/job_{an}.json','w').write(scrub(small))
if r['status']!='completed': log('FAILED',scrub(small)[:400]); sys.exit(1)
out=f'{C}/_cand/{tag}/{name}_s{seed}'; os.makedirs(out,exist_ok=True)
for (h,i),im in zip(fr,imgs):
    if isinstance(im,str) and im.startswith('http'): data=urllib.request.urlopen(urllib.request.Request(im,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read()
    elif isinstance(im,dict) and 'base64' in im: data=base64.b64decode(im['base64'].split(',')[-1])
    elif isinstance(im,dict) and 'url' in im: data=urllib.request.urlopen(urllib.request.Request(im['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read()
    else: log('unknown fmt',str(im)[:100]); continue
    open(f'{out}/hit{h}_{i:03d}.png','wb').write(data)
log('done frames',len(imgs),'usage',r.get('usage'),'spent_total',spent())
