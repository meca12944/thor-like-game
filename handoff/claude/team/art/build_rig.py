# 이야기 그림 살리기 (원본 1280x720): 사람·성 마스크(rembg sam / u2net, sam_hd.py) + 그 자리를 메운 배경판(cv2.inpaint)
# 결과 = test128/assets/cg/rig/<그림>__<층>.png (L 마스크), <그림>__plate.jpg
import cv2, numpy as np, glob, os
from PIL import Image
CG='/home/user/thor-like-game/test128/assets/cg/'; OUT=CG+'rig/'
for f in glob.glob(OUT+'*'): os.remove(f)
RIG={'cg_felt_arrival':['hero','castle'],'cg_linette_meet':['linette','hero'],'cg_arachne_end':['arachne','hero'],'cg_memory_fire':['hero']}
for n,parts in RIG.items():
  img=cv2.imread(CG+n+'.jpg'); uni=np.zeros(img.shape[:2],np.uint8)
  for p in parts:
    m=np.array(Image.open(f'hd_{n}__{p}.png').convert('L').resize((img.shape[1],img.shape[0])));m=(m>110).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)); m=cv2.dilate(m,np.ones((3,3),np.uint8))
    Image.fromarray(m).save(OUT+f'{n}__{p}.png',optimize=True)
    if p!='castle': uni|=m
  ip=cv2.dilate(uni,np.ones((15,15),np.uint8))
  plate=cv2.inpaint(img,ip,15,cv2.INPAINT_TELEA)
  cv2.imwrite(OUT+f'{n}__plate.jpg',plate,[cv2.IMWRITE_JPEG_QUALITY,88])
print(sorted(os.listdir(OUT)))
