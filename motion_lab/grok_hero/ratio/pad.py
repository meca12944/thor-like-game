# 어깨 보호대(청동 둥근 판) = 자세가 바뀌어도 모양이 그대로인 단단한 물건 → 크기 자로 씀. 가장 큰 청동 덩어리 2개의 높이·폭
import json,glob,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
from measure_ratio import CLIPS
def pads(f):
    A=np.array(Image.open(f).convert('RGBA')).astype(int);r,g,b,a=[A[...,i] for i in range(4)]
    m=(a>0)&(r-b>28)&(r>=g)&(g>=b)&(r>70)&~((r>135)&(r-g<70)&(g-b>2))
    top=int(np.nonzero(a.any(1))[0].min());m[top+int(.5*(189-top)):]=0
    m=ndimage.binary_closing(m,iterations=2);L,n=ndimage.label(m);sl=ndimage.find_objects(L);sz=np.bincount(L.ravel())
    c=sorted([(sz[i+1],s) for i,s in enumerate(sl)],key=lambda t:-t[0])[:2]
    return [(int(s[0].start),int(s[1].start),int(s[0].stop),int(s[1].stop),int(z)) for z,s in c if z>=40]
R={}
for k,d in CLIPS.items():
    R[k]=[pads(f) for f in sorted(glob.glob(d+'/*.png'))[:8]]
    hs=[max(p[2]-p[0] for p in ps) for ps in R[k] if ps];ws=[max(p[3]-p[1] for p in ps) for ps in R[k] if ps]
    print(f'{k:14s} 보호대 높이 {np.median(hs) if hs else "-"} 폭 {np.median(ws) if ws else "-"}  ({len(hs)}장)')
json.dump(R,open('pads.json','w'))
# 확인 그림: 각 묶음 첫 장
ks=list(CLIPS);S=2;W=Image.new('RGB',(176*S*6,200*S*2),(70,74,80));d=ImageDraw.Draw(W)
for i,k in enumerate(ks):
    f=sorted(glob.glob(CLIPS[k]+'/*.png'))[0];im=Image.open(f).convert('RGBA').crop((40,0,216,200)).resize((176*S,200*S),Image.NEAREST);ox,oy=(i%6)*176*S,(i//6)*200*S
    W.paste(im,(ox,oy),im)
    for y0,x0,y1,x1,_ in R[k][0]: d.rectangle([ox+(x0-40)*S,oy+y0*S,ox+(x1-40)*S,oy+y1*S],outline=(0,255,0),width=2)
    d.text((ox+4,oy+4),k,fill=(255,255,255))
W.save('pads.png')
