#!/usr/bin/env python3
"""from8x8_v1 assembly: selection.json {motion:{dir:'<cand rel path>' | 'MIRROR:<cand rel path>'}} -> from8x8_v1/<motion>/<dir>/NNN.png,
from8x8_<motion>.gif (south|east|west|north, 2x, gray), from8x8_<motion>_vs_design.png (per dir: design row (8 evenly spaced frames of the old px_ clip) over ours)."""
import os,sys,json,shutil,glob
from PIL import Image,ImageDraw,ImageFont
G='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=G+'/from8x8_v1'; V='/workspace/town-demo/char_v4/pixellab/hero/vid'
SEL=json.load(open(C+'/selection.json'))['selection']; D=['south','east','west','north']; GR=(128,128,128,255); S=2; L=20
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
except Exception: font=ImageFont.load_default()
RIGHT={'idle':'px_idle4_right','walk':'px_walk_side','run':'px_run_side','atk1':'px_atk1','atk2':'px_atk2','atk3':'px_atk3','dash':'px_dash','hurt':'px_hurt_side','cast':'px_cast_side'}
def dsrc(m,d):
    if d in('east','west'): return V+'/'+RIGHT[m],d=='west'
    return V+'/'+(('px_idle4_down' if d=='south' else 'px_idle4_up') if m=='idle' else f'px_{m}_{"front" if d=="south" else "back"}'),False
MS=json.load(open(C+'/selection.json')).get('ms',{})
mot=sys.argv[1:] or list(SEL)
for m in mot:
    F={}
    for d in D:
        src=SEL[m][d]; mir=src.startswith('MIRROR:'); p=C+'/_cand/'+(src[7:] if mir else src)
        od=f'{C}/{m}/{d}'; shutil.rmtree(od,ignore_errors=True); os.makedirs(od); F[d]=[]
        for f in sorted(x for x in os.listdir(p) if x.endswith('.png')):
            im=Image.open(f'{p}/{f}').convert('RGBA')
            if mir: im=im.transpose(Image.FLIP_LEFT_RIGHT)
            im.save(f'{od}/{f}'); F[d].append(im)
    bb=None
    for v in F.values():
        for im in v:
            b=im.getbbox(); bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
    bb=(max(0,bb[0]-4),max(0,bb[1]-4),min(256,bb[2]+4),min(256,bb[3]+4)); cw,ch=bb[2]-bb[0],bb[3]-bb[1]; n=max(len(v) for v in F.values())
    fr=[]
    for i in range(n):
        c=Image.new('RGBA',(4*cw*S,ch*S+L),GR); dr=ImageDraw.Draw(c)
        for k,d in enumerate(D):
            im=F[d][min(i,len(F[d])-1)]; dr.text((k*cw*S+4,2),f'{d} {m} f{i}'+(' (mirror)' if SEL[m][d].startswith('MIRROR:') else ''),fill=(255,255,255,255),font=font)
            c.alpha_composite(im.crop(bb).resize((cw*S,ch*S),Image.NEAREST),(k*cw*S,L))
        fr.append(c.convert('RGB'))
    fr[0].save(f'{C}/from8x8_{m}.gif',save_all=True,append_images=fr[1:],duration=MS.get(m,90),loop=0)
    # vs design
    CS=150; NC=max(8,n); sh=Image.new('RGBA',(110+NC*CS,8*CS),GR); dr=ImageDraw.Draw(sh)
    for r,d in enumerate(D):
        dp,mir=dsrc(m,d); fs=sorted(glob.glob(dp+'/*.png')); k=8
        des=[Image.open(fs[round(j*(len(fs)-1)/(k-1))]).convert('RGBA') for j in range(k)]
        if mir: des=[x.transpose(Image.FLIP_LEFT_RIGHT) for x in des]
        ub=None
        for x in des:
            b=x.getbbox(); ub=b if ub is None else (min(ub[0],b[0]),min(ub[1],b[1]),max(ub[2],b[2]),max(ub[3],b[3]))
        y0=2*r*CS; dr.text((4,y0+60),f'{d}\nDESIGN\n{os.path.basename(dp)}'+('\n(mirrored)' if mir else ''),fill=(255,230,150,255)); dr.text((4,y0+CS+60),f'{d}\nOURS',fill=(150,255,255,255))
        for j,x in enumerate(des):
            x=x.crop(ub); s=min(CS/x.width,CS/x.height); x=x.resize((max(1,int(x.width*s)),max(1,int(x.height*s))),Image.NEAREST)
            sh.alpha_composite(x,(110+j*CS+(CS-x.width)//2,y0+CS-x.height))
        for j,x in enumerate(F[d]):
            x=x.crop(bb); s=min(CS/x.width,CS/x.height); x=x.resize((int(x.width*s),int(x.height*s)),Image.NEAREST)
            sh.alpha_composite(x,(110+j*CS+(CS-x.width)//2,y0+2*CS-x.height))
        dr.line([(0,y0),(sh.width,y0)],fill=(60,60,60,255))
    sh.save(f'{C}/from8x8_{m}_vs_design.png'); print(m,'ok',n)
