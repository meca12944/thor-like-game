import os,sys,numpy as np
from PIL import Image
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; A=O+'/moves_v1'
for m in sys.argv[1:]:
  for d in ['south','north','east','west']:
    p=f'{A}/{m}/{d}'
    if not os.path.isdir(p): print(m,d,'missing'); continue
    F=[np.array(Image.open(f'{p}/{f}').convert('RGBA')).astype(int) for f in sorted(os.listdir(p))]
    base=np.array(Image.open(f'{O}/v1_1x_descA/{d}.png').convert('RGBA')).astype(int)
    pal=base[base[...,3]>128][:,:3]; pal=np.unique(pal//8,axis=0)
    def diff(a,b): return np.mean(np.any(np.abs(a-b)>24,axis=2))*100
    cons=[diff(F[i],F[i+1]) for i in range(len(F)-1)]; seam=diff(F[-1],F[0])
    # novel colours: opaque pixels whose colour (quantised) far from base palette
    nov=[]; bright=[]
    for f in F:
        px=f[f[...,3]>128][:,:3]; q=px//8
        s=set(map(tuple,pal)); n=sum(1 for c in map(tuple,q) if c not in s)
        nov.append(100*n/max(1,len(px))); bright.append(int(np.sum((px.min(1)>225))))
    bb=[Image.fromarray(f.astype('uint8')).getbbox() for f in F]
    print(f'{m:6s}{d:6s} consec {np.mean(cons):5.1f}% seam(last->first) {seam:5.1f}%  novelcol% max {max(nov):4.1f}  whitepx {min(bright)}-{max(bright)}  h {min(b[3]-b[1] for b in bb)}-{max(b[3]-b[1] for b in bb)} feetY {[b[3] for b in bb]}')
