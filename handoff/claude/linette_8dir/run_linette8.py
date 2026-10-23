# Linette 8-direction rotation from the 117px original mini (south). create-character-v3, reference mode, 8 dirs (~8 gen).
# Key comes ONLY from env PIXELLAB_API_KEY; never printed or logged.
import os,sys,json,time,base64,urllib.request
K=os.environ.get('PIXELLAB_API_KEY') or sys.exit('PIXELLAB_API_KEY missing')
API='https://api.pixellab.ai/v2'; D=os.path.dirname(os.path.abspath(__file__)); CAP=40
def req(m,p,body=None):
    r=urllib.request.Request(API+p,method=m,data=json.dumps(body).encode() if body else None,
        headers={'Authorization':'Bearer '+K,'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(r,timeout=120) as f: return json.load(f)
log=open(os.path.join(D,'run.log'),'a')
def L(*a): s=' '.join(str(x) for x in a); print(s); log.write(time.strftime('%F %T ')+s+'\n'); log.flush()
seed=int(sys.argv[1]) if len(sys.argv)>1 else 1
desc=("Linette, petite cheerful adult woman (22), pale blonde long ponytail with a blue ribbon, red bikini top, red pleated mini skirt, "
      "brown leather belt with a purple pouch, brown elbow gloves, brown thigh-high boots with silver knee guards, a long thin sewing needle "
      "held in each hand like rapiers. Same character, same colors and same proportions as the reference in every direction.")
ref=base64.b64encode(open(os.path.join(D,'south_ref_256.png'),'rb').read()).decode()
body={'description':desc,'reference_image':{'type':'base64','base64':ref,'format':'png'},'n_directions':8,'view':'low top-down','seed':seed,'no_background':True}
L('request create-character-v3 n_directions=8 seed',seed,'cap',CAP)
r=req('POST','/create-character-v3',body); jid=r.get('background_job_id'); cid=r.get('character_id'); L('job',jid,'character',cid)
while True:
    time.sleep(6); j=req('GET',f'/background-jobs/{jid}'); st=j.get('status')
    if st in('completed','failed','error'): break
L('status',st,'billing_usage',json.dumps(j.get('billing_usage') or j.get('usage')))
out=os.path.join(D,f'out_s{seed}'); os.makedirs(out,exist_ok=True)
json.dump({k:v for k,v in j.items() if k!='last_response'},open(os.path.join(out,'job.json'),'w'),indent=1)
imgs=(j.get('last_response') or {}).get('images') or []
for i,im in enumerate(imgs):
    nm=im.get('direction') or str(i); open(os.path.join(out,f'{nm}.png'),'wb').write(base64.b64decode(im['base64']))
L('saved',len(imgs),'images to',out)
