# usage: make_state.py <name> "<edit description>" [seed]   -> states/<name>/<dir>.png
import sys,json,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from pl import *
CID='7e26e0f3-b375-4384-b955-3304cacebff3'
name,desc=sys.argv[1],sys.argv[2]; seed=int(sys.argv[3]) if len(sys.argv)>3 else 7
st,r=req('POST','/create-character-state',{'character_id':CID,'edit_description':desc,'seed':seed,'state_name':name,'use_color_palette_from_reference':True})
open(f'{RAW}/submit_state_{name}.json','w').write(scrub({'http':st,'body':r}))
log('state submit',name,st,{k:v for k,v in r.items() if 'image' not in k})
jid=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]
j=wait(jid,'state_'+name); lr=j.get('last_response') or {}
log('state',name,j.get('status'),'usage',j.get('usage'),'keys',list(lr.keys()),'cid',lr.get('character_id'))
out=f'{C}/states/{name}'; os.makedirs(out,exist_ok=True)
su=lr.get('storage_urls') or {}
for d,u in (su.items() if isinstance(su,dict) else []):
    if isinstance(u,str): dl(u,f'{out}/{d}.png')
json.dump({'character_id':lr.get('character_id'),'desc':desc,'seed':seed},open(f'{out}/info.json','w'),indent=1)
