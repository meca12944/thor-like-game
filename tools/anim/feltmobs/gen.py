# PixelLab /v2/generate-image-v2: one image with idle (left) + attack (right) pose, styled on an existing mob sheet cell.
# usage: gen.py style.png out.png W H "description"   (key from env, never printed)
import os,sys,json,base64,urllib.request,time
KEY=os.environ['PIXELLAB_API_KEY']; H={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'}
def call(url,body=None):
    r=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,method='POST' if body else 'GET',headers=H)
    with urllib.request.urlopen(r,timeout=300) as f: return json.loads(f.read())
sty,out,w,h,desc=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
from PIL import Image
sw,sh=Image.open(sty).size
b={'description':desc,'image_size':{'width':w,'height':h},'no_background':True,
   'style_image':{'image':{'type':'base64','base64':base64.b64encode(open(sty,'rb').read()).decode(),'format':'png'},'size':{'width':sw,'height':sh}}}
j=call('https://api.pixellab.ai/v2/generate-image-v2',b); jid=j.get('background_job_id')
while True:
    time.sleep(8); s=call('https://api.pixellab.ai/v2/background-jobs/'+jid)
    if s.get('status') in ('completed','failed'): break
lr=s.get('last_response') or {}
print('status',s.get('status'),'usage',lr.get('usage') or s.get('usage'))
ims=lr.get('images') or []
for i,im in enumerate(ims):
    data=im.get('base64') if isinstance(im,dict) else im
    p=out if len(ims)==1 else out.replace('.png',f'_{i}.png'); open(p,'wb').write(base64.b64decode(data.split(',')[-1])); print('saved',p)
if not ims: print(json.dumps(lr)[:800])
