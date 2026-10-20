# white crescent for up (back-view) attacks, only on the far side (upper half circle around the shoulders), drawn behind the body
import math,numpy as np
from PIL import Image,ImageDraw
SW={'hit1':(330,210,58,14),'hit2':(210,330,58,14),'hit3':(195,345,70,20)}  # start deg, end deg, radius, max thickness
def crescent(h,center,u0,u1):
    a0,a1,R,T=SW[h];im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im);cx,cy=center
    us=[u0+(u1-u0)*i/40 for i in range(41)]
    ang=lambda u:math.radians(a0+(a1-a0)*u)
    th=lambda u:T*math.sin(math.pi*min(1,max(0,(u-u0)/(u1-u0+1e-6))))**0.8
    outer=[(cx+R*math.cos(ang(u)),cy+R*0.62*math.sin(ang(u))) for u in us]   # flattened for the top-down camera
    inner=[(cx+(R-th(u))*math.cos(ang(u)),cy+(R-th(u))*0.62*math.sin(ang(u))) for u in reversed(us)]
    d.polygon(outer+inner,fill=(238,238,252,255),outline=(196,196,232,255))
    return im
def stages(n_keys_with_trail):  # progress windows for successive trail keys: grow, full, fade
    base=[(0,0.55),(0,1),(0.45,1),(0.8,1)]
    return base[:n_keys_with_trail]+[(0.9,1)]*max(0,n_keys_with_trail-4)
def body_center(im):
    a=np.array(im)[...,3]>0;ys,xs=np.nonzero(a);return (xs.min()+xs.max())/2,ys.min()+38
