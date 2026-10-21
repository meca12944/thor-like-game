# Felt village square for the sandbox, drawn with PixelLab: one top-down Wang tileset (grass <-> worn cobblestone) + map objects
# (fountain, benches, cart stall, crates/barrels, broken pillar, torch post, notice board), all with the Felt concept's colours.
# usage: gen.py <out dir> <palette.png> [only=name,...]      (key from env only; raw job json scrubbed)
import os,sys,json,base64,time
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','anim','thrust'))
out,pal=sys.argv[1:3];only=sys.argv[3].split(',') if len(sys.argv)>3 else None
os.environ['OUT']=out;from pl import req,wait,b64,log,scrub,RAW
os.makedirs(out,exist_ok=True)
def save_imgs(j,name):
    lr=j.get('last_response') or {};ims=lr.get('images') or ([lr['image']] if lr.get('image') else [])
    for i,im in enumerate(ims):
        data=im.get('base64') if isinstance(im,dict) else im
        open(f'{out}/{name}_{i}.png','wb').write(base64.b64decode(data.split(',')[-1]))
    return len(ims)
STYLE=dict(view='low top-down',outline='single color outline',shading='medium shading',detail='high detail')
OBJ={
 'fountain':('old cracked round two-tier stone fountain with clear bright blue flowing water, moss in the cracks, worn medieval village square, 16-bit JRPG pixel art',{'width':192,'height':192}),
 'bench':('worn wooden bench with iron legs, poor medieval village',{'width':96,'height':64}),
 'cart':('small merchant cart stall with red cloth roof and crates of goods, poor medieval village, no text',{'width':128,'height':128}),
 'crates':('stack of old wooden crates and two barrels',{'width':96,'height':96}),
 'pillar':('broken burnt stone pillar ruin with rubble, overgrown',{'width':80,'height':128}),
 'torch':('wooden post with a lit iron torch lantern',{'width':48,'height':112}),
 'board':('wooden notice board with blank paper notes, no text',{'width':80,'height':96}),
 'well':('old stone well with wooden roof and bucket',{'width':112,'height':128}),
}
jobs=[]
if not only or 'tileset' in only:
    body={'lower_description':'dry grass with small dirt patches','upper_description':'worn grey cobblestone village plaza with cracked stones','transition_description':'mossy stone edge',
          'tile_size':{'width':32,'height':32},'view':'low top-down','outline':'lineless','shading':'medium shading','detail':'highly detailed','transition_size':0.25}
    st,r=req('POST','/create-tileset',body);open(f'{RAW}/submit_tileset.json','w').write(scrub({'http':st,'body':r}))
    if st in(200,202):jobs.append(('tileset',r.get('background_job_id') or (r.get('background_job_ids') or [None])[0],r))
    else:log('TILESET FAIL',st,scrub(r)[:400])
for k,(desc,size) in OBJ.items():
    if only and k not in only:continue
    body=dict(description=desc,image_size=size,**STYLE)
    if not os.environ.get('NOPAL'):body['color_image']=b64(pal)   # Felt colours (NOPAL=1 for water etc.)
    st,r=req('POST','/map-objects',body);open(f'{RAW}/submit_{k}.json','w').write(scrub({'http':st,'body':r}))
    if st in(200,202):jobs.append((k,r.get('background_job_id') or (r.get('background_job_ids') or [None])[0],r))
    else:log('OBJ FAIL',k,st,scrub(r)[:400])
tot=0
for k,jid,r in jobs:
    j=wait(jid,k);u=j.get('usage') or {};tot+=float(u.get('generations') or u.get('usd') or 0)
    if k=='tileset':
        open(f'{out}/tileset_job.json','w').write(scrub(j));n=save_imgs(j,'tileset')
    else:n=save_imgs(j,k)
    log(k,j.get('status'),'images',n,'usage',u)
log('total usage',tot)
