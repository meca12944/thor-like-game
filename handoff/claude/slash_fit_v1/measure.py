import json,glob,sys,os
import numpy as np
from PIL import Image
HAZ={'위험(빨강)':(255,60,50),'독(보라)':(170,80,255),'거미줄(흰)':(225,225,240),'뿌리(초록)':(120,220,80),'수정(청록)':(90,255,160),'소환(노랑)':(255,220,60),'도토리(주황)':(255,160,60)}
def lin(c): c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def lum(a): l=lin(a); return 0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]
def lab(rgb):
    l=lin(np.asarray(rgb,float)); M=np.array([[.4124,.3576,.1805],[.2126,.7152,.0722],[.0193,.1192,.9505]]); xyz=l@M.T/np.array([.9505,1,1.089])
    f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116); return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
res={}
for m in sys.argv[1:]:
  for vd in sorted(glob.glob(f'out/{m}/*/')):
    v=os.path.basename(vd[:-1]); ratios=[]; cols=[]; area=0
    for f in range(48):
        a=np.asarray(Image.open(f'{vd}{f:03d}a.png').convert('RGB'),float); b=np.asarray(Image.open(f'{vd}{f:03d}b.png').convert('RGB'),float)
        mk=np.abs(a-b).sum(-1)>24
        if not mk.any(): continue
        A=a[mk];B=b[mk]; la=lum(A);lb=lum(B); r=(np.maximum(la,lb)+.05)/(np.minimum(la,lb)+.05); ratios.append(r); cols.append(A); area+=mk.sum()
    r=np.concatenate(ratios); C=np.concatenate(cols)
    # dominant slash colour = mean of brighter-saturated half (exclude near-white core)
    sat=C.max(1)-C.min(1); dom=C[sat>40].mean(0) if (sat>40).sum()>50 else C.mean(0)
    dl=lab(dom); hz={k:float(np.linalg.norm(lab(c)-dl)) for k,c in HAZ.items()}; near=min(hz,key=hz.get)
    res.setdefault(v,{})[m]={'med':float(np.median(r)),'p3':float((r>=3).mean()*100),'p2':float((r>=2).mean()*100),'area':int(area),'dom':[int(x) for x in dom],'hazNear':near,'hazDE':round(hz[near],1)}
json.dump(res,open('measure.json','w'),ensure_ascii=False,indent=1)
for v,d in res.items():
    print(v.ljust(18),' | '.join(f"{m}: 대비{d[m]['med']:.1f} 잘보임{d[m]['p3']:.0f}%" for m in d), '| 가까운경고', d[list(d)[0]]['hazNear'], d[list(d)[0]]['hazDE'])
