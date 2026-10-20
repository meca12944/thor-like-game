# Shared cleanup for PixelLab frames: binary alpha, drop small detached bits away from the main body.
import numpy as np
from PIL import Image
from scipy import ndimage
def clean(im):
    a=np.array(im.convert('RGBA'));m=a[...,3]>=128;a[...,3]=np.where(m,255,0)
    lab,n=ndimage.label(m,structure=np.ones((3,3)))
    if n==0:return Image.fromarray(a)
    sz=ndimage.sum(m,lab,range(1,n+1));big=int(np.argmax(sz))+1;ys,xs=np.nonzero(lab==big);x0,x1,y0,y1=xs.min()-8,xs.max()+8,ys.min()-4,ys.max()+8
    for i in range(1,n+1):
        if i==big:continue
        yy,xx=np.nonzero(lab==i)
        inside=xx.min()>=x0 and xx.max()<=x1 and yy.min()>=y0 and yy.max()<=y1
        if not inside or (sz[i-1]<40 and yy.max()<ys.min()+10):a[lab==i,3]=0
    return Image.fromarray(a)
