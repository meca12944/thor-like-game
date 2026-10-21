# One full 8-frame cycle drawn by animate-with-text-v3 from a key back to the same key (tw8_<d>, 9 frames, last = first):
# frames 0-7, each re-scaled about the feet to the key's height (the model draws middle frames a few % bigger). usage: cycle8.py <d> <out>
# (used for the diagonal runs: their near/far key edits came out as the same pose, so key->key halves held a whole stride each)
import sys,glob,os
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__));d,out=sys.argv[1],sys.argv[2];fs=sorted(glob.glob(f'{D}/tw8_{d}/*.png'))[:8];os.makedirs(out,exist_ok=True)
h=lambda im:(lambda b:(b[3]-b[1],b))(im.getbbox());H0=h(Image.open(fs[0]).convert('RGBA'))[0]
for i,f in enumerate(fs):
    im=Image.open(f).convert('RGBA');hh,b=h(im)
    if abs(hh-H0)>0.5:
        s=H0/hh;im2=im.resize((round(256*s),round(256*s)),Image.NEAREST);cx=(b[0]+b[2])/2;fy=b[3];c=Image.new('RGBA',(256,256));c.paste(im2,(round(cx-cx*s),round(fy-fy*s)),im2);im=c
    im.save(f'{out}/{i:03d}.png');print(i,hh,'->',h(im)[0])
