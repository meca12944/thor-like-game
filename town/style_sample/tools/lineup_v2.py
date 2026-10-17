import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
S='/workspace/town-demo/style_sample/'
F=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf',22)
from build_fem import NAMES
cells=json.load(open(S+'assets/idle_cells.json'))
order=['hero','a_tailor','h_mystic','g_dancer','f_diver','e_tailor','c_priest','d_yuna','g_tool']
K=5; colw=64*K; H=58*K+110
out=Image.new('RGBA',(colw*len(order)+40,H+60),(34,38,44,255)); d=ImageDraw.Draw(out)
d.text((20,12),'lineup_v2 — 768x432 grid, hero-matched proportions (56 px, head 14 px = 4.0 heads, legs 20 px, same baseline). x5 nearest',font=F,fill=(230,230,230))
base=60+57*K
for i,n in enumerate(order):
    sh=Image.open(S+f'assets/idle_{n}.png'); x,y,w,h,ax,ay=cells[n]['front']
    c=sh.crop((x,y,x+w,y+h)).resize((w*K,h*K),Image.NEAREST); cx=20+i*colw+colw//2
    out.alpha_composite(c,(cx-ax*K,base-(ay+1)*K))
    lab=NAMES[n]+(' (modern)' if n=='d_yuna' else '')
    d.text((cx-len(lab)*6,base+14),lab,font=F,fill=(255,230,160) if n!='hero' else (160,220,255))
for yy,col in ((base-56*K,(255,210,80)),(base-43*K,(255,90,90)),(base-20*K,(80,200,255)),(base,(120,255,120))):
    d.line([(10,yy),(out.width-10,yy)],fill=col+(110,),width=1)
out.save(S+'lineup_v2.png'); print(out.size)
