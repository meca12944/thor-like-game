import sys,numpy as np
from PIL import Image,ImageDraw
from measure import load
rows=[a.split(':') for a in sys.argv[2:]];S=2
W=max(len(load(c,k)) for c,k in rows)
im=Image.new('RGB',(W*160*S,len(rows)*150*S),(60,70,60));d=ImageDraw.Draw(im)
for r,(c,k) in enumerate(rows):
    for i,a in enumerate(load(c,k)):
        t=Image.fromarray(a).crop((48,50,208,200)).resize((160*S,150*S),Image.NEAREST)
        im.paste(t,(i*160*S,r*150*S),t);d.line([(i*160*S,(189-50)*S+r*150*S),((i+1)*160*S,(189-50)*S+r*150*S)],fill=(200,0,0))
        d.text((i*160*S+4,r*150*S+4),f"{k} {i}",fill=(255,255,0))
im.save(sys.argv[1])
