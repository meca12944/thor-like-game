import numpy as np, sys, json
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from key import keyed, split_frames
def frames(path,n):
  rgb,fg=keyed(path);segs=split_frames(fg,n)
  out=[]
  for sg in segs:
    if sg[0]=='ids':
      m=np.isin(sg[2],sg[1])
    else:
      a,b=sg;m=np.zeros_like(fg);m[:,a:b]=fg[:,a:b]
    ys,xs=np.where(m);y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    rgba=np.zeros((y1-y0,x1-x0,4),np.uint8);rgba[...,:3]=rgb[y0:y1,x0:x1];rgba[...,3]=m[y0:y1,x0:x1]*255
    out.append(dict(img=rgba,x0=int(x0),y0=int(y0)))
  return out,rgb,fg
def anchor(f):
  a=f['img'][...,3]>0;H,W=a.shape
  # baseline: lowest row with a reasonable pixel count (ignores 1-2px sword tips)
  rc=a.sum(1);base=max(i for i in range(H) if rc[i]>=3)
  # x: centroid of head region (top 30% of opaque rows) -- head is the steadiest part
  ys=np.where(rc>0)[0];top=ys[0];hh=int((base-top)*.28)+1
  xs=np.where(a[top:top+hh].any(0))[0]
  w=a[top:top+hh].sum(0);cx=(w*np.arange(W)).sum()/w.sum()
  return float(cx),int(base)
if __name__=='__main__':
  p,n=sys.argv[1],int(sys.argv[2]);fr,rgb,fg=frames(p,n)
  print(len(fr),[ (f['img'].shape[1],f['img'].shape[0]) for f in fr],[anchor(f) for f in fr])
  # zoom strip, anchored
  Z=2;anc=[anchor(f) for f in fr];L=max(a[0] for a in anc);R=max(f['img'].shape[1]-a[0] for f,a in zip(fr,anc));T=max(a[1] for a in anc)
  cw=int(L+R)+4;ch=T+6;S=Image.new('RGBA',(cw*len(fr),ch),(60,60,70,255))
  for i,(f,a) in enumerate(zip(fr,anc)):
    im=Image.fromarray(f['img']);S.alpha_composite(im,(int(i*cw+L-a[0])+2,T-a[1]+2))
  d=ImageDraw.Draw(S)
  for i in range(len(fr)):d.line([(i*cw,T+2),(i*cw+cw,T+2)],fill=(0,255,0,255))
  S=S.resize((S.width*Z,S.height*Z),Image.NEAREST);S.save(sys.argv[3] if len(sys.argv)>3 else '/workspace/anim/strip.png')
