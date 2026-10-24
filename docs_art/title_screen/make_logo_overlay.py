"""Logo-only overlay for the in-game title (test128/assets/title/title_c_logo.png).
Same logo/subtitle/rule/glow as make_titles.py build_overlay(cx=W/2, ty=60, align='c'), but WITHOUT the baked
menu, its red selection diamond and the bottom darkening band: test128/title.js draws a live menu (selection, 저장 없음)
and the bottom band in CSS so it spans the full screen width. Run from this folder: python3 make_logo_overlay.py <out.png>
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
G='/usr/share/fonts/truetype/sand-box/google/'
EN=G+'Cormorant SC/CormorantSC-Bold.ttf'
KO=G+'Nanum Myeongjo/NanumMyeongjo-Bold.ttf'
SUB='\uC0AC\uBA78\uC758 \uADA4\uC801'  # 사멸의 궤적
assert SUB=='사멸의 궤적' and ord(SUB[4])==0xADA4
W,H=1920,1080; TXT=(240,228,200); ACC=(176,64,52)
def tw(d,s,f,sp=0): return sum(d.textlength(c,font=f) for c in s)+sp*(len(s)-1)
def draw_spaced(d,xy,s,f,fill,sp):
    x,y=xy
    for c in s: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
cx,ty=W/2,60
bg=Image.new('RGBA',(W,H),(0,0,0,0))
glow=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(glow).ellipse([cx-560,ty-120,cx+560,ty+300],fill=(20,12,8,95))
bg=Image.alpha_composite(bg,glow.filter(ImageFilter.GaussianBlur(90)))
d=ImageDraw.Draw(bg)
fen1=ImageFont.truetype(EN,58); fen2=ImageFont.truetype(EN,128); fko=ImageFont.truetype(KO,64)
l1,l2='Trail of','Extinction'; w1=tw(d,l1,fen1,10); w2=tw(d,l2,fen2,6); wk=tw(d,SUB,fko,22)
ly=ty+52+150
items=[(cx-w1/2,ty,l1,fen1,10),(cx-w2/2,ty+52,l2,fen2,6),(cx-wk/2,ly+34,SUB,fko,22)]
txt=Image.new('RGBA',(W,H),(0,0,0,0)); sh=Image.new('RGBA',(W,H),(0,0,0,0)); dt=ImageDraw.Draw(txt); ds=ImageDraw.Draw(sh)
for x,y,s,f,sp in items: draw_spaced(ds,(x+3,y+4),s,f,(15,8,4,210),sp); draw_spaced(dt,(x,y),s,f,TXT,sp)
bg=Image.alpha_composite(Image.alpha_composite(bg,sh.filter(ImageFilter.GaussianBlur(6))),txt)
d=ImageDraw.Draw(bg); rw=max(w2,wk)+40; rx=cx-rw/2
d.line([(rx,ly+10),(rx+rw,ly+10)],fill=(220,205,175,255),width=2)
mx=rx+rw/2; d.polygon([(mx,ly+1),(mx+9,ly+10),(mx,ly+19),(mx-9,ly+10)],fill=ACC,outline=(230,210,170))
bg.crop((0,0,W,540)).save(sys.argv[1] if len(sys.argv)>1 else 'title_c_logo.png', optimize=True)  # logo lives in the top half only
