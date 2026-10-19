import json,os
from PIL import Image
G='/home/user/thor-like-game/test128/assets/';h=json.load(open(G+'anim/hero8.json'))
sh={};man={}
for a in ['walk','idle','hurt','hit1','hit2','hit3']:
    for dr in ['down','up','right']:
        n=f'{a}_{dr}';os.makedirs(f'all/{n}',exist_ok=True);man[n]=[]
        for i,f in enumerate(h['anims'][n]):
            s,c,t=f[:3]
            if s not in sh: sh[s]=Image.open(G+h['sheets'][s]).convert('RGBA')
            x,y,w,hh,ax,ay=h['cells'][s][c];o=Image.new('RGBA',(256,256));im=sh[s].crop((x,y,x+w,y+hh));o.paste(im,(128-ax,189-ay),im)
            o.save(f'all/{n}/k{i}.png');man[n].append(t)
json.dump(man,open('all/manifest.json','w'));print(sum(len(v) for v in man.values()))
