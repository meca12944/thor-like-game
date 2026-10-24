import sys,json
import numpy as np
from PIL import Image
from rembg import remove,new_session
CG='/home/user/thor-like-game/test128/assets/cg/'
s=new_session('sam')
jobs=json.loads(sys.argv[1])  # {name:{part:[[x,y],...]}}  in 384x216 coords
for n,parts in jobs.items():
  im=Image.open(CG+n+'.png').convert('RGB').resize((1536,864),Image.LANCZOS)
  for part,pts in parts.items():
    prompt=[{"type":"point","data":[x*4,y*4],"label":1} for x,y in pts]
    m=remove(im,session=s,only_mask=True,sam_prompt=prompt).resize((384,216),Image.BILINEAR)
    m.save(f'{n}__{part}.png')
print('ok')
