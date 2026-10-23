# Blasphemous-style mood pass for a top-down room (no credits), on top of harmonize.py:
#  1 dark, muted ground + one dominant hue family per zone (here: dusk ochre / cold violet shadows)
#  2 light pools: torches/fountain light a warm area, everything else sits in cool ambient (characters get lit by the same map)
#  3 foreground silhouettes: near-black arch/pillar shapes framing the bottom/side edges (depth without parallax)
#  4 atmosphere: light shafts from top-left + floating dust motes
import numpy as np,random
from PIL import Image,ImageDraw,ImageFilter
def lightmap(size,lights,ambient=(104,96,136)):
    W,H=size;yy,xx=np.mgrid[0:H,0:W].astype(float);L=np.zeros((H,W,3))+np.array(ambient)/255
    for x,y,r,col,k in lights:
        f=np.clip(1-np.hypot((xx-x),(yy-y)*1.35)/r,0,1)**1.6;L+=f[...,None]*np.array(col)/255*k
    return L
def apply_light(img,L,gamma=1.0):
    a=np.array(img.convert('RGB')).astype(float)/255;return Image.fromarray((np.clip(a*L*1.25,0,1)*255).astype(np.uint8))
def mute_ground(img,k=.78,s=.7,tint=(.98,.93,.86)):
    a=np.array(img.convert('RGBA')).astype(float);rgb=a[...,:3];l=rgb.mean(-1,keepdims=True);rgb=(rgb-l)*s+l;rgb*=k*np.array(tint);a[...,:3]=rgb.clip(0,255);return Image.fromarray(a.astype(np.uint8))
def foreground(img,col=(14,10,20)):
    W,H=img.size;fg=Image.new('RGBA',(W,H));d=ImageDraw.Draw(fg)
    for x0 in (-30,W-120):                                  # broken pillars at the bottom corners
        d.rectangle((x0,H-260,x0+150,H),fill=col+(255,));d.rectangle((x0-20,H-280,x0+170,H-250),fill=col+(255,))
    return fg
def shafts(size,ang=-0.55,n=4,seed=3):
    W,H=size;r=random.Random(seed);m=Image.new('L',(W,H),0);d=ImageDraw.Draw(m)
    for i in range(n):
        x=r.randint(int(W*.05),int(W*.6));w=r.randint(60,140);dx=int(H*np.tan(-ang))
        d.polygon([(x,0),(x+w,0),(x+w+dx,H),(x+dx,H)],fill=r.randint(26,44))
    return m.filter(ImageFilter.GaussianBlur(28))
def dust(size,n=90,seed=7):
    W,H=size;r=random.Random(seed);return [(r.randrange(W),r.randrange(H),r.choice((1,1,2))) for _ in range(n)]
