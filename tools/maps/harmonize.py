# Make background art sit with the characters (no credits): applied per layer before compositing.
#  1 shared palette  : background tiles/props/enemies are remapped to one master palette built from the hero + the tiles (no dither)
#  2 outline match   : the outer outline of props/enemies becomes the hero's coloured dark (deep purple) instead of black / none
#  3 quiet ground    : floor value contrast x0.65 and saturation x0.85 (busy ground was louder than the characters)
#  4 contact shadows : soft scene-coloured ellipse under every character and prop (feet sit on the ground)
#  5 one light       : whole frame graded together (warm light / cool shadow split-tone + light vignette), characters included
import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage
HERO_OUTLINE=np.array([35,25,39])
def build_palette(images,n=56):
    px=np.concatenate([np.array(im.convert('RGBA')).reshape(-1,4) for im in images]);px=px[px[:,3]>0][:,:3]
    px=px[np.random.default_rng(1).choice(len(px),min(len(px),60000),replace=False)].astype(float)
    C=px[np.random.default_rng(2).choice(len(px),n,replace=False)]
    for _ in range(14):
        d=((px[:,None,:]-C[None])**2).sum(-1);l=d.argmin(1)
        for k in range(n):
            s=px[l==k]
            if len(s):C[k]=s.mean(0)
    return C.round().astype(np.uint8)
def to_palette(im,P):
    a=np.array(im.convert('RGBA'));m=a[...,3]>0;rgb=a[...,:3][m].astype(int)
    d=((rgb[:,None,:]-P[None].astype(int))**2).sum(-1);a[...,:3][m]=P[d.argmin(1)];return Image.fromarray(a)
def outline(im,col=HERO_OUTLINE,thick=1):
    a=np.array(im.convert('RGBA'));m=a[...,3]>128;edge=m&~ndimage.binary_erosion(m,iterations=thick)
    dark=edge&(a[...,:3].max(-1)<90)|edge;a[...,:3][dark]=(a[...,:3][dark]*.25+col*.75).astype(np.uint8);a[...,3][m]=255;return Image.fromarray(a)
def quiet(im,k=.72,s=.9):
    a=np.array(im.convert('RGBA')).astype(float);rgb=a[...,:3];l=rgb.mean(-1,keepdims=True);mean=l[a[...,3]>0].mean()
    rgb=(rgb-l)*s+l;rgb=(rgb-mean)*k+mean;a[...,:3]=rgb.clip(0,255);return Image.fromarray(a.astype(np.uint8))
def shadow(canvas,x,y,w,col=(30,24,48),alpha=.5):
    h=max(4,int(w*.28));sh=Image.new('L',(w*2,h*2),0);from PIL import ImageDraw
    ImageDraw.Draw(sh).ellipse((w*.5,h*.5,w*1.5,h*1.5),fill=int(255*alpha));sh=sh.filter(ImageFilter.GaussianBlur(h*.35))
    layer=Image.new('RGBA',sh.size,col+(0,));layer.putalpha(sh);canvas.alpha_composite(layer,(int(x-w),int(y-h)))
def grade(im,warm=(255,226,180),cool=(70,80,140),amount=.14,vignette=.22):
    a=np.array(im.convert('RGB')).astype(float)/255;l=a.mean(-1,keepdims=True)
    tone=l*np.array(warm)/255+(1-l)*np.array(cool)/255;a=a*(1-amount)+a*tone*amount*2.2
    H,W=a.shape[:2];yy,xx=np.mgrid[0:H,0:W];r=np.hypot((xx-W/2)/(W/2),(yy-H/2)/(H/2));a*=(1-vignette*np.clip(r-.55,0,1)[...,None])
    return Image.fromarray((a.clip(0,1)*255).astype(np.uint8))
