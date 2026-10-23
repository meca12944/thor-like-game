# Code-drawn projectiles / flashes for the Felt mobs (shared by patterns.py and shoot.py).
import math
# drawn on a 1/3-res layer, upscaled x3 nearest for a pixel look
def ang_pts(cx,cy,d,pts):
    c,s=d;return [(cx+x*c-y*s,cy+x*s+y*c) for x,y in pts]
def rot(d,a):
    c,s=math.cos(a),math.sin(a);return (d[0]*c-d[1]*s,d[0]*s+d[1]*c)
def draw_proj(g,kind,x,y,d,t,age):
    if kind=='needle':
        g.line(ang_pts(x,y,d,[(-7,0),(5,0)]),fill=(30,30,36),width=3);g.line(ang_pts(x,y,d,[(-6,0),(5,0)]),fill=(220,224,232),width=1)
        g.point(ang_pts(x,y,d,[(-5,0)]),fill=(30,30,36))
        for k in range(1,4):g.point(ang_pts(x,y,d,[(-7-3*k,0)]),fill=(160,160,170))
    elif kind=='threadball':
        g.ellipse((x-5,y-5,x+5,y+5),fill=(200,198,190),outline=(40,38,40))
        for k in range(3):a=age*0.3+k*2.1;g.arc((x-4,y-4,x+4,y+4),math.degrees(a),math.degrees(a)+120,fill=(120,116,112))
        tail=[ang_pts(x,y,d,[(-6-2*k,2*math.sin(age*0.4+k*0.9))])[0] for k in range(10)];g.line(tail,fill=(190,186,178),width=1)
    elif kind=='blade':
        p=rot((1,0),age*0.5);g.polygon(ang_pts(x,y,p,[(-8,0),(0,-2),(8,0),(0,2)]),fill=(170,90,50),outline=(50,25,15))
        g.polygon(ang_pts(x,y,rot(p,math.pi/2),[(-8,0),(0,-2),(8,0),(0,2)]),fill=(150,75,40),outline=(50,25,15))
        g.ellipse((x-1,y-1,x+1,y+1),fill=(230,200,140))
    elif kind=='pin':
        g.line(ang_pts(x,y,d,[(-5,0),(4,0)]),fill=(30,30,36),width=3);g.line(ang_pts(x,y,d,[(-5,0),(4,0)]),fill=(210,214,220),width=1)
        hx,hy=ang_pts(x,y,d,[(-6,0)])[0];g.ellipse((hx-2,hy-2,hx+2,hy+2),fill=(200,30,40),outline=(60,10,14))
    elif kind=='web':
        g.ellipse((x-6,y-6,x+6,y+6),fill=(235,235,240,180),outline=(90,90,100))
        for k in range(6):a=k*math.pi/3+age*0.05;g.line((x,y,x+6*math.cos(a),y+6*math.sin(a)),fill=(150,150,160))
        g.ellipse((x-3,y-3,x+3,y+3),outline=(150,150,160))
    elif kind=='venom':
        g.line(ang_pts(x,y,d,[(-6,0),(4,0)]),fill=(20,40,20),width=3);g.line(ang_pts(x,y,d,[(-5,0),(4,0)]),fill=(150,230,90),width=1)
        for k in range(1,3):tx,ty=ang_pts(x,y,d,[(-7-4*k,0)])[0];g.point((tx,ty),fill=(100,200,60))
    elif kind=='orb':
        r=5+math.sin(age*0.3);g.ellipse((x-r-3,y-r-3,x+r+3,y+r+3),fill=(120,40,170,90));g.ellipse((x-r,y-r,x+r,y+r),fill=(150,60,210),outline=(50,10,70))
        g.ellipse((x-2,y-2-1,x+2,y+2-1),fill=(230,190,255))
    elif kind=='shard':
        p=rot((1,0),age*0.4);g.polygon(ang_pts(x,y,p,[(-5,-3),(6,0),(-3,4)]),fill=(130,126,120),outline=(40,38,36))
        g.line(ang_pts(x,y,p,[(-2,-1),(3,0)]),fill=(160,90,200))
def draw_zone(g,x,y,age):   # web slow zone left where a web shot ends
    al=max(0,200-age*2);g.ellipse((x-12,y-7,x+12,y+7),outline=(200,200,210,al));g.line((x-12,y,x+12,y),fill=(200,200,210,al));g.line((x,y-7,x,y+7),fill=(200,200,210,al))
def flash(g,x,y,age,col):   # release flash ring
    r=4+age*1.5;al=max(0,220-age*28);g.ellipse((x-r,y-r,x+r,y+r),outline=col+(al,),width=2)
def slash(g,x,y,age,flip=False):  # melee hit arc
    al=max(0,240-age*30);r=14
    g.arc((x-r,y-r,x+r,y+r),-70,70,fill=(255,250,230,al),width=3)
