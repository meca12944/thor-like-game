#!/usr/bin/env python3
"""Extract run_v1 frames from character_after / job results, build run_8dir.gif + run_8dir_frames.png. No key needed."""
import json, os, io, base64, urllib.request
from PIL import Image, ImageDraw
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/run_v1'
DIRS=['south','south-east','east','north-east','north','north-west','west','south-west']
GID=json.load(open(A+'/_raw/jobs.json'))['animation_group_id']
def load(x):
    if isinstance(x,dict):
        if x.get('url'): x=x['url']
        elif x.get('base64'): return Image.open(io.BytesIO(base64.b64decode(x['base64']))).convert('RGBA')
    if isinstance(x,str):
        if x.startswith('http'):
            return Image.open(io.BytesIO(urllib.request.urlopen(x,timeout=60).read())).convert('RGBA')
        return Image.open(io.BytesIO(base64.b64decode(x.split(',')[-1]))).convert('RGBA')
def frames_for(d):
    ch=json.load(open(A+'/_raw/character_after.json'))
    ch=ch.get('body',ch)
    for an in ch.get('animations',[]):
        if str(an.get('animation_group_id',an.get('id')))!=GID and an.get('name')!='run_v1_running8': continue
        if an.get('direction')==d or an.get('directions')==[d]:
            fr=an.get('frames') or an.get('frame_urls') or []
            if fr: return [load(f) for f in fr]
        fu=an.get('frame_urls') or an.get('frames')
        if isinstance(fu,dict) and d in fu: return [load(f) for f in fu[d]]
    j=json.load(open(A+f'/_raw/job_{d}.json')); lr=j.get('last_response') or j.get('result') or {}
    for k in ('images','frames'):
        v=lr.get(k)
        if isinstance(v,dict) and d in v: v=v[d]
        if v: return [load(f) for f in v]
    raise SystemExit(f'no frames for {d}')
F={}
for d in DIRS:
    F[d]=frames_for(d); os.makedirs(f'{A}/{d}',exist_ok=True)
    for i,im in enumerate(F[d]): im.save(f'{A}/{d}/{i:03d}.png')
    print(d,len(F[d]),F[d][0].size)
n=max(len(v) for v in F.values()); W,H=F['south'][0].size
# crop to union bbox across all frames for compactness
bb=None
for v in F.values():
    for im in v:
        b=im.getbbox()
        if b: bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
pad=6; bb=(max(0,bb[0]-pad),max(0,bb[1]-pad),min(W,bb[2]+pad),min(H,bb[3]+pad)); cw,chh=(bb[2]-bb[0])*2,(bb[3]-bb[1])*2
LAB=16; GAP=6; G=(128,128,128,255)
def cell(im): return im.crop(bb).resize((cw,chh),Image.NEAREST)
gif=[]
for f in range(n):
    c=Image.new('RGBA',(4*cw+5*GAP,2*(chh+LAB)+3*GAP),G); dr=ImageDraw.Draw(c)
    for k,d in enumerate(DIRS):
        x=GAP+(k%4)*(cw+GAP); y=GAP+(k//4)*(chh+LAB+GAP)
        dr.text((x+3,y+2),d,fill=(255,255,255)); v=F[d]; c.alpha_composite(cell(v[f%len(v)]),(x,y+LAB))
    gif.append(c.convert('RGB'))
gif[0].save(A+'/run_8dir.gif',save_all=True,append_images=gif[1:],duration=75,loop=0,disposal=1,optimize=False)
# contact sheet: rows=dirs, cols=frames + idle ref
idle={d:Image.open(f'{O}/v1_1x_descA/{d}.png').convert('RGBA') for d in DIRS}
sw=90; s=Image.new('RGBA',(sw+(n+1)*(cw+GAP)+GAP,LAB+len(DIRS)*(chh+GAP)+GAP),G); dr=ImageDraw.Draw(s)
dr.text((sw+GAP+3,2),'idle',fill=(255,255,0))
for f in range(n): dr.text((sw+GAP+(f+1)*(cw+GAP)+3,2),f'{f:03d}',fill=(255,255,255))
for r,d in enumerate(DIRS):
    y=LAB+r*(chh+GAP); dr.text((4,y+chh//2),d,fill=(255,255,255))
    s.alpha_composite(cell(idle[d]),(sw+GAP,y))
    for f,im in enumerate(F[d]): s.alpha_composite(cell(im),(sw+GAP+(f+1)*(cw+GAP),y))
s.save(A+'/run_8dir_frames.png'); print('gif',gif[0].size,n,'frames; sheet',s.size)
