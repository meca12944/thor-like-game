"""주인공·리네트 키 비율 후보 그림: 각자 방향마다 키를 하나로 맞추고(주인공 124), 리네트를 비율대로"""
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from fix import *
from pxscale import pxscale
F=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',14)
def hgt(a):return feet_bot(a)-int(head_y([a])[0])
def sc(a,s):
    if abs(s-1)<1e-3:return a
    b=np.array(pxscale(Image.fromarray(a),s));o=np.zeros_like(a);h,w=b.shape[:2];ox,oy=int(round(128-128*s)),int(round(189-189*s))
    ys,xs=slice(max(0,oy),min(256,oy+h)),slice(max(0,ox),min(256,ox+w));o[ys,xs]=b[ys.start-oy:ys.stop-oy,xs.start-ox:xs.stop-ox];return o
P=[('right','right'),('down','south'),('up','north')]
H={h:load('hero8','idle_'+h)[0] for h,_ in P};L={l:load('linette','idle_'+l)[0] for _,l in P}
rows=[('지금',None)]+[(f'리네트 = 주인공의 {int(r*100)}%',r) for r in (0.94,0.92,0.89)]
im=Image.new('RGB',(3*200+10,len(rows)*165+10),(70,84,70));d=ImageDraw.Draw(im)
for i,(name,r) in enumerate(rows):
    oy=i*165+10
    for j,(h,l) in enumerate(P):
        a=H[h];b=L[l]
        if r:a=sc(a,124/hgt(a));b=sc(b,124*r/hgt(b))
        for img,dx in ((a,-38),(b,38)):
            t=Image.fromarray(img).crop((48,40,208,200));im.paste(t,(j*200+20+dx,oy-10),t)
        d.text((j*200+8,oy+132),f'{hgt(a)} : {hgt(b)}',fill=(255,255,255),font=F)
    d.line([(0,oy+139),(610,oy+139)],fill=(150,60,60));d.text((4,oy-6),name,fill=(255,240,120),font=F)
im.resize((im.width*2,im.height*2),Image.NEAREST).save('ratio.png');print(im.size)
