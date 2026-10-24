# 이야기 그림 살리기: 사람·큰 물체 마스크(rembg sam / u2net) + 그 자리를 메운 배경판(cv2.inpaint). 결과 = assets/cg/rig/<그림>__<층>.png (L 마스크), <그림>__plate.png
import cv2, numpy as np
from PIL import Image
CG='/home/user/thor-like-game/test128/assets/cg/'; OUT=CG+'rig/'
RIG={'cg_felt_arrival':{'hero':'cg_felt_arrival__hero.png','castle':'cg_felt_arrival__castle.png'},
     'cg_linette_meet':{'linette':'cg_linette_meet__linette.png','hero':'cg_linette_meet__hero.png'},
     'cg_arachne_end':{'arachne':'cg_arachne_end__arachne.png','hero':'cg_arachne_end__hero.png'},
     'cg_memory_fire':{'hero':'cg_memory_fire_u2net_mask.png'}}
for n,parts in RIG.items():
  img=cv2.imread(CG+n+'.png'); uni=np.zeros(img.shape[:2],np.uint8)
  for p,f in parts.items():
    m=np.array(Image.open(f).convert('L'));m=(m>110).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8)); m=cv2.dilate(m,np.ones((2,2),np.uint8))
    Image.fromarray(m).save(OUT+f'{n}__{p}.png',optimize=True)
    if p!='castle': uni|=m
  ip=cv2.dilate(uni,np.ones((5,5),np.uint8))
  plate=cv2.inpaint(img,ip,7,cv2.INPAINT_TELEA)
  cv2.imwrite(OUT+f'{n}__plate.png',plate)
  print(n,{p:int((np.array(Image.open(OUT+f'{n}__{p}.png'))>0).mean()*100) for p in parts})
