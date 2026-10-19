#!/usr/bin/env python3
"""trail_front_v1 (owner 2026-10-19 11:28 KST): PixelLab /edit-animation-v2 on existing combo3_final frames so the slash trail is only in FRONT.
usage: run_trail_front.py <tag> <job_name> <dir> <seed> <hit:frame>...   (2-4 frames, 256px)
Output: trail_front_v1/_cand/<tag>/<job_name>_s<seed>/hit<h>_<frame>.png (seed in path). Budget cap 300 from trail_front_v1/_raw/job_*.json. Key from env only."""
import os,sys,json,time,glob,base64,urllib.request,urllib.error
G='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=G+'/trail_front_v1'; RAW=C+os.environ.get('RAWDIR','/_raw'); os.makedirs(RAW,exist_ok=True); SRC=os.environ.get('SRCDIR',G+'/combo3_final')
KEY=os.environ['PIXELLAB_API_KEY']; API='https://api.pixellab.ai/v2'; CAP=int(os.environ.get('CAP','300')); EST=25
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
KEEP=" Keep the character, his body, face, hair, cape, outfit, pose, the sword and all colors exactly the same; only the slash trail changes."
DESC={'east':("Edit only the white slash trail (sword smear): erase every part of the white trail that is behind the character's back, on the LEFT side of his body and behind him. "
              "The trail must appear only IN FRONT of him, on the RIGHT side, in the direction he is facing and attacking."+KEEP),
      'east2':("Edit only the white slash trail (sword smear). The trail must START at the front of his chest and extend only to the RIGHT, out in front of him toward the sword tip. "
               "Erase all of the white trail that is on the LEFT half of the image, over his back, over his hair, over his cape or behind his body; no white streaks or sparkles on his left side."+KEEP),
      'northback':("Turn the character into a TRUE BACK VIEW: we see him from behind, the back of his head and his long black hair, his back and his cape; NO face, no eyes, no chest, no front of the coat. "
               "He is attacking UP the screen, away from the camera. Keep the same pose, the same stance and feet position, the same size, the same sword position and angle in each frame. "
               "The slash trail (sword smear) is only in FRONT of him: up the screen, beyond his head and shoulders at the far end of the sword; erase any trail that crosses over his body, his waist or his legs, "
               "or that is below his shoulders. Same character design: long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron."),
      'northtrail':("Back view of the swordsman attacking up the screen. Edit ONLY the golden-white slash trail: it must be ABOVE his head, higher than the top of his hair, up the screen in front of him, "
               "a thin arc at the far tip of the sword. Erase any trail pixels that overlap his hair, head, shoulders, cape, body or legs, and any trail lower than his head. "
               "Keep the character, back view, pose, sword and colors exactly the same."),
      'north':("Edit only the white/golden slash trail (sword smear): erase every part of the trail that lies over or across the character's body and below his waist. "
               "Keep the trail only at the far end of the sword, out in front of the attack, never across his body."+KEEP),
      'south':("Edit only the white/golden slash trail (sword smear): erase every part of the trail that is behind the character's back. "
               "The trail appears only in front of him, on the side of the sword tip, in the direction of the attack."+KEEP)}
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
