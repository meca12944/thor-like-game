# crescent that follows the blade: arc through the blade tip around the shoulder, leading the tip a little, tail along the swing
import math,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
def pivot(im):
    a=np.array(im)[...,3]>0;ys,xs=np.nonzero(a);band=a.copy();band[:ys.min()+25]=0;band[ys.min()+70:]=0
    return float(np.median(np.nonzero(band)[1])),ys.min()+42.0
def tip(im):
    a=np.array(im.convert('RGBA')).astype(int);r,g,b,al=[a[...,i] for i in range(4)]
    mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b);st=(al>0)&(mn>120)&(mx-mn<50)
    lab,n=ndimage.label(st,structure=np.ones((3,3)));px,py=pivot(im);best=None
    for i in range(1,n+1):
        ys,xs=np.nonzero(lab==i)
        if len(xs)<15: continue
        d=np.hypot(xs-px,ys-py);j=d.argmax()
        if best is None or d[j]>best[2]: best=(xs[j],ys[j],d[j])
    return best
def arc(center,R,a_tip,sgn,span,lead=40,T=None,sq=1.0):
    # Ys8-like: thin clean half-moon, sharp tail, a hair ahead of the blade tip
    T=T or min(9,0.15*R);cx,cy=center;a0=a_tip-sgn*span;a1=a_tip+sgn*lead;us=[i/48 for i in range(49)]
    ang=lambda u:math.radians(a0+(a1-a0)*u)
    th=lambda u:T*(u**1.3)*max(0.0,1-max(0,(u-0.85)/0.15))**0.5  # grows from the tail, thickest near the tip, rounds off at the front
    im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im);Ro=R+2
    outer=[(cx+Ro*math.cos(ang(u)),cy+Ro*sq*math.sin(ang(u))) for u in us]
    inner=[(cx+(Ro-th(u))*math.cos(ang(u)),cy+(Ro-th(u))*sq*math.sin(ang(u))) for u in reversed(us)]
    d.polygon(outer+inner,fill=(240,242,255,235))
    inner2=[(cx+(Ro-th(u)*0.45)*math.cos(ang(u)),cy+(Ro-th(u)*0.45)*sq*math.sin(ang(u))) for u in reversed(us)]
    d.polygon(outer+inner2,fill=(255,255,255,255))  # bright edge
    return im
