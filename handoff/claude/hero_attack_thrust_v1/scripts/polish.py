# attack clean-up (hit1/hit2 only; hit3 untouched): palette lock to the in-game colours, drop specks, feet on one baseline,
# hips may travel but not pop (<=5px a frame)
import json,os,numpy as np
from PIL import Image
from scipy import ndimage
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
_pal={}
def palette(key):
    if key in _pal: return _pal[key]
    srcs=[P+f'all/{h}_right/k{i}.png' for h in ('hit1','hit2') for i in range(8)]+[P+'all/idle_right/k0.png']
    if key!='side': srcs+= [P+f'q34/rot_{"south-east" if key=="se" else "north-east"}.png']
    cols=set()
    for s in srcs:
        a=np.array(Image.open(s).convert('RGBA'));m=a[...,3]>0;cols|=set(map(tuple,a[m][:,:3]))
    _pal[key]=np.array(sorted(cols),dtype=np.int32);return _pal[key]
def lock(im,key):
    a=np.array(im.convert('RGBA'));m=a[...,3]>0;px=a[m][:,:3].astype(np.int32);pal=palette(key)
    out=np.empty_like(px)
    for s in range(0,len(px),4096):
        d=((px[s:s+4096,None,:]-pal[None,:,:])**2).sum(-1);out[s:s+4096]=pal[d.argmin(1)]
    a[m,:3]=out;return Image.fromarray(a)
def despeck(im,minpx=8):
    # drop only tiny specks that float away from the body (feet / sword tips close to the body are kept)
    a=np.array(im.convert('RGBA'));m=a[...,3]>0;lab,n=ndimage.label(m,structure=np.ones((3,3)))
    if n>1:
        sz=np.bincount(lab.ravel());big=lab==(sz[1:].argmax()+1);near=ndimage.binary_dilation(big,iterations=4)
        for i in range(1,n+1):
            c=lab==i
            if sz[i]<minpx and not (c&near).any(): a[c]=0
    return Image.fromarray(a)
def ground(im):  # lowest body pixel (white/grey blade and trail pixels ignored)
    a=np.array(im.convert('RGBA')).astype(int);r,g,b=a[...,0],a[...,1],a[...,2];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    body=(a[...,3]>0)&~((mn>120)&(mx-mn<50));ys=np.nonzero(body.any(1))[0];return ys.max() if len(ys) else 189
def kp(clip,i):
    K={k['label']:(k['x']*256,k['y']*256) for k in json.load(open(P+f'jit/{clip}/{i:02d}_kp.json'))['keypoints']}
    return max(K['LEFT LEG'][1],K['RIGHT LEG'][1]),(K['LEFT HIP'][0]+K['RIGHT HIP'][0])/2
def polish(frames,clip,key,relock=None):
    """frames: [(img,ticks)] of the 8 keys; relock: indices to palette-lock (redrawn frames)"""
    gbase=189;hx0=None;prev=None;out=[]
    for i,(im,t) in enumerate(frames):
        if relock is None or i in relock: im=lock(im,key)
        im=despeck(im);gy=ground(im);dy=round(gbase-gy)
        a=np.array(im)[...,3]>0;hx=float(np.median(np.nonzero(a[max(0,gy-70):max(1,gy-40)].any(0))[0])) if a[max(0,gy-70):max(1,gy-40)].any() else 128.0  # body column (hips band)
        if prev is None: dx=0
        else:
            want=hx;lim=5;cur=prev[1]+max(-lim,min(lim,want-prev[1]));dx=round(cur-hx)
        prev=(i,hx+dx);o=Image.new('RGBA',(256,256));o.paste(im,(dx,dy),im);out.append((o,t))
    return out
