# PixelLab helper (key from env, never printed). edit(src,out,desc,seed) = edit-images-v2 edit_with_text; anim(first,last,outdir,n,action,seed) = animate-with-text-v3
import os,json,base64,time,urllib.request,sys
KEY=os.environ['PIXELLAB_API_KEY'];API='https://api.pixellab.ai/v2';D=os.path.dirname(os.path.abspath(__file__))
def call(path,body=None):
    r=urllib.request.Request(API+path,data=json.dumps(body).encode() if body else None,method='POST' if body else 'GET',headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=300) as f:return json.loads(f.read())
b64=lambda p:base64.b64encode(open(p,'rb').read()).decode()
def run(path,body,tag):
    for t in range(4):
        try:j=call(path,body);break
        except Exception as e:print(tag,'retry',getattr(e,'code',''),(getattr(e,'read',lambda:b'')()[:200]),flush=True);time.sleep(15)
    jid=j.get('background_job_id') or (j.get('background_job_ids') or [None])[0]
    while True:
        time.sleep(6)
        try:s=call('/background-jobs/'+jid)
        except Exception:continue
        if s.get('status') in('completed','failed'):break
    lr=s.get('last_response') or {};u=lr.get('usage') or s.get('usage')
    open(D+'/usage.log','a').write(json.dumps({'tag':tag,'status':s.get('status'),'usage':u})+'\n');print(tag,s.get('status'),'usage',u,flush=True)
    return [base64.b64decode((im.get('base64') if isinstance(im,dict) else im).split(',')[-1]) for im in (lr.get('images') or [])]
def edit(src,out,desc,seed=5):
    ims=run('/edit-images-v2',{'method':'edit_with_text','edit_images':[{'image':{'type':'base64','base64':b64(src),'format':'png'},'width':256,'height':256}],'image_size':{'width':256,'height':256},'description':desc,'seed':seed,'no_background':True},'edit_'+os.path.basename(out))
    if ims:open(out,'wb').write(ims[0])
def anim(first,last,outdir,n,action,seed=7):
    img=lambda p:{'type':'base64','base64':b64(p),'format':'png'}
    ims=run('/animate-with-text-v3',{'first_frame':img(first),'last_frame':img(last),'action':action,'frame_count':n,'seed':seed,'no_background':True},'anim_'+os.path.basename(outdir))
    os.makedirs(outdir,exist_ok=True)
    for i,b in enumerate(ims):open(f'{outdir}/{i:03d}.png','wb').write(b)
if __name__=='__main__':
    if sys.argv[1]=='edit':edit(sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]) if len(sys.argv)>5 else 5)
    else:anim(sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]),sys.argv[6],int(sys.argv[7]) if len(sys.argv)>7 else 7)
