#!/usr/bin/env python3
"""botw chain_v1 (owner 2026-10-19 09:26 KST): PixelLab v3 interpolation transitions (custom_start_frame -> end_frame) between BotW basic hits.
usage: run_botw_chain.py <tag> <name>:<dir>:<start.png>:<end.png>[:seed] ...  (paths relative to botw_basic_v1/)
Output: chain_v1/_cand/<tag>/<name>_<dir>_s<seed>/ (seed in path, never overwritten). Budget cap 150 from chain_v1/_raw/job_*.json. Key from env only; never printed."""
import os, sys, json, time, glob, base64, threading, urllib.request, urllib.error
B='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/botw_basic_v1'; C=B+'/chain_v1'; RAW=C+'/_raw'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
CAP=150; FC=int(os.environ.get('FC','4'))
def scrub(o): return json.dumps(o,indent=1,ensure_ascii=False).replace(KEY,'<REDACTED>')
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
def spent():
    s=0
    for f in glob.glob(RAW+'/job_*.json'):
        try: s+=(json.load(open(f)).get('usage') or {}).get('generations') or 0
        except Exception: pass
    return s
FACE={'south':"Front view facing the camera.",'east':"Pure side view facing RIGHT in profile, never turning toward the camera.",
      'north':"Back view facing away from the camera, face never shown, sword visible beside the body."}
DESC={'trans':("A fast, fluid sword combo transition: the swordsman flows directly from the end pose of the previous slash into the windup pose of the next attack, "
               "the sword arm swinging the blade back into position in one smooth motion, feet planted, weight low, no pause and no return to the idle stance. "),
      'intro':("A fast sword attack start: from the relaxed idle stance with the sword held upright, quickly draw the sword out into the windup pose of a horizontal slash, "
               "one smooth motion, feet planted. ")}
COMMON=(" Same character: long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron, same face and same size. One-handed longsword in the right hand. "
        "No slash trail, no effects.")
def b64(p): return {'type':'base64','base64':base64.b64encode(open(B+'/'+p,'rb').read()).decode(),'format':'png'}
def log(*a):
    s=f'[{time.strftime("%H:%M:%S")}] '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
def gen(tag,name,d,sp,ep,seed):
    an=f'botwchain_{tag}_{name}_{d}_s{seed}'
    kind='intro' if name.startswith('intro') else 'trans'
    body={'character_id':CID,'mode':'v3','action_description':DESC[kind]+FACE[d]+COMMON,'frame_count':FC,'directions':[d],
          'animation_name':an,'keep_first_frame':False,'seed':seed,'custom_start_frame':b64(sp),'end_frame':b64(ep)}
    st,r=req('POST','/characters/animations',body)
    body['custom_start_frame']=sp; body['end_frame']=ep
    open(f'{RAW}/submit_{an}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
    if st!=200: log('SUBMIT FAIL',an,st,scrub(r)[:400]); return
    j=r['background_job_ids'][0]; log('submitted',an)
    while True:
        time.sleep(8); st,r=req('GET',f'/background-jobs/{j}')
        if r.get('status') in ('completed','failed'): break
    open(f'{RAW}/job_{an}.json','w').write(scrub(r))
    if r['status']!='completed': log('JOB FAIL',an,scrub(r)[:300]); return
    out=f'{C}/_cand/{tag}/{name}_{d}_s{seed}'; os.makedirs(out,exist_ok=True)
    for i,u in enumerate(r['last_response']['storage_urls']['frames']):
        open(f'{out}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
    log('done',an,r.get('usage'),'frames',len(r['last_response']['storage_urls']['frames']))
tag=sys.argv[1]; jobs=[]
for a in sys.argv[2:]:
    p=a.split(':'); jobs.append((p[0],p[1],p[2],p[3],int(p[4]) if len(p)>4 else 8800))
s0=spent(); est=len(jobs)*FC
log(f'tag={tag} jobs={len(jobs)} est~{est} spent_so_far={s0} cap={CAP}')
if s0+est>CAP: log('BUDGET STOP'); sys.exit(2)
ts=[threading.Thread(target=gen,args=(tag,)+j) for j in jobs]
for t in ts: t.start(); time.sleep(1.5)
for t in ts: t.join()
log('spent total from job records:',spent())
