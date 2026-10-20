# face skin tone match (see apply_thrust_v2.py / apply_hit3_face.py)
import numpy as np
from PIL import Image
def head_band(a):
    # head = top of the dark navy hair (sword blades and white trails above it are ignored)
    rgb=a[...,:3].astype(int);hair=(a[...,3]>0)&(rgb.max(-1)<110)&(rgb[...,2]>=rgb[...,0])
    ys=np.nonzero(hair.any(1))[0]
    if not len(ys): ys=np.nonzero((a[...,3]>0).any(1))[0]
    top=ys.min();return top+6,top+40
def skin_px(a,band):
    rgb=a[...,:3].astype(int);R,G,B=rgb[...,0],rgb[...,1],rgb[...,2];sat=(R-B)/np.maximum(R,1);hue=60*(G-B)/np.maximum(R-B,1)
    m=(a[...,3]>0)&(R>140)&(R>G)&(G>B)&((R-B)>35)&(sat<0.62)&(hue<38)  # skin; gold trim/pauldron is more saturated or more yellow
    mm=np.zeros_like(m);mm[band[0]:band[1]]=m[band[0]:band[1]];return mm
def ref_ramp(img):
    a=np.array(img.convert('RGBA'));m=skin_px(a,head_band(a));px=a[m][:,:3];return px[np.argsort(px.astype(int).sum(1))]
def fix_face2(img,ref):
    # face found from the picture itself (skin-coloured pixels in the head band), every skin pixel takes the reference ramp by brightness rank
    a=np.array(img.convert('RGBA'));m=skin_px(a,head_band(a))
    if m.sum()==0 or len(ref)==0: return img
    px=a[m][:,:3].astype(int);order=np.argsort(np.argsort(px.sum(1)));q=(order/max(1,len(px)-1)*(len(ref)-1)).round().astype(int)
    a[m,:3]=ref[q];return Image.fromarray(a)

def fix_face3(img,ref,depth=30):
    # stronger: inside the face band (hair top +6 .. +depth) every warm pixel counts as skin, saturated orange shading included;
    # the pauldron sits lower than this band
    a=np.array(img.convert('RGBA'));b0,_=head_band(a);rgb=a[...,:3].astype(int);R,G,B=rgb[...,0],rgb[...,1],rgb[...,2]
    m=(a[...,3]>0)&(R>120)&(R>G)&(G>B)&((R-B)>35);mm=np.zeros_like(m);mm[b0:b0+depth-6]=m[b0:b0+depth-6]
    from scipy import ndimage
    lab,n=ndimage.label(mm,structure=np.ones((3,3)));keep=np.zeros_like(mm)
    hair=(a[...,3]>0)&(rgb.max(-1)<110)&(B>=R);hd=ndimage.binary_dilation(hair,iterations=2)
    for i in range(1,n+1):  # the face sits inside the hair (most of its edge touches hair); the gold pauldron is outlined by the coat instead
        c=lab==i;edge=ndimage.binary_dilation(c,iterations=1)&~c
        px=rgb[c];sat=(px[:,0]-px[:,2])/np.maximum(px[:,0],1);hue=60*(px[:,1]-px[:,2])/np.maximum(px[:,0]-px[:,2],1)
        gold=((hue>40)&(sat>0.45)).sum()>=2  # yellow highlights = gold armour, not skin
        if not gold and (hd&edge).sum()>=0.5*edge.sum(): keep|=c
    mm=keep
    if mm.sum()==0 or len(ref)==0: return img
    px=rgb[mm];order=np.argsort(np.argsort(px.sum(1)));q=(order/max(1,len(px)-1)*(len(ref)-1)).round().astype(int);a[mm,:3]=ref[q];return Image.fromarray(a)
