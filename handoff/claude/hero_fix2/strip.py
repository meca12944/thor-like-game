import sys;sys.path.insert(0,'.')
from h8lib import *
from PIL import ImageDraw
R=sys.argv[1];out=sys.argv[2];names=sys.argv[3:];s,j,k,H=load(R)
rows=[H['anims'][n] for n in names];W=150;HH=200;n=max(len(r) for r in rows)
sh=Image.new('RGB',(W*n+120,HH*len(rows)),(40,44,52));d=ImageDraw.Draw(sh)
for ri,(nm,L) in enumerate(zip(names,rows)):
    d.text((4,ri*HH+4),nm,fill=(255,230,120))
    gy=ri*HH+180;d.line((120,gy,sh.width,gy),fill=(255,80,80));d.line((120,gy-144,sh.width,gy-144),fill=(80,160,255))
    for ci,f in enumerate(L):
        im,ax,ay=cell(R,H,f[0],f[1]);sh.paste(im,(120+ci*W+75-ax,gy-ay),im);d.text((120+ci*W+2,ri*HH+4),'%d:%dt'%(f[1],f[2]),fill=(200,200,200))
sh.save(out)
