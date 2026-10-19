#!/usr/bin/env python3
"""chain_v1: build continuous combo from hit clips + PixelLab transitions (spec in chain_v1/chain_spec.json).
Writes chain_v1/<dir>/NNN.png (west = mirror of east), botw_chain_<dir>.gif, botw_chain_4dir.gif (2x, gray, hitstop holds)."""
import os,json,shutil
from PIL import Image,ImageDraw,ImageFont
B='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/botw_basic_v1'; C=B+'/chain_v1'
SPEC=json.load(open(C+'/chain_spec.json')); D=['south','east','west','north']; G=(128,128,128,255); S=2; L=20
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
except Exception: font=ImageFont.load_default()
def smear(im):
    return sum(1 for r,g,b,a in im.get_flattened_data() if a>128 and b>180 and g>170 and (b-r>40 or (r>225 and g>225 and b>225)))
def segs(d):
    src='east' if d=='west' else d; out=[]
    for seg in SPEC[src]:
        p=seg['src'] if seg['src'].startswith('chain_v1') else seg['src']
        ims=[Image.open(f'{B}/{p}/{i:03d}.png').convert('RGBA') for i in seg['frames']]
        if d=='west': ims=[im.transpose(Image.FLIP_LEFT_RIGHT) for im in ims]
        kind=seg['kind']; imp=max(range(len(ims)),key=lambda i:smear(ims[i])) if kind=='hit' else -1
        out.append((kind,seg['label'],ims,imp))
    return out
ALL={d:segs(d) for d in D}
bb=None
for v in ALL.values():
    for _,_,ims,_ in v:
        for im in ims:
            b=im.getbbox(); bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
bb=(max(0,bb[0]-4),max(0,bb[1]-4),min(256,bb[2]+4),min(256,bb[3]+4)); cw,ch=bb[2]-bb[0],bb[3]-bb[1]
def dur(kind,i,imp): return 170 if (kind=='hit' and i==imp) else (60 if kind!='hit' else 80)
def big(im): return im.crop(bb).resize((cw*S,ch*S),Image.NEAREST)
for d in D:
    od=f'{C}/{d}'; shutil.rmtree(od,ignore_errors=True); os.makedirs(od)
    fr=[];du=[];n=0
    for kind,lab,ims,imp in ALL[d]:
        for i,im in enumerate(ims):
            im.save(f'{od}/{n:03d}.png'); n+=1
            c=Image.new('RGBA',(cw*S,ch*S+L),G); ImageDraw.Draw(c).text((4,2),f'{d} {lab} {i}',fill=(255,255,255,255),font=font)
            c.alpha_composite(big(im),(0,L)); fr.append(c.convert('RGB')); du.append(dur(kind,i,imp))
    du[-1]=450; fr[0].save(f'{C}/botw_chain_{d}.gif',save_all=True,append_images=fr[1:],duration=du,loop=0)
nseg=len(ALL['south']); fr=[];du=[]
for s in range(nseg):
    n=max(len(ALL[d][s][2]) for d in D)
    for i in range(n):
        c=Image.new('RGBA',(4*cw*S,ch*S+L),G); dr=ImageDraw.Draw(c); ds=[]
        for k,d in enumerate(D):
            kind,lab,ims,imp=ALL[d][s]; j=min(i,len(ims)-1)
            dr.text((k*cw*S+4,2),f'{d} {lab}',fill=(255,255,255,255),font=font); c.alpha_composite(big(ims[j]),(k*cw*S,L))
            ds.append(dur(kind,j,imp) if i<len(ims) else 0)
        fr.append(c.convert('RGB')); kind=ALL['south'][s][0]
        du.append(170 if 170 in ds else (60 if kind!='hit' else 80))
du[-1]=450; fr[0].save(f'{C}/botw_chain_4dir.gif',save_all=True,append_images=fr[1:],duration=du,loop=0)
print('ok',bb,{d:sum(len(x[2]) for x in ALL[d]) for d in D})
