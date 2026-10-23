# Map-method proof: tiles at the hero's pixel density (64 px, 1 art px = 1 screen point like the 124 px hero).
#  1) /create-tileset mode=pro 64px: worn stone floor <-> dark grass (Wang 16)  2) /create-tiles-pro building kit 64px: stone walls/floor/door
# usage: gen_arena.py <out dir> [tileset|kit]
import os,sys,json,base64
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','anim','thrust'))
out=sys.argv[1];what=sys.argv[2:] or ['tileset','kit'];os.environ['OUT']=out
from pl import req,wait,log,scrub,RAW
os.makedirs(out,exist_ok=True)
def dump_imgs(j,name):
    n=0
    def walk(o,path):
        nonlocal n
        if isinstance(o,dict):
            b=o.get('base64')
            if isinstance(b,str) and len(b)>100:
                open(f'{out}/{name}_{n:02d}.png','wb').write(base64.b64decode(b.split(',')[-1]));n+=1;return
            for k,v in o.items():walk(v,path+'.'+k)
        elif isinstance(o,list):
            for v in o:walk(v,path)
    walk(j.get('last_response') or {},'');return n
J=[]
if 'tileset' in what:
    body={'mode':'pro','lower_description':'dark trampled grass','upper_description':'worn cracked grey flagstone floor of a ruined plaza','tile_size':{'width':64,'height':64},'view':'high top-down','transition_size':0.25}
    st,r=req('POST','/create-tileset',body);open(f'{RAW}/submit_tileset64.json','w').write(scrub({'http':st,'body':r}))
    if st in(200,202):J.append(('tileset64',r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]))
    else:log('FAIL tileset',st,scrub(r)[:600])
if 'kit' in what:
    body={'description':'ruined stone dungeon room','tile_type':'square_topdown','tile_size':64,'tile_view':'high top-down','tile_feature':'building',
          'building_wall_description':'dark weathered stone brick walls with moss','building_floor_description':'cracked grey flagstone floor','building_wall_tiles':2}
    st,r=req('POST','/create-tiles-pro',body);open(f'{RAW}/submit_kit64.json','w').write(scrub({'http':st,'body':r}))
    if st in(200,202):J.append(('kit64',r.get('background_job_id') or (r.get('background_job_ids') or [None])[0] or r.get('tile_id')))
    else:log('FAIL kit',st,scrub(r)[:600])
for name,jid in J:
    j=wait(jid,name);open(f'{out}/{name}_job.json','w').write(scrub(j));n=dump_imgs(j,name);log(name,j.get('status'),'images',n,'usage',j.get('usage'),(j.get('last_response') or {}).get('billing_usage'))
