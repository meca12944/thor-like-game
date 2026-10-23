# Felt NPC base: create-character-v3 from text, 4 directions, 256 canvas (owner 10-23 "일단 3명 만들어 봐": 마르타, 오스왈드, 세라). Key from env only.
import os,sys,json,time,urllib.request,subprocess
K=os.environ['PIXELLAB_API_KEY'];API='https://api.pixellab.ai/v2';D=os.path.dirname(os.path.abspath(__file__))
name,seed=sys.argv[1],int(sys.argv[2]);desc=open(f'{D}/desc_{name}.txt').read().strip()
STYLE=" Full body, standing relaxed, about 120 pixels tall in a 256 canvas. Dark fantasy pixel art with muted, dusty, ashen colors (refugee slum outside a burned royal capital), detailed shading, same style as a gritty top-down action RPG. Clearly an adult. No effects."
body={'description':desc+STYLE,'view':'low top-down','seed':seed,'no_background':True,'image_size':{'width':256,'height':256}}
r=urllib.request.Request(API+'/create-character-v3',method='POST',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+K,'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
try:
    with urllib.request.urlopen(r,timeout=120) as f:j=json.load(f)
except urllib.error.HTTPError as e:print('FAIL',e.code,e.read().decode()[:400].replace(K,'X'));sys.exit(1)
print(name,'job',j.get('background_job_id'),'char',j.get('character_id'),flush=True)
json.dump({'name':name,'seed':seed,'character_id':j.get('character_id')},open(f'{D}/char_{name}_s{seed}.json','w'))
subprocess.run([sys.executable,f'{D}/fetch_job.py',j['background_job_id'],f'{D}/{name}_s{seed}'])
