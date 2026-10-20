# hit3 (motion unchanged): face skin matched to hit1 frame 0's skin ramp (found from the picture, gold trim kept). Repaints right+left cells in place.
import json,sys,numpy as np
from PIL import Image
sys.path.insert(0,'/home/user/thor-like-game/tools/anim');import skin_match as SK
T='/home/user/thor-like-game/test128/';ref=SK.ref_ramp(Image.open('/home/user/thor-like-game/handoff/claude/hero_attack_thrust_v2/frames/hit1_00.png'))
d=json.load(open(T+'assets/anim/hero8.json'));sheets={}
for side in ['right','left']:
    for s,c,t,*_ in d['anims'][f'hit3_{side}']:
        if s not in sheets: sheets[s]=Image.open(T+'assets/'+d['sheets'][s]).convert('RGBA')
        x,y,w,h,ax,ay=d['cells'][s][c];crop=sheets[s].crop((x,y,x+w,y+h));o=Image.new('RGBA',(256,256));o.paste(crop,(128-ax,189-ay))
        f=SK.fix_face3(o,ref).crop((128-ax,189-ay,128-ax+w,189-ay+h));sheets[s].paste(Image.new('RGBA',(w,h)),(x,y));sheets[s].paste(f,(x,y))
for s,im in sheets.items(): im.save(T+'assets/'+d['sheets'][s],'WEBP',lossless=True,quality=100,method=6)
print('ok',list(sheets))
