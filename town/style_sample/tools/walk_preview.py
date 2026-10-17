import sys, time
from PIL import Image, ImageDraw
S='/workspace/town-demo/style_sample/'
ns=sys.argv[1].split(','); k=int(sys.argv[2]) if len(sys.argv)>2 else 2
ims=[Image.open(S+f'assets/walk_{n}.png') for n in ns]
W=ims[0].width; H=ims[0].height
out=Image.new('RGBA',(W*k,(H)*k*len(ns)),(70,90,70,255))
for i,im in enumerate(ims):
    out.alpha_composite(im.resize((W*k,H*k),Image.NEAREST),(0,i*H*k))
d=ImageDraw.Draw(out)
for i in range(len(ns)*4+1): d.line([(0,i*57*k),(W*k,i*57*k)],fill=(40,50,40,255))
for c in range(13): d.line([(c*48*k,0),(c*48*k,out.height)],fill=(40,50,40,255))
p=S+f'work/wp_{ns[0]}_{int(time.time())}.png'; out.save(p); print(p,out.size)
