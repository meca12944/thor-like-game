# head locator: normalized cross-correlation of the idle head (hair + face silhouette, luminance*alpha) over the upper part of the frame
import numpy as np
from PIL import Image
IDLE='/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/south/000.png'
HB=(104,60,144,100)  # head box in idle (hair crown .. chin)
def feat(a):
    a=a.astype(float);al=a[...,3]/255;lum=a[...,:3].mean(-1)/255
    hair=al*((a[...,:3].max(-1)<90)&(a[...,2]>=a[...,0]-10));skin=al*((a[...,0]>150)&(a[...,0]-a[...,2]>30))
    return np.stack([hair,skin*.5,al*.3],-1)
I=np.array(Image.open(IDLE).convert('RGBA'));T=feat(I)[HB[1]:HB[3],HB[0]:HB[2]];T=T-T.mean()
def find(a):
    F=feat(a);h,w=T.shape[:2];best=(-1e9,0,0)
    for y in range(10,140):
        for x in range(60,200-w):
            P=F[y:y+h,x:x+w];P=P-P.mean();s=(P*T).sum()/(np.sqrt((P*P).sum()*(T*T).sum())+1e-6)
            if s>best[0]:best=(s,x,y)
    return best
