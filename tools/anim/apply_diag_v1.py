# hero up/down -> diagonal (owner 2026-10-20: "상하 모션을 대각선으로 대체하고 상하 모션을 없애"). Source = hero_sandbox v5 atlas
# (handoff/claude/hero_sandbox_v5/assets): *_down = 3/4 south-east, *_up = 3/4 north-east for idle/walk/run/dash/jump/hit1-3;
# the game mirrors them for south-west / north-west (heroCell8, H8.diag). Hurt/death/cast/hold/rec have no up/down art any more:
# while facing up/down they use the side clip of the horizontal facing. Cells go to a new sheet anim/hero8_diag.webp.
import json
from PIL import Image
T='/home/user/thor-like-game/test128/';S='/home/user/thor-like-game/handoff/claude/hero_sandbox_v5/assets/'
d=json.load(open(T+'assets/anim/hero8.json'));s=json.load(open(S+'hero_sbx.json'))
ssh=[Image.open(S+p).convert('RGBA') for p in s['sheets']]
NAMES=['idle','walk','run','dash','jump','hit1','hit2','hit3']
crops=[];keymap={}
for n in NAMES:
    for dr in ['down','up']:
        for e in s['anims'][f'{n}_{dr}']:
            k=(e[0],e[1])
            if k not in keymap:x,y,w,h,ax,ay=s['cells'][e[0]][e[1]];keymap[k]=len(crops);crops.append((ssh[e[0]].crop((x,y,x+w,y+h)),ax,ay))
W=2048;x=0;y=0;rowh=0;pos=[]
for im,ax,ay in crops:
    if x+im.width>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=im.width+1;rowh=max(rowh,im.height)
sheet=Image.new('RGBA',(W,y+rowh))
for (im,ax,ay),(px,py) in zip(crops,pos):sheet.paste(im,(px,py))
sp='anim/hero8_diag.webp'
if sp not in d['sheets']:d['sheets'].append(sp);d['cells'].append([])
SHI=d['sheets'].index(sp);d['cells'][SHI]=[[px,py,im.width,im.height,int(ax),int(ay)] for (im,ax,ay),(px,py) in zip(crops,pos)]
sheet.save(T+'assets/'+sp,'WEBP',lossless=True,quality=100,method=6)
for n in NAMES:
    for dr in ['down','up']:
        L=[[SHI,keymap[(e[0],e[1])],e[2]] for e in s['anims'][f'{n}_{dr}']]
        if n=='dash':  # game dodge = 17 ticks
            tot=sum(e[2] for e in L);acc=0;out=[]
            for e in L:nt=round((acc+e[2])*17/tot)-round(acc*17/tot);acc+=e[2];out.append([e[0],e[1],max(1,nt)])
            L=out
        d['anims'][f'{n}_{dr}']=L
for k in [k for k in d['anims'] if (k.endswith('_down') or k.endswith('_up')) and k.rsplit('_',1)[0] not in NAMES]:del d['anims'][k]
d['diag']=1
d['src']['diag_v1']='*_down/_up = 3/4 SE/NE (tools/anim/apply_diag_v1.py from hero_sandbox v5); SW/NW mirrored in code; other clips side-only'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s2=open(T+'index.html',encoding='utf-8').read();a=s2.index("/*H8*/const H8=");b=s2.index(";/*/H8*/");pre=s2[a:b];k=pre.index('?null:')+6;s2=s2[:a]+pre[:k]+js+s2[b:]
open(T+'index.html','w',encoding='utf-8').write(s2);print('ok',sheet.size,len(crops),sorted(k for k in d['anims'] if k.endswith('_down')))
