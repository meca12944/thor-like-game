# pull the white crescent trail out of an in-game attack frame (big bright low-saturation blobs; the thin blade is smaller)
import numpy as np
from PIL import Image
from scipy import ndimage
def trail(img,minpx=150):
    a=np.array(img.convert('RGBA')).astype(int);r,g,b,al=a[...,0],a[...,1],a[...,2],a[...,3]
    m=(al>0)&(np.minimum(np.minimum(r,g),b)>150)&((np.maximum(np.maximum(r,g),b)-np.minimum(np.minimum(r,g),b))<60)
    m=ndimage.binary_dilation(m,iterations=1)&(al>0)
    lab,n=ndimage.label(m);keep=np.zeros_like(m)
    for i in range(1,n+1):
        c=lab==i
        if c.sum()>=minpx: keep|=c
    o=np.zeros_like(a);o[keep]=a[keep];return Image.fromarray(o.astype('uint8'),'RGBA'),int(keep.sum())
if __name__=='__main__':
    import sys
    for p in sys.argv[1:]: print(p,trail(Image.open(p))[1])
