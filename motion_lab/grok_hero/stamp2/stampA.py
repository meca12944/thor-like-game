# 고치기 안 A (팀장 10-25 「얼굴이 아주 커진다」, 크레딧 0): v2 판을 **원래 장의 살색 자리 안으로만** 찍고, 머리카락(앞머리·옆머리)은 원래 그대로 위에 남김
# 피부색: 판의 피부 3단(밝음·중간·그림자)을 **원래 장 피부 3단**으로 바꿔 끼움(밝기·채도 = 원래 몸). 눈·눈썹·입·반짝임 칸만 판 색 그대로
import glob,os,shutil,json,numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2
import stamp2 as S
from common import load,skinmask
G=S.G;OUT=f'{G}/final_stampedA'
def tones(px,k=3):
    c,_=kmeans2(px.astype(float),k,seed=2,minit='++');return c[np.argsort(c.mean(1))]
for d in os.listdir(f'{G}/final'):
    os.makedirs(f'{OUT}/{d}',exist_ok=True)
    for f in glob.glob(f'{G}/final/{d}/*.png'): shutil.copy(f,f'{OUT}/{d}/')
P={dn:S.plate(dn) for dn in ('down','dr','right')};T={}
for c,dn in S.DIR.items():
    Q,C,pal,skin3=P[dn];h,w=C.shape
    pskin=np.argsort(skin3.mean(1));ps=skin3[pskin]                       # 판 피부 3단(어두움→밝음)
    for f in sorted(glob.glob(f'{G}/final/{c}/*.png')):
        a=load(f);y0,x0,sc=S.place(a,Q,C,dn);o=a.copy()
        fs=ndimage.binary_fill_holes(ndimage.binary_closing(skinmask(a),iterations=1))   # 원래 살색 자리(눈·입 구멍 포함)
        ot=tones(a[skinmask(a)][:,:3]) if skinmask(a).sum()>6 else ps
        reg=o[y0:y0+h,x0:x0+w];win=fs[y0:y0+h,x0:x0+w];put=C&win
        q=Q[...,:3].astype(float);d=((q[...,None,:]-ps[None,None])**2).sum(-1);idx=d.argmin(-1);isskin=d.min(-1)<300
        new=Q.copy();new[...,:3]=np.where(isskin[...,None],ot[idx],Q[...,:3]).astype(np.uint8)
        reg[put]=new[put];Image.fromarray(o).save(f'{OUT}/{c}/{os.path.basename(f)}');T[f'{c}/{os.path.basename(f)}']=int(put.sum())
    print(c,'찍음')
json.dump(T,open('placeA.json','w'),indent=1)
