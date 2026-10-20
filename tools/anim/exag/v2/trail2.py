# code-drawn crescents for every facing: arc on the side the hero faces. up = far side, drawn behind the body; right/down = drawn over the body
import math
from PIL import Image,ImageDraw
# (start deg, end deg, radius, thickness, y squash) ; image angles: 0 = +x, 90 = down
SW={'right':{'hit1':(-75,70,58,14,0.85),'hit2':(70,-75,58,14,0.85),'hit3':(-105,105,72,20,0.85)},
    'down': {'hit1':(25,155,58,14,0.62),'hit2':(155,25,58,14,0.62),'hit3':(10,170,72,20,0.62)},
    'up':   {'hit1':(335,205,54,8,0.62),'hit2':(205,335,54,8,0.62),'hit3':(190,350,64,9,0.62)}}
OFF={'right':(14,44),'down':(0,48),'up':(0,38)}
def crescent(dr,h,box,u0,u1):
    a0,a1,R,T,sq=SW[dr][h];x0,y0,x1,y1=box;cx=(x0+x1)/2+OFF[dr][0];cy=y0+OFF[dr][1]
    im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im);us=[u0+(u1-u0)*i/40 for i in range(41)]
    ang=lambda u:math.radians(a0+(a1-a0)*u);th=lambda u:T*math.sin(math.pi*(u-u0)/(u1-u0+1e-6))**0.8
    outer=[(cx+R*math.cos(ang(u)),cy+R*sq*math.sin(ang(u))) for u in us]
    inner=[(cx+(R-th(u))*math.cos(ang(u)),cy+(R-th(u))*sq*math.sin(ang(u))) for u in reversed(us)]
    d.polygon(outer+inner,fill=(238,238,252,255),outline=(196,196,232,255));return im
def stages(n):
    base=[(0,0.55),(0,1),(0.45,1),(0.8,1)];return base[:n]+[(0.9,1)]*max(0,n-4)
