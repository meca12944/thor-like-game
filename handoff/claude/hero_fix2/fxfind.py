import sys,colorsys;sys.path.insert(0,'.')
from h8lib import *
def isfx(p):
    r,g,b,a=p
    if a<=40: return False
    lum=.3*r+.59*g+.11*b
    return (lum>=70 and b>=r-5) or (lum>150 and b>=r-25)
if __name__=='__main__':
    R='fix2';s,j,k,H=load(R);from PIL import ImageDraw
    cells=[int(c) for c in sys.argv[1].split(',')];W=170
    sh=Image.new('RGB',(W*len(cells),200),(40,44,52));d=ImageDraw.Draw(sh)
    for i,c in enumerate(cells):
        im,ax,ay=cell(R,H,23,c);px=im.load();n=0;ov=im.copy();po=ov.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                if isfx(px[x,y]): po[x,y]=(255,0,255,255);n+=1
        sh.paste(ov,(i*W+85-ax,185-ay),ov);d.text((i*W+2,2),'%d n=%d'%(c,n),fill=(255,255,255))
    sh.save(sys.argv[2])
