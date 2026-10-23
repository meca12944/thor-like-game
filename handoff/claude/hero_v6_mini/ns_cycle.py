# copied from handoff/claude/linette_ns_keys_v1/cycle_ns.py (Linette room), reads ns/tw_<motion>_RL|LR
# Build an 8-frame walk/run cycle from two key poses + their in-betweens (tw_<d>_RL, tw_<d>_LR from tween.py):
# R, RL1, RL2, RL3, L, LR1, LR2, LR3. In-betweens are re-scaled about the feet so the body height matches the keys
# (animate-with-text-v3 draws the middle frames ~5% bigger; the two key edits can differ too), with a small natural rise at the passing frames.
# usage: cycle_ns.py <d> <outdir> [rise_px=2]
import sys,glob,os,math
from PIL import Image
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ns');d,out=sys.argv[1],sys.argv[2];RISE=float(sys.argv[3]) if len(sys.argv)>3 else 2
RL=sorted(glob.glob(f'{D}/tw_{d}_RL/*.png'));LR=sorted(glob.glob(f'{D}/tw_{d}_LR/*.png'))
seq=[RL[0],RL[1],RL[2],RL[3],LR[0],LR[1],LR[2],LR[3]]
def h(im):b=im.getbbox();return b[3]-b[1],b
keyH=(h(Image.open(RL[0]).convert('RGBA'))[0]+h(Image.open(LR[0]).convert('RGBA'))[0])/2
os.makedirs(out,exist_ok=True)
for i,f in enumerate(seq):
    im=Image.open(f).convert('RGBA');hh,b=h(im);ph=i%4
    target=keyH+(RISE*math.sin(math.pi*ph/4) if ph else 0)   # passing frames a touch taller (body rises)
    if abs(target-hh)>0.5:   # every frame (keys too: two edits can come out a few % apart)
        s=target/hh;w2,h2=round(256*s),round(256*s);cx=(b[0]+b[2])/2;fy=b[3]
        im2=im.resize((w2,h2),Image.NEAREST);c=Image.new('RGBA',(256,256));c.paste(im2,(round(cx-cx*s),round(fy-fy*s)),im2);im=c
    im.save(f'{out}/{i:03d}.png')
    print(i,os.path.relpath(f,D),'h',hh,'->',h(im)[0])
