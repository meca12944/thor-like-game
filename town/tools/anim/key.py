# chroma-key a generated sheet: flood-fill background from borders -> exact #FF00FF, return RGBA + frames
import numpy as np, sys
from PIL import Image
from scipy import ndimage as ndi
def keyed(path):
  im=np.asarray(Image.open(path).convert('RGB')).astype(int)
  H,W,_=im.shape
  border=np.concatenate([im[0],im[-1],im[:,0],im[:,-1]])
  bg=np.median(border,axis=0)
  r,g,b=im[...,0],im[...,1],im[...,2]
  dist=np.sqrt(((im-bg)**2).sum(-1))
  # magenta-ish: red & blue high, green low
  mag=(r-g>90)&(b-g>40)&(g<120)
  cand=(dist<110)|mag
  lab,n=ndi.label(cand)
  edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
  bgm=np.isin(lab,list(edge))
  # enclosed holes that are strongly magenta also bg
  bgm|=(dist<60)&mag
  fg=~bgm
  fg=ndi.binary_opening(fg,iterations=1)
  # drop tiny specks
  lab,n=ndi.label(fg);sz=ndi.sum(fg,lab,range(1,n+1))
  keep=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>=40]);fg=keep
  # despill: pull magenta fringe on edge pixels toward neutral
  out=im.copy()
  edgepx=fg&~ndi.binary_erosion(fg,iterations=2)
  sp=edgepx&(r>g+30)&(b>g+30)
  m=np.minimum(r,b);out[...,0]=np.where(sp,np.minimum(r,g+ (r-g)//3),r);out[...,2]=np.where(sp,np.minimum(b,g+(b-g)//3),b)
  return out.astype(np.uint8),fg
def save_magenta(path,dst):
  rgb,fg=keyed(path);o=rgb.copy();o[~fg]=[255,0,255];Image.fromarray(o).save(dst);return rgb,fg
def split_frames(fg,n=None,mingap=3):
  cols=fg.any(0);xs=np.where(cols)[0]
  segs=[];s=None
  for x in range(fg.shape[1]):
    if cols[x] and s is None:s=x
    if not cols[x] and s is not None:
      segs.append([s,x]);s=None
  if s is not None:segs.append([s,fg.shape[1]])
  # merge tiny segments into neighbours
  segs=[sg for sg in segs]
  changed=True
  while changed:
    changed=False
    for i,(a,b) in enumerate(segs):
      if b-a<25 and len(segs)>1:
        j=i-1 if i>0 and (i==len(segs)-1 or a-segs[i-1][1]<segs[i+1][0]-b) else i+1
        segs[min(i,j)]=[min(segs[i][0],segs[j][0]),max(segs[i][1],segs[j][1])];del segs[max(i,j)];changed=True;break
  if n and len(segs)!=n:
    # fallback: split by component centroids with k-means on x
    lab,k=ndi.label(fg);objs=ndi.find_objects(lab);sz=ndi.sum(fg,lab,range(1,k+1))
    cx=np.array([ (o[1].start+o[1].stop)/2 for o in objs]);
    x0,x1=xs[0],xs[-1];cent=np.linspace(x0,x1,2*n+1)[1::2]
    for it in range(20):
      a=np.argmin(abs(cx[:,None]-cent[None]),1)
      for j in range(n):
        if (a==j).any():cent[j]=np.average(cx[a==j],weights=sz[a==j])
    segs=[]
    for j in range(n):
      ids=[i for i in range(k) if a[i]==j]
      if not ids: continue
      segs.append(('ids',[i+1 for i in ids],lab))
  return segs
