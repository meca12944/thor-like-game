# Tiny PixelLab helper for the Linette thrust pilot. Key from env only; responses are scrubbed before saving.
import os,sys,json,time,urllib.request,urllib.error,base64
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; C=os.path.dirname(os.path.abspath(__file__)); RAW=C+'/_raw'; os.makedirs(RAW,exist_ok=True)
def scrub(o): return json.dumps(o,indent=1,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for a in range(25):
        try:
            with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
        except urllib.error.HTTPError as e:
            b2=e.read()
            if e.code in (429,500,502,503,504) and a<24: time.sleep(20); continue
            try: return e.code,json.loads(b2)
            except Exception: return e.code,{'raw':b2.decode(errors='replace')[:2000]}
        except Exception as e:
            if a<12: time.sleep(5); continue
            return 0,{'err':str(e)}
def wait(jid,name):
    while True:
        time.sleep(8); st,r=req('GET',f'/background-jobs/{jid}')
        if r.get('status') in ('completed','failed','error'): break
    open(f'{RAW}/job_{name}.json','w').write(scrub(r)); return r
def dl(url,path):
    for a in range(6):
        try: open(path,'wb').write(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read()); return
        except Exception: time.sleep(5)
def b64(path): return {'type':'base64','base64':base64.b64encode(open(path,'rb').read()).decode(),'format':'png'}
def log(*a):
    s=f'[{time.strftime("%F %T")}] '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
