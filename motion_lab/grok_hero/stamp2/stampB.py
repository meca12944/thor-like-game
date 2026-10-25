# 안 B 찍기 (사장님 10-25 「진행해」): PixelLab 「얼굴 틀·앞머리 그대로, 눈·코·입만」 기준 얼굴 faceB_<방향>.png
# 판 = 기준 장(src)의 원래 살색 자리(구멍 채움) +1px 안의 faceB 칸만 (앞머리·옆머리는 각 장 원래 그대로). 자리 = 머리 모양 겹치기(stamp2.headfit)
# 각 장에서도 그 장 살색 +1px 안에만 찍음. 피부 밝기는 장마다 원래 살색 평균에 맞춤(눈·입 진한 칸은 그대로)
import sys,glob,os,shutil,json,numpy as np
from PIL import Image
from scipy import ndimage
import stamp2 as S
from common import load,skinmask
G=S.G;OUT=f'{G}/final_stampedB'
def area(a): return ndimage.binary_fill_holes(ndimage.binary_closing(skinmask(a),iterations=1))
def build(dn):
    s=load(f'{S.R}/src_{dn}.png');b=load(f'{S.R}/faceB_{dn}.png');m=area(s)&(s[...,3]>0)   # 팀장 10-25: 판 둘레 = 원래 살색 +0px
    ys,xs=np.nonzero(m);y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1;S.POS[dn]=(int(y0),int(x0));return b[y0:y1,x0:x1].copy(),m[y0:y1,x0:x1]
if __name__=='__main__':
    dirs=sys.argv[1:] or ['down','dr','right'];T={}
    if not os.path.isdir(OUT):
        for d in os.listdir(f'{G}/final'):
            os.makedirs(f'{OUT}/{d}',exist_ok=True)
            for f in glob.glob(f'{G}/final/{d}/*.png'): shutil.copy(f,f'{OUT}/{d}/')
    for dn in dirs:
        P,M=build(dn);h,w=M.shape
        for c in [k for k,v in S.DIR.items() if v==dn]:
            for f in sorted(glob.glob(f'{G}/final/{c}/*.png')):
                a=load(f);dy,dx,sc=S.headfit(a,dn);y0,x0=S.POS[dn][0]+dy,S.POS[dn][1]+dx;o=a.copy()
                put=M&area(a)[y0:y0+h,x0:x0+w]&(a[y0:y0+h,x0:x0+w,3]>0)
                Q=P.copy();sk=skinmask(a)
                if sk.any():
                    tgt=a[sk][:,:3].astype(float).mean(0);ps=put&(Q[...,:3].astype(float).mean(2)>90);src=Q[ps][:,:3].astype(float).mean(0) if ps.any() else tgt
                    Q[ps,:3]=np.clip(Q[ps,:3]*(tgt/np.maximum(src,1)),0,255).astype(np.uint8)
                    for _ in range(3):   # 찍은 뒤 살색 평균 밝기를 원래와 같게 (±3 기준)
                        tmp=o.copy();tmp[y0:y0+h,x0:x0+w][put]=Q[put];sk2=skinmask(tmp)
                        if not sk2.any(): break
                        k=a[sk][:,:3].astype(float).mean()/max(1,tmp[sk2][:,:3].astype(float).mean())
                        if abs(k-1)<.005: break
                        Q[ps,:3]=np.clip(Q[ps,:3]*k,0,255).astype(np.uint8)
                o[y0:y0+h,x0:x0+w][put]=Q[put];Image.fromarray(o).save(f'{OUT}/{c}/{os.path.basename(f)}');T[f'{c}/{os.path.basename(f)}']=dict(dy=int(y0),dx=int(x0),fit=sc)
            print(c,'찍음')
    json.dump(T,open('placeB.json','w'),indent=1)
