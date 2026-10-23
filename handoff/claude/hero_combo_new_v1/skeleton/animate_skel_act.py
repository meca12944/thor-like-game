# PixelLab /v2/animate-with-skeleton-v3: idle frame + its estimated skeleton + per-frame skeletons -> frames. usage: animate_skel.py <first.png> <first_kp.json> <frames_kp.json> <direction> <outdir> <seed>
import os,sys,json,time,base64,urllib.request,urllib.error
KEY=os.environ['PIXELLAB_API_KEY'];API='https://api.pixellab.ai/v2'
first,fkp,kp,dr,out,seed=sys.argv[1:7]
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for a in range(20):
        try:
            with urllib.request.urlopen(r,timeout=120) as f:return f.status,json.loads(f.read() or b'{}')
        except urllib.error.HTTPError as e:
            b2=e.read()
            if e.code in (429,500,502,503,504) and a<19:time.sleep(20);continue
            return e.code,{'raw':b2.decode(errors='replace')[:800]}
        except Exception as e:
            if a<5:time.sleep(5);continue
            return 0,{'err':str(e)}
F=json.load(open(fkp));F=F['keypoints'] if isinstance(F,dict) else F
F=[{k:v for k,v in p.items() if k in('x','y','label','z_index')} for p in F]
for p in F:p['z_index']=int(p.get('z_index',0))
body={'description':'young swordsman with long straight black hair, dark navy coat with gold trim, cape with red lining, gold pauldron on one shoulder, longsword held in the right hand, same sword size every frame',
      'action':os.environ.get('ACTION','attack'),'direction':dr,'view':'low top-down','first_frame':{'type':'base64','base64':base64.b64encode(open(first,'rb').read()).decode(),'format':'png'},
      'first_frame_keypoints':F,'keypoints':json.load(open(kp)),'template_id':'mannequin','seed':int(seed),'no_background':True}
st,r=req('POST','/animate-with-skeleton-v3',body)
if st not in (200,202):print('SUBMIT FAIL',st,json.dumps(r)[:600].replace(KEY,'<K>'));sys.exit(1)
j=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0];print('job submitted',flush=True)
while True:
    time.sleep(10);st,r=req('GET',f'/background-jobs/{j}')
    if r.get('status') in ('completed','failed'):break
if r['status']!='completed':print('FAILED',json.dumps(r)[:500]);sys.exit(1)
imgs=r['last_response'].get('images') or [];os.makedirs(out,exist_ok=True)
for i,im in enumerate(imgs):open(f'{out}/{i:03d}.png','wb').write(base64.b64decode(im['base64'].split(',')[-1]) if isinstance(im,dict) else urllib.request.urlopen(urllib.request.Request(im,headers={'User-Agent':'Mozilla/5.0'})).read())
print('done',len(imgs),r.get('usage'))
