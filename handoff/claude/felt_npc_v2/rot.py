# 8-direction rotation of a hero-proportion NPC (ref_<name>.png) via create-character-v3 reference mode (~8). Key from env only.
import os,sys,json,subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from pl import *
n=sys.argv[1];seed=int(sys.argv[2]) if len(sys.argv)>2 else 1;desc=open(f'{C}/../felt_npc_v1/desc_{n}.txt').read().strip()
body={'description':desc+' Same character, same colors and same proportions (big head, short body, about 3 heads tall) as the reference in every direction. No effects.',
      'reference_image':b64(f'{C}/ref_{n}.png'),'n_directions':8,'view':'low top-down','seed':seed,'no_background':True}
st,r=req('POST','/create-character-v3',body)
if st not in (200,202): print('FAIL',st,scrub(r)[:300]);sys.exit(1)
json.dump({'name':n,'character_id':r.get('character_id')},open(f'{C}/char_{n}.json','w'))
subprocess.run([sys.executable,f'{C}/fetch_job.py',r['background_job_id'],f'{C}/rot_{n}'])
