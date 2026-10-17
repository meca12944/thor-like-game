import sys,json
from PIL import Image, ImageDraw, ImageFont
D='/workspace/thor-like-game/docs_art/'
ids=[l.split()[0] for l in open('/workspace/art_work/prop/lm_full.txt')]
out=sys.argv[1]; sc=float(sys.argv[2]); names=json.loads(open(sys.argv[3]).read()) if len(sys.argv)>3 else {}
per=int(sys.argv[4]) if len(sys.argv)>4 else 14
w,h=int(900*sc),int(1320*sc); top=40
rows=(len(ids)+per-1)//per
S=Image.new('RGBA',(w*per+60,(h+top)*rows),(38,40,48,255)); d=ImageDraw.Draw(S)
FP='/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc'
import os
f=ImageFont.truetype(FP,max(12,int(40*sc))) if os.path.exists(FP) else ImageFont.load_default()
fs=ImageFont.truetype(FP,14) if os.path.exists(FP) else ImageFont.load_default()
G=[(100,'crown',(255,255,255)),(207,'eye',(80,220,255)),(284,'chin',(255,160,60)),(694,'hip',(255,120,200)),(1260,'base',(255,230,80))]
GC=[(546,'child crown',(200,200,200)),(648,'child eye',(80,220,255)),(716,'child chin',(255,160,60)),(1037,'child hip',(255,120,200))]
for r in range(rows):
    y0=r*(h+top)
    for i,p in enumerate(ids[r*per:(r+1)*per]):
        cid=p.split('/')[1]
        im=Image.open(D+p+'.png').convert('RGBA').resize((w,h),Image.LANCZOS)
        S.alpha_composite(im,(60+i*w,y0+top))
        d.text((60+i*w+4,y0+6),names.get(cid,cid),fill='white',font=f)
    for y,l,c in G+GC:
        yy=y0+top+int(y*sc); dash= 'child' in l
        for x in range(60,S.width,12 if dash else 1):
            d.line([(x,yy),(x+(6 if dash else 1),yy)],fill=c+(200,),width=1)
        d.text((2,yy-8),l.replace('child ','c.'),fill=c,font=fs)
S.save(out)
