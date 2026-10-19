#!/usr/bin/env python3
"""combo3 GIFs/sheets. usage: gif_combo3.py main | compare"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont
O=os.environ.get('C3','/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/combo3_v1')
D=['south','east','north','west']; G=(128,128,128,255); S=2; L=18
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
except Exception: font=ImageFont.load_default()
def seq(root,d):
    out=[]
    for h in (1,2,3):
        p=f'{root}/hit{h}/{d}'; out+= [Image.open(f'{p}/{f}').convert('RGBA') for f in sorted(os.listdir(p)) if f.endswith('.png')]
    return out
def impacts():
    m=json.load(open(O+'/trailA/trailA_meta.json')); res=[]
    for h in (1,2,3):
        ks=[]
        for d in D:
            a=m[f'hit{h}/{d}']['arc_px']; ks.append(max(range(len(a)),key=lambda i:a[i]))
        res.append((h-1)*8+sorted(ks)[len(ks)//2])
    return res
def ubox(seqs):
    bb=None
    for v in seqs:
        for im in v:
            b=im.getbbox()
            if b: bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
    p=6; W,H=seqs[0][0].size; return (max(0,bb[0]-p),max(0,bb[1]-p),min(W,bb[2]+p),min(H,bb[3]+p))
def save_gif(frames,path,imp):
    dur=[160 if i in imp else 80 for i in range(len(frames))]
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=2)
mode=sys.argv[1]; imp=impacts()
if mode=='main':
    fr={d:seq(O,d) for d in D}; bb=ubox(list(fr.values())); cw,ch=bb[2]-bb[0],bb[3]-bb[1]; n=len(fr['south'])
    gifs=[]
    for i in range(n):
        c=Image.new('RGBA',(2*cw*S,2*(ch*S+L)),G); dr=ImageDraw.Draw(c)
        for k,d in enumerate(D):
            x,y=(k%2)*cw*S,(k//2)*(ch*S+L); dr.text((x+4,y+2),f'{d}  hit{i//8+1} f{i%8}',fill=(255,255,255,255),font=font)
            c.alpha_composite(fr[d][i].crop(bb).resize((cw*S,ch*S),Image.NEAREST),(x,y+L))
        gifs.append(c.convert('RGB'))
    save_gif(gifs,O+'/'+os.path.basename(O).replace('combo3_v1','combo3')+'_4dir.gif',imp)
    LW=90; sh=Image.new('RGBA',(LW+n*cw,4*ch+16),G); dr=ImageDraw.Draw(sh)
    for i in range(n): dr.text((LW+i*cw+4,2),f'h{i//8+1}.{i%8}'+('*' if i in imp else ''),fill=(255,255,255,255),font=font)
    for r,d in enumerate(D):
        dr.text((4,16+r*ch+ch//2-7),d,fill=(255,255,255,255),font=font)
        for i,im in enumerate(fr[d]):
            sh.alpha_composite(im.crop(bb),(LW+i*cw,16+r*ch))
            if i%8==0 and i: dr.line([(LW+i*cw,16),(LW+i*cw,16+4*ch)],fill=(255,220,0,255),width=1)
    sh.save(O+'/'+os.path.basename(O).replace('combo3_v1','combo3')+'_4dir_frames.png'); print('main ok',n,bb,'impact',imp)
else:
    fa={d:seq(O+'/trailA',d) for d in D}; fb={d:seq(O+'/trailB',d) for d in D}
    bb=ubox(list(fa.values())+list(fb.values())); cw,ch=bb[2]-bb[0],bb[3]-bb[1]; n=len(fa['south'])
    gifs=[]
    for i in range(n):
        c=Image.new('RGBA',(4*cw*S,2*(ch*S+L)),G); dr=ImageDraw.Draw(c)
        for k,d in enumerate(D):
            for j,(tag,f) in enumerate([('A ours',fa),('B PixelLab',fb)]):
                x,y=((k%2)*2+j)*cw*S,(k//2)*(ch*S+L); dr.text((x+4,y+2),f'{d} {tag} h{i//8+1}',fill=(255,255,255,255),font=font)
                c.alpha_composite(f[d][min(i,len(f[d])-1)].crop(bb).resize((cw*S,ch*S),Image.NEAREST),(x,y+L))
            dr.line([((k%2)*2*cw*S,0),((k%2)*2*cw*S,c.height)],fill=(60,60,60,255),width=2)
        gifs.append(c.convert('RGB'))
    save_gif(gifs,O+'/combo3_trail_compare.gif',imp); print('compare ok',n,bb)
