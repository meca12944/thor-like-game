# 바늘 사수 바탕 그림: 그록 마스터 → 256칸(발 y249), 배율 1개(옆 서기 키 124). 조준·발사는 머리가 서기 자리에 오게 맞춤.
import os
from PIL import Image
C=os.path.dirname(os.path.abspath(__file__)); G=C+'/../../../grok_in/1장_마물_20261025/03_needle_marksman/m03_'
ss=Image.open(G+'side_stand.png').convert('RGBA'); b=ss.getbbox(); S=124/(b[3]-b[1]); print('scale',round(S,4))
for n,ax in [('side_stand',None),('front_stand',None),('aim',.41),('fire',.26)]:
    im=Image.open(G+n+'.png').convert('RGBA')
    bb=im.getbbox(); im=im.crop(bb); im=im.resize((round(im.width*S),round(im.height*S)),Image.LANCZOS)
    x=128-im.width//2 if ax is None else round(128-im.width*ax)  # 던지기: 머리(몸통)가 서기 자리에 오게
    c=Image.new('RGBA',(256,256),(0,0,0,0)); c.alpha_composite(im,(x,249-im.height)); c.save(f'{C}/base/{n}.png'); print(n,c.getbbox())
s=Image.open(f'{C}/base/side_stand.png'); b=s.getbbox(); f=s.crop(b); f=f.resize((round(f.width*1.6),round(f.height*1.6)),Image.LANCZOS)
c=Image.new('RGBA',(256,256),(0,0,0,0)); c.alpha_composite(f,(128-f.width//2,249-f.height)); c.save(f'{C}/key/side_big.png')
