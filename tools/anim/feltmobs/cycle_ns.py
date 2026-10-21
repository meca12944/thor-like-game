# Front/back walk cycles (2번방 key-pose method): R, RL1-3, L, LR1-3 from key poses + animate-with-text-v3 in-betweens.
# Every frame is cleaned, scaled about the feet so the body height matches the side walk (in-betweens come out ~5% bigger),
# passing frames 1-2px taller, then placed on the side strips' canvas (256px, feet y 250, centred).
# usage: cycle_ns.py <ns dir> <pl dir>   (ns dir: tw/<src>_<d>_RL|LR/f_00..04.png; pl dir: <mid>_walk.png side strips -> <mid>_walk_s/_n.png)
import sys,glob,math,numpy as np
from PIL import Image
from assemble_lib import clean
N,O=sys.argv[1:3]
MUL={'needle_spider':1.25,'stone_hound':1.3,'thread_wraith':.8}   # long, low side views stand taller from the front; the wraith's side bbox includes a stray thread
MOBS=[('thread_wraith','c1_01_silmamul'),('thread_puppet','c1_02_thread_puppet'),('needle_spider','c1_03_needle_spider'),('stone_hound','c1_04_unrotting_hound')]
def bbox(im):return im.getbbox()
for src,mid in MOBS:
    side=Image.open(f'{O}/{mid}_walk.png');sh=np.mean([bbox(side.crop((i*256,0,i*256+256,256)))[3]-bbox(side.crop((i*256,0,i*256+256,256)))[1] for i in range(8)])
    k0=None   # scale found for the front view; the back view uses it too (its silhouette can be lower than the front's)
    for d,tag in (('south','s'),('north','n')):
        RL=sorted(glob.glob(f'{N}/tw/{src}_{d}_RL/f_*.png'));LR=sorted(glob.glob(f'{N}/tw/{src}_{d}_LR/f_*.png'))
        seq=[clean(Image.open(f)) for f in RL[:4]+LR[:4]]
        keyH=(bbox(seq[0])[3]-bbox(seq[0])[1]+bbox(seq[4])[3]-bbox(seq[4])[1])/2;st=Image.new('RGBA',(256*8,256))
        for i,im in enumerate(seq):
            b=bbox(im);h=b[3]-b[1];ph=i%4;k0=k0 or sh*MUL.get(src,1)/keyH;target=keyH*k0*(1+(0.012*math.sin(math.pi*ph/4) if ph else 0))
            s=target/h;fr=im.crop(b);fr=fr.resize((max(1,round(fr.width*s)),max(1,round(fr.height*s))),Image.NEAREST)
            st.paste(fr,(i*256+128-fr.width//2,250-fr.height),fr)
        st.save(f'{O}/{mid}_walk_{tag}.png');print(mid,d,'side h',round(sh),'key h',round(keyH))
