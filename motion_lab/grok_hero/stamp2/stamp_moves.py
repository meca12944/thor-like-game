# 새 동작(대시·맞기·점프·사망)에도 얼굴 B 도장: 머리 모양 겹침 0.80 이상인 장만, 그리고 **동작 하나에서 80% 이상 장이 맞을 때만 전부 찍음**(섞이면 얼굴이 장마다 바뀌어 깜빡임) → final_stampedB2/
import glob,os,shutil,numpy as np
from PIL import Image
from scipy import ndimage
import stamp2 as S, stampB as B
from common import load,skinmask
G=S.G;OUT=f'{G}/final_stampedB2'
DIRMAP={'down':'down','dr':'dr','right':'right'}
P={dn:B.build(dn) for dn in DIRMAP}
for c in sorted(os.listdir(f'{G}/final')):
    if c.split('_')[0] not in ('dash','jump','hurt','death','rjump'): continue
    os.makedirs(f'{OUT}/{c}',exist_ok=True);dn=c.split('_',1)[1];n=0;tot=0
    fs=sorted(glob.glob(f'{G}/final/{c}/*.png'))
    ok=dn in P and np.mean([S.headfit(load(f),dn)[2]>=.80 for f in fs])>=.8
    for f in fs:
        a=load(f);o=a.copy();tot+=1
        if ok:
            Pp,M=P[dn];h,w=M.shape;dy,dx,sc=S.headfit(a,dn)
            if True:
                y0,x0=S.POS[dn][0]+dy,S.POS[dn][1]+dx;put=M&B.area(a)[y0:y0+h,x0:x0+w]&(a[y0:y0+h,x0:x0+w,3]>0)
                Q=Pp.copy();sk=skinmask(a)
                if sk.any():
                    ps=put&(Q[...,:3].astype(float).mean(2)>90)
                    if ps.any(): Q[ps,:3]=np.clip(Q[ps,:3]*(a[sk][:,:3].astype(float).mean(0)/np.maximum(Q[ps][:,:3].astype(float).mean(0),1)),0,255).astype(np.uint8)
                o[y0:y0+h,x0:x0+w][put]=Q[put];n+=1
        Image.fromarray(o).save(f'{OUT}/{c}/{os.path.basename(f)}')
    print(c,'도장',n,'/',tot)
