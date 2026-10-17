# piecewise vertical/horizontal remap to the proportion template (target->source sampling)
import numpy as np, cv2
from PIL import Image
def interp(yt, ct, cs):
    """piecewise linear, linear extrapolation with end-segment slope"""
    ct=np.asarray(ct,float); cs=np.asarray(cs,float)
    out=np.interp(yt,ct,cs)
    lo=yt<ct[0]; hi=yt>ct[-1]
    out[lo]=cs[0]+(yt[lo]-ct[0])*(cs[1]-cs[0])/(ct[1]-ct[0])
    out[hi]=cs[-1]+(yt[hi]-ct[-1])*(cs[-1]-cs[-2])/(ct[-1]-ct[-2])
    return out
def warp(img, size, ct, cs, sx_y, sx_v, cxt, cxs_y, cxs_v):
    """img RGBA array; ct/cs y control points; sx given as (target y, scale) knots; cxs source centre knots (target y)."""
    W,H=size
    yt=np.arange(H,dtype=float)
    ys=interp(yt,ct,cs)
    sx=np.interp(yt,sx_y,sx_v)
    cxs=np.interp(yt,cxs_y,cxs_v)
    xt=np.arange(W,dtype=float)
    mx=(cxs[:,None]+(xt[None,:]-cxt)/sx[:,None]).astype(np.float32)
    my=np.repeat(ys[:,None],W,1).astype(np.float32)
    f=img.astype(np.float32)/255; a=f[...,3:]
    pm=np.concatenate([f[...,:3]*a,a],2)
    # supersample-ish: area pre-blur when shrinking strongly is unnecessary here (scales 0.6-1.6)
    o=cv2.remap(pm,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    o=np.clip(o,0,1); al=o[...,3:]
    rgb=np.where(al>1e-4,o[...,:3]/np.maximum(al,1e-4),0)
    return (np.dstack([np.clip(rgb,0,1),al])*255+0.5).astype(np.uint8)
