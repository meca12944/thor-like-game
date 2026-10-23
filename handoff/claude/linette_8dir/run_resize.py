# Scale Linette 8-dir to hero size (117px -> 124px) with PixelLab /resize, one call per direction (~1 gen each). Key from env only.
import os,sys,json,time,base64,io,subprocess
from PIL import Image
K=os.environ['PIXELLAB_API_KEY']; D=os.path.dirname(os.path.abspath(__file__)); CAP=20
BOX=(82,64,174,200)            # common crop for all dirs (92x136) so every direction gets the same scale
SC=124/117; TW,TH=round(92*SC),round(136*SC)
dirs=sys.argv[1:] or ['south','south-west','west','north-west','north','north-east','east','south-east']
out=os.path.join(D,'resize_v1'); os.makedirs(out,exist_ok=True)
log=open(os.path.join(D,'run.log'),'a')
def L(*a): s=' '.join(map(str,a)); print(s); log.write(time.strftime('%F %T ')+s+'\n'); log.flush()
def call(m,p,body=None):
    args=['curl','-sS','--retry','4','--retry-all-errors','-X',m,'-H','Authorization: Bearer '+K,'-H','Content-Type: application/json',f'https://api.pixellab.ai/v2{p}']
    r=subprocess.run(args+(['--data-binary','@-'] if body else []),input=json.dumps(body) if body else None,capture_output=True,text=True)
    return json.loads(r.stdout)
desc=("Linette, adult woman, pale blonde ponytail with blue ribbon, red bikini top, red pleated mini skirt, brown belt with purple pouch, "
      "brown gloves, brown thigh-high boots with silver knee guards, a long thin needle in each hand. Keep the exact design, colors and pose.")
spent=0
for d in dirs:
    src=Image.open(os.path.join(D,'out_s1',f'{d}.png')).convert('RGBA').crop(BOX)
    b=io.BytesIO(); src.save(b,'PNG')
    body={'description':desc,'reference_image':{'type':'base64','base64':base64.b64encode(b.getvalue()).decode(),'format':'png'},
          'reference_image_size':{'width':src.width,'height':src.height},'target_size':{'width':TW,'height':TH},
          'view':'low top-down','direction':d,'no_background':True,'seed':1}
    r=call('POST','/resize',body)
    if 'background_job_id' in r:
        jid=r['background_job_id']
        while True:
            time.sleep(5); j=call('GET',f'/background-jobs/{jid}')
            if j.get('status') in('completed','failed','error'): break
        r=j.get('last_response') or {}; use=j.get('usage')
    else: use=r.get('usage')
    im=(r.get('image') or (r.get('images') or [None])[0])
    g=(use or {}).get('generations',0) if isinstance(use,dict) else 0; spent+=g
    L('resize',d,f'{src.size}->{TW}x{TH}','usage',json.dumps(use),'keys',[k for k in r.keys() if k not in('image','images')])
    if im: open(os.path.join(out,f'{d}.png'),'wb').write(base64.b64decode(im['base64']))
    if spent>CAP: L('cap reached'); break
L('resize spent',spent,'cap',CAP)
