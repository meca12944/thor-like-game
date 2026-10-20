# usage: anim.py <name> <dir> <frames> <end_frame.png|-> "<action>" [seed]
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from pl import *
CID=os.environ.get('CID','fb140a07-3f50-40a1-9a11-ca71de7b3c49')   # hero
seed_s=sys.argv[6] if len(sys.argv)>6 else '11'
name,d,fc,end,act=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4],sys.argv[5]; seed=int(sys.argv[6]) if len(sys.argv)>6 else 11
body={'character_id':CID,'mode':'v3','action_description':act,'frame_count':fc,'directions':[d],'animation_name':name,'keep_first_frame':True,'seed':seed}
if end!='-': body['end_frame']=b64(end)
st,r=req('POST','/characters/animations',body)
open(f'{RAW}/submit_{name}_{d}_s{seed_s}.json','w').write(scrub({'http':st,'body':r,'request':{k:v for k,v in body.items() if k!='end_frame'}}))
if st!=200: log('SUBMIT FAIL',name,st,scrub(r)[:400]); sys.exit(1)
j=wait(r['background_job_ids'][0],f'{name}_{d}_s{seed_s}')
log('anim',name,d,j.get('status'),'usage',j.get('usage'))
out=f'{C}/{name}/{d}_s{seed_s}'; os.makedirs(out,exist_ok=True)
for i,u in enumerate(j['last_response']['storage_urls']['frames']): dl(u,f'{out}/{i:03d}.png')
