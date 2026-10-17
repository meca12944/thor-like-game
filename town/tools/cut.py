import json, numpy as np
from PIL import Image, ImageDraw
L=json.load(open('/workspace/town-demo/tools/level.json'))
bg=Image.open('/workspace/town-demo/src/bg_town.jpg').convert('RGBA')
A='/workspace/town-demo/assets/'
bg.convert('RGB').save(A+'bg_town.jpg',quality=92)
def mask_of(o,W=1280,H=720):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    if 'poly' in o: d.polygon([tuple(p) for p in o['poly']],fill=255)
    if 'ellipse' in o:
        x,y,rx,ry=o['ellipse']; d.ellipse([x-rx,y-ry,x+rx,y+ry],fill=255)
    return m
out=[]
for o in L['overlays']:
    m=mask_of(o); bb=m.getbbox()
    im=Image.new('RGBA',bg.size,(0,0,0,0)); im.paste(bg,(0,0),m)
    im=im.crop(bb); fn='ov_'+o['name']+'.png'; im.save(A+fn)
    out.append(dict(name=o['name'],src=fn,x=bb[0],y=bb[1],sortY=o['sortY']))
L['overlayImgs']=out
json.dump(L,open(A+'level.json','w'))
# debug
dbg=bg.convert('RGB'); d=ImageDraw.Draw(dbg,'RGBA')
for o in L['blocks']:
    if 'poly' in o: d.polygon([tuple(p) for p in o['poly']],fill=(255,0,0,70),outline=(255,0,0,255))
    if 'ellipse' in o:
        x,y,rx,ry=o['ellipse']; d.ellipse([x-rx,y-ry,x+rx,y+ry],fill=(255,0,0,70),outline=(255,0,0,255))
for o in L['overlays']:
    m=mask_of(o); e=np.asarray(m)>0
    edge=Image.fromarray(((e ^ np.roll(e,1,0)) | (e ^ np.roll(e,1,1))).astype(np.uint8)*255)
    dbg.paste((0,200,255,255),(0,0),edge)
    d.line([(0,o['sortY']),(1280,o['sortY'])],fill=(0,200,255,60))
b=L['bounds']; d.rectangle(b,outline=(255,255,0,255))
dbg.convert('RGB').save('/tmp/debug_level2.png')
