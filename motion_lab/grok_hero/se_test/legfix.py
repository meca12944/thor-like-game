# 시험: 그림 도구가 정면 달리기 다리를 ~12px 길게 그림 → 허리띠 아래만 세로로 줄여 발을 땅(189)에 맞춤 (윗몸·얼굴은 그대로)
import sys,glob,os,numpy as np
from PIL import Image
k,belt=sys.argv[1],int(sys.argv[2]);o=k+'_leg';os.makedirs(o,exist_ok=True)
fs=sorted(glob.glob(k+'/*.png'));bot=max(Image.open(f).getbbox()[3] for f in fs);s=(189-belt)/(bot-belt);print('세로 배율',round(s,3))
for f in fs:
    im=Image.open(f).convert('RGBA');top=im.crop((0,0,256,belt));low=im.crop((0,belt,256,256))
    lh=round(low.height*s);low2=low.resize((256,lh),Image.BOX).quantize(colors=48,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE).convert('RGBA')
    A=np.array(low2);A[...,3]=np.where(np.array(low.resize((256,lh),Image.BOX))[...,3]>110,255,0);low2=Image.fromarray(A)
    c=Image.new('RGBA',(256,256));c.paste(top,(0,0));c.paste(low2,(0,belt),low2);c.save(f'{o}/{os.path.basename(f)}')
