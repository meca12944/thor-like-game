# PixelLab /v2/edit-images-v2 edit_with_text on one 256px image (front/back start views, key poses). usage: edit.py src.png out.png seed "description"
# (key from env, never printed)
import os,sys,json,base64,urllib.request,time
KEY=os.environ['PIXELLAB_API_KEY'];H={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'}
def call(url,body=None):
    r=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,method='POST' if body else 'GET',headers=H)
    with urllib.request.urlopen(r,timeout=300) as f:return json.loads(f.read())
src,out,seed,desc=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]
b={'method':'edit_with_text','edit_images':[{'image':{'type':'base64','base64':base64.b64encode(open(src,'rb').read()).decode(),'format':'png'},'width':256,'height':256}],
   'image_size':{'width':256,'height':256},'description':desc,'seed':seed,'no_background':True}
for t in range(4):
    try:j=call('https://api.pixellab.ai/v2/edit-images-v2',b);break
    except Exception as e:print('retry',type(e).__name__,getattr(e,'read',lambda:b'')()[:300]);time.sleep(15)
jid=j.get('background_job_id') or j['background_job_ids'][0]
while True:
    time.sleep(6)
    try:s=call('https://api.pixellab.ai/v2/background-jobs/'+jid)
    except Exception as e:print('poll',type(e).__name__);continue
    if s.get('status') in ('completed','failed'):break
lr=s.get('last_response') or {};print(out,'status',s.get('status'),'usage',lr.get('usage') or s.get('usage'))
ims=lr.get('images') or []
if ims:open(out,'wb').write(base64.b64decode(ims[0]['base64'].split(',')[-1]))
else:print(json.dumps(lr)[:600])
