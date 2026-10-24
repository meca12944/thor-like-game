import sys,json
from PIL import Image
from rembg import remove,new_session
CG='/home/user/thor-like-game/test128/assets/cg/'
s=new_session(sys.argv[2] if len(sys.argv)>2 else 'sam')
jobs=json.loads(sys.argv[1])
for n,parts in jobs.items():
  im=Image.open(CG+n+'.jpg').convert('RGB'); f=im.width/384
  for part,pts in parts.items():
    if s.__class__.__name__.lower().find('sam')>=0:
      prompt=[{"type":"point","data":[x*f,y*f],"label":1} for x,y in pts]
      m=remove(im,session=s,only_mask=True,sam_prompt=prompt)
    else: m=remove(im,session=s,only_mask=True)
    m.save(f'hd_{n}__{part}.png')
print('ok')
