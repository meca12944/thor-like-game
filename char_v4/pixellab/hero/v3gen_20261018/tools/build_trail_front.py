#!/usr/bin/env python3
"""trail_front_v1 assembly. selection.json maps 'hit<h>/<dir>/<NNN>' -> cand png (PixelLab edit output). Frames not listed = original combo3_final.
Body lock (automatic, no hand pixels): result = original frame, except inside the trail zone (original-trail mask OR edited-trail mask, dilated 3px)
where the PixelLab edit pixels are used. So body/sword/timing stay identical; only the trail area takes the edit. west = mirror of east (as in combo3_final).
Writes trail_front_v1/hit<h>/<dir>/NNN.png, trail_front_<dir>_before_after.gif, trail_front_4dir.gif."""
import os,json,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
G='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=G+'/trail_front_v1'; SRC=G+'/combo3_final'
SEL=json.load(open(C+'/selection.json'))['selection']; REPL=json.load(open(C+'/selection.json')).get('replace',{}); LOCK=json.load(open(C+'/selection.json')).get('body_lock',True)
D=['south','east','west','north']; GR=(128,128,128,255); S=2; L=20
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
except Exception: font=ImageFont.load_default()
def trail(a): return (a[...,3]>60)&(a[...,:3].sum(-1)>600)
def merged(orig,ed):
    a=np.asarray(orig).copy(); b=np.asarray(ed)
    if not LOCK: return ed
    z=trail(a)|trail(b); z=np.asarray(Image.fromarray((z*255).astype('uint8')).filter(ImageFilter.MaxFilter(7)))>0
    a[z]=b[z]; return Image.fromarray(a)
# timing like the game (hero_v4_atlas combo_ticks): hit1 dur14 hit@5, hit2 dur18 hit@6, hit3 dur27 hit@9 (60fps ticks), 0.75x speed not applied
CONTACT={'hit1':{'south':4,'north':3,'east':4,'west':4},'hit2':{'south':3,'north':3,'east':4,'west':4},'hit3':{'south':5,'north':3,'east':4,'west':4}}
CMB={'hit1':(14,5),'hit2':(18,6),'hit3':(27,9)}
def even(n,k): b=[n//k]*k; [b.__setitem__(i,b[i]+1) for i in range(n%k)]; return b
def ticks(h,d): dur,hit=CMB[h]; c=CONTACT[h][d]; return even(hit,c)+even(dur-hit,8-c)
before={};after={}
for h in ('hit1','hit2','hit3'):
    for d in D:
        sd='east' if d=='west' else d; od=f'{C}/{h}/{d}'; os.makedirs(od,exist_ok=True)
        for i in range(8):
            o=Image.open(f'{SRC}/{h}/{d}/{i:03d}.png').convert('RGBA'); k=f'{h}/{sd}/{i:03d}'
            if k in REPL: n=Image.open(C+'/'+REPL[k]).convert('RGBA')   # full PixelLab edit (pose changed: no body lock)
            elif k in SEL:
                oe=Image.open(f'{SRC}/{h}/{sd}/{i:03d}.png').convert('RGBA'); n=merged(oe,Image.open(C+'/'+SEL[k]).convert('RGBA'))
                if d=='west': n=n.transpose(Image.FLIP_LEFT_RIGHT)
            else: n=o
            n.save(f'{od}/{i:03d}.png'); before[(h,d,i)]=o; after[(h,d,i)]=n
bb=None
for im in list(before.values())+list(after.values()):
    b=im.getbbox(); bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
bb=(max(0,bb[0]-4),max(0,bb[1]-4),min(256,bb[2]+4),min(256,bb[3]+4)); cw,ch=bb[2]-bb[0],bb[3]-bb[1]
def big(im): return im.crop(bb).resize((cw*S,ch*S),Image.NEAREST)
TMS=1000/60/0.75*0+1000/60   # ms per tick at 60fps
def seq(d):
    out=[]
    for h in ('hit1','hit2','hit3'):
        t=ticks(h,d)
        for i in range(8): out.append((h,i,max(40,round(t[i]*TMS*2))))   # 2x slower than game for readability
    return out
for d in D:
    fr=[];du=[]
    for h,i,ms in seq(d):
        c=Image.new('RGBA',(2*cw*S,ch*S+L),GR); dr=ImageDraw.Draw(c)
        dr.text((4,2),f'{d} BEFORE {h} f{i}',fill=(255,200,200,255),font=font); dr.text((cw*S+4,2),f'{d} AFTER {h} f{i}',fill=(200,255,255,255),font=font)
        c.alpha_composite(big(before[(h,d,i)]),(0,L)); c.alpha_composite(big(after[(h,d,i)]),(cw*S,L)); fr.append(c.convert('RGB')); du.append(ms)
    du[-1]=500; fr[0].save(f'{C}/trail_front_{d}_before_after.gif',save_all=True,append_images=fr[1:],duration=du,loop=0)
fr=[];du=[]
for k,(h,i,ms) in enumerate(seq('south')):
    c=Image.new('RGBA',(4*cw*S,ch*S+L),GR); dr=ImageDraw.Draw(c)
    for j,d in enumerate(D):
        dr.text((j*cw*S+4,2),f'{d} {h} f{i}',fill=(255,255,255,255),font=font); c.alpha_composite(big(after[(h,d,i)]),(j*cw*S,L))
    fr.append(c.convert('RGB')); du.append(max(ms,max(m for hh,ii,m in [seq(d)[k] for d in D])))
du[-1]=500; fr[0].save(f'{C}/trail_front_4dir.gif',save_all=True,append_images=fr[1:],duration=du,loop=0)
print('ok',bb)
