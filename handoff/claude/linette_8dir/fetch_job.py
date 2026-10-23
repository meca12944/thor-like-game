# Poll a PixelLab background job until done and save its images (retries on connection resets). Key from env only.
import os,sys,json,time,base64,subprocess
K=os.environ['PIXELLAB_API_KEY']; jid=sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
D=os.path.dirname(os.path.abspath(__file__))
def get():
    r=subprocess.run(['curl','-sS','--retry','5','--retry-all-errors','-H','Authorization: Bearer '+K,f'https://api.pixellab.ai/v2/background-jobs/{jid}'],capture_output=True,text=True)
    return json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else None
while True:
    j=get()
    if j and j.get('status') in ('completed','failed','error'): break
    time.sleep(10)
lr=j.get('last_response') or {}
json.dump({k:v for k,v in j.items() if k!='last_response'}|{'last_response_keys':list(lr.keys())},open(os.path.join(out,'job.json'),'w'),indent=1)
imgs=lr.get('images') or []
for i,im in enumerate(imgs):
    nm=im.get('direction') or str(i); open(os.path.join(out,f'{nm}.png'),'wb').write(base64.b64decode(im['base64']))
for nm,url in (lr.get('storage_urls') or {}).items():   # create-character-v3 returns download URLs per direction
    subprocess.run(['curl','-sS','--retry','5','--retry-all-errors','-A','Mozilla/5.0','-o',os.path.join(out,f'{nm}.png'),url],check=True); imgs.append(nm)
with open(os.path.join(D,'run.log'),'a') as f: f.write(time.strftime('%F %T ')+f"status {j.get('status')} usage {json.dumps(j.get('usage'))} saved {len(imgs)} images to {out} keys {list(lr.keys())}\n")
print(j.get('status'),len(imgs),list(lr.keys()))
