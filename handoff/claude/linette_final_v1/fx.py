# Engine-style thrust trail (drawn in code, not baked into the sprite): a bright lance streak that shoots out AHEAD of the needle tip,
# thick in the middle and pointed at both ends, white core + cyan glow, with thin speed lines; grows in 2 ticks, then fades.
# age = ticks since the full-lunge frame started.
from PIL import Image,ImageDraw
def lance(g,cx,cy,dx,dy,nx,ny,back,ahead,w,col):
    g.polygon([(cx-dx*back,cy-dy*back),(cx+nx*w/2,cy+ny*w/2),(cx+dx*ahead,cy+dy*ahead),(cx-nx*w/2,cy-ny*w/2)],fill=col)
def draw_thrust(base,x,y,meta,age):
    big=meta['big']; life=16 if big else 12
    if age<0 or age>=life: return
    grow=min(1,(age+1)/2); a=1-age/life; dx,dy=meta['dir']; nx,ny=-dy,dx
    tx,ty=x+meta['tip'][0],y+meta['tip'][1]
    ahead=(70 if big else 52)*grow; back=(34 if big else 26); W=(12 if big else 9)
    cx,cy=tx+dx*ahead*0.35,ty+dy*ahead*0.35
    lay=Image.new('RGBA',base.size); g=ImageDraw.Draw(lay)
    lance(g,cx,cy,dx,dy,nx,ny,back+ahead*0.35,ahead*0.65,W,(90,210,255,int(120*a)))
    lance(g,cx,cy,dx,dy,nx,ny,back*0.8+ahead*0.3,ahead*0.6,W*0.45,(210,250,255,int(220*a)))
    lance(g,cx,cy,dx,dy,nx,ny,back*0.6+ahead*0.25,ahead*0.55,max(1.5,W*0.18),(255,255,255,int(255*a)))
    for o,l in ((W*0.9,0.55),(-W*0.9,0.45)) if not big else ((W*0.9,0.6),(-W*0.9,0.5),(W*1.6,0.35),(-W*1.6,0.3)):   # speed lines
        sx,sy=cx+nx*o-dx*back*0.6,cy+ny*o-dy*back*0.6; L=(back+ahead)*l
        g.line((sx,sy,sx+dx*L,sy+dy*L),fill=(200,245,255,int(170*a)),width=1)
    if age<4:  # impact star at the far end
        ex,ey=tx+dx*ahead*0.95,ty+dy*ahead*0.95; r=5 if big else 4
        g.line((ex-r,ey,ex+r,ey),fill=(255,255,255,int(255*a))); g.line((ex,ey-r,ex,ey+r),fill=(255,255,255,int(255*a)))
    base.alpha_composite(lay)
