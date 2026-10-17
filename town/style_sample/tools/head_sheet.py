import sys, json, numpy as np
from PIL import Image, ImageDraw, ImageFont
O='/workspace/town-demo/style_sample/'; C=json.load(open(O+'assets/idle_cells.json'))
FT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',12)
S=9; y0,y1=int(sys.argv[1]),int(sys.argv[2]); names=sys.argv[3].split(',')
tiles=[]
for n in names:
    sh=Image.open(O+f'assets/idle_{n}.png')
    for v,(x,y,w,h,ax,ay) in [(k,c) for k,c in C[n].items() if k!='back']:
        t=sh.crop((x,y+y0,x+w,y+y1)); bg=Image.new('RGBA',t.size,(84,108,74,255)); bg.alpha_composite(t)
        im=bg.convert('RGB').resize((w*S,(y1-y0)*S),Image.NEAREST); c=Image.new('RGB',(im.width+30,im.height+16),(20,20,20)); c.paste(im,(30,0)); d=ImageDraw.Draw(c)
        for r in range(y0,y1):
            yy=(r-y0)*S; d.line((26,yy,c.width,yy),fill=(90,90,90)); d.text((0,yy),str(r),fill=(255,255,0),font=FT)
        d.text((30,im.height+2),n+' '+v,fill='white',font=FT); tiles.append(c)
W=sum(t.width+6 for t in tiles); img=Image.new('RGB',(W,tiles[0].height)); x=0
for t in tiles: img.paste(t,(x,0)); x+=t.width+6
img.save(O+'work/heads_'+sys.argv[4]+'.png'); print(img.size)
