# 오른쪽 2타 타격(9)·팔로(10) 프레임 다리 앞 '머리 모양 얼룩' 제거: 얼룩 영역을 지우고 깨끗한 프레임 11의 앞 허벅지를 앞 부츠 기준으로 맞춰 이식.
import numpy as np,shutil
from PIL import Image
V='/workspace/town-demo/char_v4/pixellab/hero/vid'; D=f'{V}/px_combo3ref_right'; B=f'{V}/v3/_backup_blobfix/px_combo3ref_right'
def boot_x(a,y=176):
    xs=np.where(a[y,:,3]>0)[0]; runs=np.split(xs,np.where(np.diff(xs)>1)[0]+1); r=runs[-1]; return (r[0]+r[-1])/2
src=np.array(Image.open(f'{B}/011.png'))
for k,(x0,x1) in {9:(140,190),10:(146,194)}.items():
    a=np.array(Image.open(f'{B}/{k:03d}.png')); y0,y1=134,173
    dx=int(round(boot_x(a)-boot_x(src)))
    reg=a[y0:y1,x0:x1]; red=(reg[...,0].astype(int)-reg[...,2]>50)&(reg[...,0]>90)
    reg[~red]=0
    s=np.roll(src,dx,axis=1)[y0:y1,x0:x1]; sm=s[...,3]>0; sred=(s[...,0].astype(int)-s[...,2]>50)&(s[...,0]>90)
    put=sm&~sred; reg[put]=s[put]
    sk=(reg[...,0]>150)&(reg[...,1]>100)&(reg[...,3]>0); sk[:10]=False  # 이식된 손 조각 제거
    from scipy import ndimage as ndi
    sk=ndi.binary_dilation(sk,iterations=1)&(reg[...,3]>0)&~red; sk[:10]=False; reg[sk]=0
    a[y0:y1,x0:x1]=reg
    hx=156+(k-9)*2; bx=a[150:170,hx:hx+22]; bright=(bx[...,:3].astype(int).sum(-1)>150)&(bx[...,3]>0)&~((bx[...,0].astype(int)-bx[...,2]>50)&(bx[...,1]<60)); bx[bright]=0  # 남은 손/칼자루 조각
    m=a[...,3]>0; lab,n=ndi.label(m,np.ones((3,3))); sz=ndi.sum(m,lab,range(1,n+1))
    for i,z in enumerate(sz):
        if z<12:
            yy,xx=np.where(lab==i+1)
            if y0<=yy.mean()<y1 and x0<=xx.mean()<x1: a[lab==i+1]=0
    Image.fromarray(a).save(f'{D}/{k:03d}.png'); print(k,'dx',dx)
