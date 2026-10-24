# 그림표: 동작마다 한 줄, 위 = 지금(칼 있음), 아래 = 칼 없는 몸. -> motion_lab/research_v1/hero8/nosword_sheet.png
import json,os
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));N=ROOT+'/motion_lab/research_v1/hero8/nosword'
s=open(ROOT+'/test128/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16);ks=sorted(os.listdir(N));ks=[k for k in ks if os.path.isdir(f'{N}/{k}')]
cw,ch=110,130;cols=12;SH={}
W=Image.new('RGB',(90+cols*cw,len(ks)*2*ch),(90,140,60));d=ImageDraw.Draw(W)
def orig(k,q):
    f=A['anims'][k][q]
    if f[0] not in SH:SH[f[0]]=Image.open(ROOT+'/test128/assets/'+A['sheets'][f[0]]).convert('RGBA')
    x,y,w,h,ax,ay=A['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((x,y,x+w,y+h)),(128-ax,189-ay));return c
for r,k in enumerate(ks):
    d.text((4,r*2*ch+4),k,fill=(255,255,255),font=F);d.text((4,r*2*ch+ch+4),'칼 없음',fill=(255,255,120),font=F)
    for q,f in enumerate(sorted(os.listdir(f'{N}/{k}'))):
        for rr,im in enumerate([orig(k,q),Image.open(f'{N}/{k}/{f}').convert('RGBA')]):
            t=im.crop((73,60,183,190));W.paste(t,(90+q*cw,(r*2+rr)*ch),t)
W.save(ROOT+'/motion_lab/research_v1/hero8/nosword_sheet.png');print(W.size)
