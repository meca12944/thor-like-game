# Champion test enemy: boar sheet champ01.jpg (4x3 grid of 320x240 cells, faces LEFT).
# Uses extract.py key() (magenta chroma key + despill). Frames: row0 c0-3 = charge, row1 c3 = idle, row1 c2 = stunned.
import numpy as np, json
from PIL import Image
_src=open('/workspace/town-demo/tools/extract.py').read().split('meta={}')[0]
exec(_src)
rgba,fg,_=key('monsters/champions/champ01.jpg')
CELLS=[(0,0),(0,1),(0,2),(0,3),(1,3),(1,2)]   # charge x4, idle, stunned
S=0.8                                         # source -> world scale (boar body ~ 150 px wide in game)
BOX=(-165,-232,165,22)                        # crop around anchor (source px): x0,y0,x1,y1
frames=[]
for r,c in CELLS:
    x0,y0=c*320,r*240; cell=rgba[y0:y0+240,x0:x0+320].copy(); m=fg[y0:y0+240,x0:x0+320]
    rgb=cell[...,:3].astype(int); body=m&(rgb.max(-1)<115)&(rgb.max(-1)>8)   # dark fur/hooves, not tan dust or stars
    body[200:,:]=False
    ys,xs=np.nonzero(body)
    # ignore the far tail of stray dark pixels: robust percentiles
    ax=int(np.percentile(xs,50)); ay=int(np.percentile(ys,99.5))
    m=m.copy(); mag=(rgb[...,0]>rgb[...,1]+35)&(rgb[...,2]>rgb[...,1]+22)&(rgb[...,2]>rgb[...,0]*0.45)
    m&=~mag                                     # dark magenta ground shading left by the key
    lab,n=ndi.label(ndi.binary_dilation(m,iterations=7))   # keep only the boar blob (+attached dust/stars)
    keep=np.bincount(lab[body&m].ravel(),minlength=n+1); keep[0]=0
    m&=lab==keep.argmax()
    edge=m&~ndi.binary_erosion(m,iterations=3)
    r_,g_,b_=rgb[...,0],rgb[...,1],rgb[...,2]
    m&=~(edge&(r_-g_>32)&(b_>g_-6))                # reddish/magenta fringe on the contour
    m=ndi.binary_erosion(m,iterations=1)|(m&~edge)  # 1px clean edge
    big=np.zeros((240+400,320+400,4),np.uint8); big[200:440,200:520]=cell; big[200:440,200:520,3]=m*255
    crop=big[200+ay+BOX[1]:200+ay+BOX[3],200+ax+BOX[0]:200+ax+BOX[2]]
    im=Image.fromarray(crop,'RGBA'); w,h=im.size
    frames.append(im.resize((round(w*S),round(h*S)),Image.NEAREST))
fw,fh=frames[0].size
sheet=Image.new('RGBA',(fw*len(frames),fh),(0,0,0,0))
for i,f in enumerate(frames): sheet.paste(f,(i*fw,0))
sheet.save(OUT+'champ_boar.png')
meta=json.load(open(OUT+'sprites.json'))
meta['champ_boar']=dict(src='champ_boar.png',w=fw,h=fh,n=len(frames),ax=round(-BOX[0]*S),ay=round(-BOX[1]*S),flipNative=True,
                        frames=dict(charge=[0,1,2,3],idle=4,stun=5),headH=round(150*S))
json.dump(meta,open(OUT+'sprites.json','w'),indent=1)
print(fw,fh,meta['champ_boar'])
