# PixelLab /v2/generate-image-v2 with a subject reference image (new view of an existing mob). usage: genref.py ref.png out.png W H seed "description"
import os,sys,json,base64,urllib.request,time
KEY=os.environ['PIXELLAB_API_KEY'];H={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'}
def call(url,body=None):
    r=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,method='POST' if body else 'GET',headers=H)
    with urllib.request.urlopen(r,timeout=300) as f:return json.loads(f.read())
ref,out,w,h,seed,desc=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
img={'type':'base64','base64':base64.b64encode(open(ref,'rb').read()).decode(),'format':'png'}
NOREF=os.environ.get('NOREF')=='1'
b={'description':desc,'image_size':{'width':w,'height':h},'seed':seed,'no_background':True,
   'reference_images':[{'image':img,'size':{'width':256,'height':256},'usage_description':'the same creature: copy its design, materials and colors exactly'}],
   'style_image':{'image':img,'size':{'width':256,'height':256}}}
if NOREF:del b['reference_images']   # style only: a new view the reference would pull back to its own pose
j=call('https://api.pixellab.ai/v2/generate-image-v2',b);jid=j['background_job_id']
while True:
    time.sleep(8)
    try:s=call('https://api.pixellab.ai/v2/background-jobs/'+jid)
    except Exception as e:print('poll',type(e).__name__);continue
    if s.get('status') in ('completed','failed'):break
lr=s.get('last_response') or {};print(out,'status',s.get('status'),'usage',lr.get('usage') or s.get('usage'))
ims=lr.get('images') or []
if ims:open(out,'wb').write(base64.b64decode(ims[0]['base64'].split(',')[-1]))
else:print(json.dumps(lr)[:600])
