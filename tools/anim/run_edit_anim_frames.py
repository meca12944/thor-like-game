# PixelLab /v2/edit-animation-v2 on 2-4 given 256px frames. usage: edit_anim.py <name> <seed> <outdir> <desc_file> frame.png... Key from env only, never printed.
import os,sys,json,time,base64,urllib.request,urllib.error
KEY=os.environ['PIXELLAB_API_KEY'];API='https://api.pixellab.ai/v2'
name,seed,out,descf=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4];fr=sys.argv[5:]
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
body={'description':open(descf).read(),'frames':[{'image':{'type':'base64','base64':base64.b64encode(open(p,'rb').read()).decode(),'format':'png'},'size':{'width':256,'height':256}} for p in fr],
      'image_size':{'width':256,'height':256},'no_background':True,'seed':seed}
st,r=req('POST','/edit-animation-v2',body)
if st not in (200,202):print(name,'SUBMIT FAIL',st,json.dumps(r)[:300].replace(KEY,'<K>'));sys.exit(1)
j=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]
while True:
    time.sleep(8);st,r=req('GET',f'/background-jobs/{j}')
    if r.get('status') in ('completed','failed'):break
if r['status']!='completed':print(name,'FAILED',json.dumps(r)[:300]);sys.exit(1)
lr=r['last_response'];imgs=lr.get('images') or lr.get('frames') or []
os.makedirs(out,exist_ok=True)
for p,im in zip(fr,imgs):
    data=base64.b64decode(im['base64'].split(',')[-1]) if isinstance(im,dict) and 'base64' in im else urllib.request.urlopen(urllib.request.Request(im if isinstance(im,str) else im['url'],headers={'User-Agent':'Mozilla/5.0'})).read()
    open(f'{out}/{os.path.basename(p)}','wb').write(data)
print(name,'done',len(imgs),r.get('usage'))
