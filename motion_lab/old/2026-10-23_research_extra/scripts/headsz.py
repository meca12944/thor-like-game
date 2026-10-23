import json,sys,numpy as np,os
from PIL import Image
from scipy import ndimage
sys.path.insert(0,'.')
from facefix import skinmask
os.chdir('/home/user/thor-like-game')
s=open('test128/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e]);SH={}
def fr(f):
    if f[0] not in SH:SH[f[0]]=Image.open('test128/assets/'+H['sheets'][f[0]]).convert('RGBA')
    x,y,w,h,ax,ay=H['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((x,y,x+w,y+h)),(128-ax,189-ay));return np.array(c)
def hs(a):
    m=ndimage.binary_fill_holes(skinmask(a));ys,xs=np.nonzero(m)
    if len(ys)<20:return None
    top=np.nonzero((a[...,3]>40).any(1))[0].min()
    return ys.max()-top, xs.max()-xs.min()+1, m.sum()   # head top -> chin, face width, area
if __name__=='__main__':
  for d in ['right','down','dr']:
    for b in ['idle','walk','run','dash','jump']:
        k=f'{b}_{d}'
        if k not in H['anims']:continue
        v=[hs(fr(f)) for f in H['anims'][k]];v=[x for x in v if x]
        if v:print(k,'머리~턱',np.median([x[0] for x in v]),'얼굴폭',np.median([x[1] for x in v]),'넓이',np.median([x[2] for x in v]),len(v))
