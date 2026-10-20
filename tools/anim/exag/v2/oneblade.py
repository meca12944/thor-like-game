# side frames: when a blade sticks out in front (right of the chest), delete blade-like streaks behind the body (PixelLab sometimes draws a second sword / grey smear)
import numpy as np
from PIL import Image
from scipy import ndimage
def steel(a):
    r,g,b,al=[a[...,i].astype(int) for i in range(4)];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    return (al>0)&(mn>85)&(mx-mn<45)
def fix(im):
    a=np.array(im.convert('RGBA'));al=a[...,3]>0;ys,xs=np.nonzero(al)
    # chest x = median x of the dark body pixels in the torso band
    band=al.copy();band[:ys.min()+25]=0;band[ys.min()+70:]=0;cx=np.median(np.nonzero(band)[1])
    st=steel(a);lab,n=ndimage.label(st,structure=np.ones((3,3)))
    comps=[(lab==i) for i in range(1,n+1)];front=[c for c in comps if c.sum()>=25 and np.nonzero(c)[1].mean()>cx+20]
    if not front: return im,0
    k=0;core=ndimage.binary_erosion(al,iterations=2);lab2,n2=ndimage.label(core)
    if n2: core=ndimage.binary_dilation(lab2==(np.bincount(lab2.ravel())[1:].argmax()+1),iterations=1)
    for c in comps:
        yy,x=np.nonzero(c)
        if c.sum()>=12 and x.mean()<cx-12:
            r=np.zeros_like(c);r[max(0,yy.min()-4):yy.max()+5,0:x.max()+3]=1  # blade + its dark outline
            kill=r&al&~core;kill|=c;a[kill]=0;k+=int(kill.sum())
    return Image.fromarray(a),k
