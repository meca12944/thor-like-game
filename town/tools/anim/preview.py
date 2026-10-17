# contact sheet of every animation (anchored at feet, green baseline), zoomed: tools/anim/preview.py hero out.png
import json,sys
from PIL import Image,ImageDraw
R='/workspace/town-demo/';ch=sys.argv[1];J=json.load(open(R+f'assets/anim/{ch}.json'));A=Image.open(R+'assets/'+J['src'])
Z=4;CW,CH=70,50;names=[n for n in J['anims'] if 'alias' not in J['anims'][n]]
mx=max(len(J['anims'][n]['frames']) for n in names)
S=Image.new('RGBA',(CW*mx+90,CH*len(names)),(70,90,60,255));d=ImageDraw.Draw(S)
for r,n in enumerate(names):
  d.text((2,r*CH+4),n,fill='white')
  for i,(c,t,dx,dy) in enumerate(J['anims'][n]['frames']):
    x,y,w,h,ax,ay=J['cells'][c];im=A.crop((x,y,x+w,y+h))
    ox=90+i*CW+30;oy=r*CH+42
    S.alpha_composite(im,(int(ox-ax+dx),int(oy-ay+dy)))
    d.line([(90+i*CW,oy+1),(90+i*CW+CW-4,oy+1)],fill=(0,255,0,255));d.text((90+i*CW+2,r*CH+2),str(t),fill=(255,255,0))
S=S.resize((S.width*Z//2,S.height*Z//2),Image.NEAREST);S.save(sys.argv[2])
