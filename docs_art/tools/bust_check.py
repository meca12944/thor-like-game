import sys
from PIL import Image, ImageDraw, ImageFont
D='/workspace/thor-like-game/docs_art/bust/'
IDS=['hero','a_tailor','h_mystic','g_dancer','f_diver','e_tailor','c_priest','d_yuna']
NM={}
import json,re
src=sys.argv[1] if len(sys.argv)>1 else D; out=sys.argv[2]; sc=float(sys.argv[3]) if len(sys.argv)>3 else 0.3
w,h=int(1024*sc),int(1280*sc); top=60
sheet=Image.new('RGBA',(w*8,h+top+10),(38,40,48,255)); d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',22) if __import__('os').path.exists('/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc') else ImageFont.load_default()
names=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
for i,c in enumerate(IDS):
    im=Image.open(src+c+'/neutral.png').convert('RGBA').resize((w,h),Image.LANCZOS)
    sheet.alpha_composite(im,(i*w,top)); d.text((i*w+8,8),names.get(c,c),fill='white',font=f)
G=[(150,'crown',(255,255,255)),(391,'eye',(80,220,255)),(565,'chin',(255,160,60)),(660,'shoulder',(120,255,120)),(843,'chest',(255,120,200)),(1042,'waist',(255,230,80))]
for y,l,col in G:
    yy=top+int(y*sc); d.line([(0,yy),(w*8,yy)],fill=col+(230,),width=2); d.text((4,yy-14),l,fill=col,font=ImageFont.load_default())
for i in range(8):
    x=i*w+int(512*sc); d.line([(x,top),(x,top+h)],fill=(255,255,255,90),width=1)
    for s in (-235,235): xx=x+int(s*sc); d.line([(xx,top+int(640*sc)),(xx,top+int(680*sc))],fill=(120,255,120,255),width=3)
sheet.save(out)
