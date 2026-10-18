# combo3_thin raw fx -> px_combo3ref_* (retimed order, body frames untouched) + before/after gif
import json,os,shutil,numpy as np
from PIL import Image,ImageDraw
VID='/workspace/town-demo/char_v4/pixellab/hero/vid'; V3=VID+'/v3'; PV=V3+'/preview'; CW,CH=304,256
J=json.load(open(V3+'/combo3_ref.json'))['combos']; BK=V3+'/_backup_combo3ref_fx_pre_thin'
for d,C in J.items():
    src=f'{VID}/px_combo3ref_{d}'; b=f'{BK}/{d}'
    if not os.path.isdir(b):
        os.makedirs(b); [shutil.copy(f'{src}/fx_{n:03d}.png',b) for n in range(len(C['frames']))]
    for n,f in enumerate(C['frames']): shutil.copy(f"{VID}/px_combo3thinraw_{d}/fx_{f['src_arc_frame']:03d}.png",f'{src}/fx_{n:03d}.png')
def comp(d,n,fxd):
    im=Image.new('RGBA',(CW,CH),(150,170,140,255)); im.alpha_composite(Image.open(f'{VID}/px_combo3ref_{d}/{n:03d}.png')); im.alpha_composite(Image.open(f'{fxd}/fx_{n:03d}.png')); return im.convert('RGB')
tl={d:np.repeat(np.arange(len(C['ticks'])),C['ticks']) for d,C in J.items()}; G=[]
T=max(len(v) for v in tl.values())
for tk in range(T):
    S=Image.new('RGB',(CW*4,(CH+14)*2),(150,170,140)); dr=ImageDraw.Draw(S)
    for i,d in enumerate(['down','up','right','left']):
        n=tl[d][min(tk,len(tl[d])-1)]; S.paste(comp(d,n,f'{BK}/{d}'),(i*CW,14)); S.paste(comp(d,n,f'{VID}/px_combo3ref_{d}'),(i*CW,CH+28))
        dr.text((i*CW+4,2),f'before {d} t{tk}',fill=0); dr.text((i*CW+4,CH+16),f'thin {d}',fill=0)
    G.append(S)
G[0].save(f'{PV}/combo3_ref_vs_thin_4dir.gif',save_all=True,append_images=G[1:],duration=[33]*(len(G)-1)+[600],loop=0)
G[20].save('/tmp/sf/thin20.png'); G[42].save('/tmp/sf/thin42.png'); print('ok',len(G))
