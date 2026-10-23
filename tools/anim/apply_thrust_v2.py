# thrust v2: same frames as v1 with the face skin matched to frame 0 (found from the picture, gold trim kept).
# Repaints the hit1/hit2 right+left cells in place (colours only, boxes unchanged). Lunge for the thrusts set to 0/0, finisher 16.
import json,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/';R='/home/user/thor-like-game/handoff/claude/hero_attack_thrust_v2/frames/'
d=json.load(open(T+'assets/anim/hero8.json'));sp='anim/hero8_atk.webp';SHI=d['sheets'].index(sp);sheet=Image.open(T+'assets/'+sp).convert('RGBA')
for h in ['hit1','hit2']:
    for side in ['right','left']:
        for i,(s,c,t) in enumerate(d['anims'][f'{h}_{side}']):
            im=Image.open(R+f'{h}_{i:02d}.png').convert('RGBA')
            if side=='left': im=im.transpose(Image.FLIP_LEFT_RIGHT)
            x,y,w,hh,ax,ay=d['cells'][s][c];crop=im.crop((128-ax,189-ay,128-ax+w,189-ay+hh))
            sheet.paste(Image.new('RGBA',(w,hh)),(x,y));sheet.paste(crop,(x,y))
sheet.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
d['src']['thrust_v2']='thrust v1 frames with matched face skin, repainted in place (tools/anim/apply_thrust_v2.py)'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
assert s.count('H8.lunge=[18,22,32];')==1;s=s.replace('H8.lunge=[18,22,32];','H8.lunge=[0,0,16];')  # the thrust art lunges by itself; code step only on the finisher
open(T+'index.html','w',encoding='utf-8').write(s);print('ok')
