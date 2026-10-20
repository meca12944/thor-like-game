# PixelLab /v2/animate-with-text-v3. usage: anim.py first.png [last.png|-] out_prefix frames "action"  (key from env, never printed)
import os,sys,json,base64,urllib.request,time
KEY=os.environ['PIXELLAB_API_KEY'];H={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'}
def call(url,body=None):
    r=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,method='POST' if body else 'GET',headers=H)
    with urllib.request.urlopen(r,timeout=300) as f:return json.loads(f.read())
first,last,out,n,act=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),sys.argv[5]
img=lambda p:{'type':'base64','base64':base64.b64encode(open(p,'rb').read()).decode(),'format':'png'}
b={'first_frame':img(first),'action':act,'frame_count':n,'no_background':True}
if last!='-':b['last_frame']=img(last)
for t in range(4):
    try:j=call('https://api.pixellab.ai/v2/animate-with-text-v3',b);break
    except Exception as e:print('retry',type(e).__name__,getattr(e,'read',lambda:b'')()[:300]);time.sleep(15)
jid=j['background_job_id']
while True:
    time.sleep(6)
    try:s=call('https://api.pixellab.ai/v2/background-jobs/'+jid)
    except Exception as e:print('poll',type(e).__name__);continue
    if s.get('status') in ('completed','failed'):break
lr=s.get('last_response') or {};print(out,'status',s.get('status'),'usage',lr.get('usage') or s.get('usage'))
ims=lr.get('images') or []
for i,im in enumerate(ims):
    data=im.get('base64') if isinstance(im,dict) else im;open(f'{out}_{i:02d}.png','wb').write(base64.b64decode(data.split(',')[-1]))
if not ims:print(json.dumps(lr)[:600])
