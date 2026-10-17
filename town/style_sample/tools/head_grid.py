import sys, json
from PIL import Image, ImageDraw, ImageFont
O='/workspace/town-demo/style_sample/'; C=json.load(open(O+'assets/idle_cells.json'))
FT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',16)
S=14; y0,y1=7,18; names=sys.argv[1].split(','); tiles=[]
for n in names:
    sh=Image.open(O+f'assets/idle_{n}.png'); row=[]
    for v in ('front','side'):
        x,y,w,h,ax,ay=C[n][v]; t=sh.crop((x,y+y0,x+w,y+y1)); bg=Image.new('RGBA',t.size,(84,108,74,255)); bg.alpha_composite(t)
        im=bg.convert('RGB').resize((w*S,(y1-y0)*S),Image.NEAREST); c=Image.new('RGB',(430,im.height+22),(20,20,20)); c.paste(im,(34,0)); d=ImageDraw.Draw(c)
        for r in range(y0,y1):
            yy=(r-y0)*S; d.line((30,yy,34+im.width,yy),fill=(120,120,120)); d.text((2,yy-1),str(r),fill=(255,255,0),font=FT)
        d.text((34,im.height+3),n+' '+v,fill='white',font=FT); row.append(c)
    tiles.append(row)
img=Image.new('RGB',(870,sum(r[0].height+6 for r in tiles)))
yy=0
for r in tiles:
    img.paste(r[0],(0,yy)); img.paste(r[1],(440,yy)); yy+=r[0].height+6
img.save(O+'work/hg_'+sys.argv[2]+'.png')
