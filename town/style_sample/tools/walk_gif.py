import json
from PIL import Image, ImageDraw, ImageFont
S='/workspace/town-demo/style_sample/'; meta=json.load(open(S+'assets/walk_meta.json'))
F=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf',16)
from build_fem import NAMES
order=['a_tailor','h_mystic','g_dancer','f_diver','e_tailor','c_priest','d_yuna','g_tool']; K=3
m0=meta[order[0]]; cw,ch=m0['cw'],m0['ch']; W=cw*K*len(order); H=ch*K*4+60
sheets={n:Image.open(S+f'assets/walk_{n}.png') for n in order}
frames=[]
for t in range(16):   # 16 frames @ 75 ms: walk 8 frames shown at 150 ms each (= 9 ticks @60fps), idle not shown
    im=Image.new('RGB',(W,H),(96,118,84)); d=ImageDraw.Draw(im)
    for i,n in enumerate(order):
        d.text((i*cw*K+cw*K//2-30,6),NAMES[n].split(' ')[0],font=F,fill=(255,240,200))
        for r in range(4):
            fi=meta[n]['walk'][0]+(t//2)%8
            c=sheets[n].crop((fi*cw,r*ch,(fi+1)*cw,(r+1)*ch)).resize((cw*K,ch*K),Image.NEAREST)
            im.paste(c,(i*cw*K,30+r*ch*K),c)
    frames.append(im)
frames[0].save(S+'heroines_walk_4dir.gif',save_all=True,append_images=frames[1:],duration=75,loop=0,optimize=True)
print(W,H)
