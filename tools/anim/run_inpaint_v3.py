# PixelLab /v2/inpaint-v3: redraw only the white mask area (ring around the pasted idle face) to blend it in. usage: inpaint.py in.png mask.png out.png seed. Key from env, never printed.
import os,sys,json,time,base64,urllib.request,urllib.error
KEY=os.environ['PIXELLAB_API_KEY'];API='https://api.pixellab.ai/v2'
inp,mask,out,seed=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for a in range(20):
        try:
            with urllib.request.urlopen(r,timeout=120) as f:return f.status,json.loads(f.read() or b'{}')
        except urllib.error.HTTPError as e:
            b2=e.read()
            if e.code in (429,500,502,503,504) and a<19:time.sleep(15);continue
            return e.code,{'raw':b2.decode(errors='replace')[:800]}
        except Exception as e:
            if a<5:time.sleep(5);continue
            return 0,{'err':str(e)}
img=lambda p:{'image':{'type':'base64','base64':base64.b64encode(open(p,'rb').read()).decode(),'format':'png'},'size':{'width':256,'height':256}}
desc=("Blend seamlessly: the long straight black hair around the face, the neck and the collar of the dark coat with gold trim, matching the surrounding pixel art exactly. "
      "Same character, same colors, clean pixels, no new objects.")
st,r=req('POST','/inpaint-v3',{'description':desc,'inpainting_image':img(inp),'mask_image':img(mask),'no_background':True,'seed':seed})
if st not in (200,202):print('SUBMIT FAIL',st,json.dumps(r)[:400].replace(KEY,'<K>'));sys.exit(1)
j=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]
if not j and r.get('image'):open(out,'wb').write(base64.b64decode(r['image']['base64'].split(',')[-1]));print('done sync',r.get('usage'));sys.exit()
while True:
    time.sleep(6);st,r=req('GET',f'/background-jobs/{j}')
    if r.get('status') in ('completed','failed'):break
if r['status']!='completed':print('FAILED',json.dumps(r)[:400]);sys.exit(1)
lr=r['last_response'];im=lr.get('image') or (lr.get('images') or [None])[0]
open(out,'wb').write(base64.b64decode(im['base64'].split(',')[-1]));print('done',out,r.get('usage'))
