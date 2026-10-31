import sys;sys.path.insert(0,'.')
from h8lib import *;from fxclean import skin
R=sys.argv[1] if len(sys.argv)>1 else 'fix2';s,j,k,H=load(R);base=H['sheets'].index('anim/hero_grok_0.webp')
def ft(c):
    im,ax,ay=cell(R,H,base,c);px=im.load();W,Hh=im.size
    ys=[y for y in range(Hh) for x in range(W) if skin(px[x,y])]
    return (min(ys)-ay) if len(ys)>=8 else None
ref={}
for d in ['down','dr','right','up','n']:
    v=[ft(f[1]) for f in H['anims']['walk_'+d]];v=[x for x in v if x is not None];ref[d]=min(v) if v else None
print('walk faceTop',ref)
for n,L in H['anims'].items():
    if not L or L[0][0]!=base: continue
    d=n.split('_',1)[1] if '_' in n else ''
    if d not in ref or ref[d] is None or n.startswith('walk'): continue
    for f in L:
        t=ft(f[1])
        if t is not None and t<ref[d]-8: print(n,f[1],'faceTop',t,'walk',ref[d],'diff',ref[d]-t)
