# preview anims from the built atlas: python3 tools/anim/preview_anims.py out.png anim1 anim2 ...
import json,sys
from PIL import Image,ImageDraw
J=json.load(open('/workspace/town-demo/assets/anim/hero.json'));AT=Image.open('/workspace/town-demo/assets/anim/hero.png')
names=sys.argv[2:];S=3;CW=56;CH=50
W=max(len(J['anims'][n]['frames']) for n in names)*CW*S+90;c=Image.new('RGBA',(W,len(names)*CH*S),(70,90,70,255));d=ImageDraw.Draw(c)
for r,n in enumerate(names):
  d.text((2,r*CH*S+4),n,fill='white')
  for i,(ci,t,dx,dy) in enumerate(J['anims'][n]['frames']):
    x,y,w,h,ax,ay=J['cells'][ci];im=AT.crop((x,y,x+w,y+h)).resize((w*S,h*S),Image.NEAREST)
    ox=90+i*CW*S+CW*S//2-int(ax*S)+dx*S;oy=r*CH*S+(CH-6)*S-int(ay*S)+dy*S;c.alpha_composite(im,(ox,oy))
    d.line((90+i*CW*S,(r*CH+CH-6)*S,90+(i+1)*CW*S-4,(r*CH+CH-6)*S),fill=(40,50,40))
c.save(sys.argv[1])
