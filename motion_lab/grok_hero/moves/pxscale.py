# owner 10-21 "아래 위 도트가 부드럽지 않아 좌우 만큼": nearest-neighbour resizes doubled/dropped pixel rows -> use this everywhere a frame is rescaled
# pixel-art friendly rescale: LANCZOS on premultiplied RGBA, hard alpha, colours snapped back to the source frame's own palette
import numpy as np
from PIL import Image
def pxscale(im,s):
    im=im.convert('RGBA');a=np.array(im).astype(float);al=a[:,:,3:4]/255;pm=np.concatenate([a[:,:,:3]*al,a[:,:,3:4]],2)
    W,H=im.size;w2,h2=max(1,round(W*s)),max(1,round(H*s))
    ch=[np.array(Image.fromarray(pm[:,:,k].astype(np.float32),'F').resize((w2,h2),Image.LANCZOS)) for k in range(4)]
    A=np.clip(ch[3],0,255);rgb=np.stack([np.clip(ch[k]/np.maximum(A,1e-3)*255,0,255) for k in range(3)],2)
    pal=np.unique(a[a[:,:,3]>128][:,:3].astype(int),axis=0).astype(float)
    flat=rgb.reshape(-1,3);out=np.zeros_like(flat)
    for i in range(0,len(flat),4096):
        d=((flat[i:i+4096,None,:]-pal[None])**2).sum(2);out[i:i+4096]=pal[d.argmin(1)]
    o=np.concatenate([out.reshape(h2,w2,3),(A>128)[:,:,None]*255],2).astype(np.uint8);return Image.fromarray(o,'RGBA')
