# Import room-3 idle/attack strips (art/mobs/idle on claude/attack3: 42 new + 5 field mobs) into test128.
# Writes test128/assets/mobs47/<id>_idle.webp, <id>_atk.webp (lossless) and mobs47.json:
#   {id: {idle:{w,h,n,foot}, atk:{w,h,n,foot,ticks,hit}, body:<content height px>, ram:bool}}
# Art that faces left is mirrored so every strip faces right; those mobs (and the 5 field mobs, whose attack is a
# body ram on the idle pose) get ram=true: the game lunges the idle frame in code instead of playing the attack strip.
# usage: import.py <art/mobs/idle dir> <test128 dir>
import sys,os,json,numpy as np
from PIL import Image
S,G=sys.argv[1:3];O=f'{G}/assets/mobs47';os.makedirs(O,exist_ok=True)
MIRROR={'a2_06_glow_worm','a3_07_camel_tortoise','a5_07_anglerfish','a5_08_hermit_crab','field_boar','field_horned_rabbit','field_wasp'}
M={m['id']:m for m in json.load(open(f'{S}/manifest.json'))};A={a['id']:a for a in json.load(open(f'{S}/atk_manifest.json'))}
def flip(im,w,n):
    out=Image.new('RGBA',im.size)
    for i in range(n):out.paste(im.crop((i*w,0,(i+1)*w,im.height)).transpose(Image.FLIP_LEFT_RIGHT),(i*w,0))
    return out
OUT={}
for i,m in M.items():
    idl=Image.open(f'{S}/sheets/{i}.png').convert('RGBA');atk=Image.open(f'{S}/atk/{i}.png').convert('RGBA');a=A[i]
    mir=i in MIRROR
    if mir:idl=flip(idl,m['w'],m['n']);atk=flip(atk,a['w'],a['n'])
    al=np.array(idl.crop((0,0,m['w'],m['h'])))[...,3];ys=np.nonzero(al.max(1)>0)[0];foot=m['h']-12
    idl.save(f'{O}/{i}_idle.webp',lossless=True,quality=100,method=6)
    ram=mir or i.startswith('field_')
    if not ram:atk.save(f'{O}/{i}_atk.webp',lossless=True,quality=100,method=6)
    OUT[i]={'name':m['name'].split(' (')[0],'idle':{'w':m['w'],'h':m['h'],'n':m['n'],'foot':foot},'body':int(foot-ys[0]),'ram':ram}
    if not ram:OUT[i]['atk']={k:a[k] for k in('w','h','n','foot','ticks','hit')}
json.dump(OUT,open(f'{O}/mobs47.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(OUT),sum(os.path.getsize(f'{O}/{f}') for f in os.listdir(O))//1024,'KB')
