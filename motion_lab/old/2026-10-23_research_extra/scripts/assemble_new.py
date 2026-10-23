"""새로 그린 주인공 걷기·달리기 조립: 크기·위치·땅은 동작 하나에 한 번만 (교과서 1-0)"""
import os,numpy as np
from PIL import Image
from scipy import ndimage
from fix import *
from pxscale import pxscale
def bodyh(fr):return np.median([boot_bot(a)-int(head_y([a])[0]) for a in fr])
def drop_head_tip(a):
    # 머리 위쪽에 남은 하얀 칼끝(등 뒤 칼) — 손에 칼을 들었으니 지움, 빈자리는 옆 머리카락 색으로
    a=a.copy();r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    m=(al>40)&(mx-mn<45)&(mx>110);m[110:]=False
    m=ndimage.binary_dilation(m,iterations=1)&(al>40)
    for y,x in zip(*np.nonzero(m)):
        for d in (2,3,4,5,6,8,-2,-3,-4,-5,-6,-8):
            if 0<=x+d<256 and not m[y,x+d] and a[y,x+d,3]>40:a[y,x]=a[y,x+d];break
        else:a[y,x,3]=0
    # 칼끝 테두리(어두운 선)가 떨어져 남으면 지움: 몸과 붙지 않은 작은 조각 제거
    m2=ndimage.binary_dilation(m,iterations=3);A=a[...,3]>40
    a[m2&A&((a[...,:3].astype(int).max(2)-a[...,:3].astype(int).min(2))<40)&(a[...,:3].astype(int).max(2)<90)&~ndimage.binary_erosion(A,iterations=2),3]=0
    lab,n=ndimage.label(a[...,3]>40);sz=ndimage.sum(np.ones_like(lab),lab,range(1,n+1))
    for j,v in enumerate(sz):
        if v<60:a[lab==j+1,3]=0
    return a,int(m.sum())
def build(src,ref,Gy,out,fix_tip=False):
    new=[Image.open(f'pl/{src}/{i:03d}.png').convert('RGBA') for i in range(8)]
    if fix_tip:
        tmp=[drop_head_tip(np.array(x)) for x in new];new=[Image.fromarray(t[0]) for t in tmp];print(' 칼끝 지움',[t[1] for t in tmp])
    s=bodyh(ref)/bodyh([np.array(x) for x in new]);sc=[np.array(pxscale(im,s)) for im in new]
    def place(a,dx,dy):
        o=np.zeros((256,256,4),np.uint8);h,w=a.shape[:2];ox,oy=int(round(128-128*s))+dx,int(round(189-189*s))+dy
        ys,xs=slice(max(0,oy),min(256,oy+h)),slice(max(0,ox),min(256,ox+w));o[ys,xs]=a[ys.start-oy:ys.stop-oy,xs.start-ox:xs.stop-ox];return o
    fr=[place(a,0,0) for a in sc]
    dy=Gy-max(boot_bot(a) for a in fr);dx=int(round(np.median(stats(ref)[:,2])-np.median(stats(fr)[:,2])))
    fr=[place(a,dx,dy) for a in sc];os.makedirs(f'out/hero8/{out}',exist_ok=True)
    for i,a in enumerate(fr):Image.fromarray(a).save(f'out/hero8/{out}/{i:03d}.png')
    print(out,'배율',round(s,3),'이동',dx,dy,'발',[boot_bot(a) for a in fr],'머리',list(map(int,head_y(fr))),'track',track(fr))
    return fr
if __name__=='__main__':
    build('cyc_walk_r',load('hero8','walk_right'),190,'walk_right_v2')
    build('cyc_walk_d',load('hero8','walk_down'),189,'walk_down_v2')
    build('cyc_walk_u',load('hero8','idle_up'),189,'walk_up_v2',fix_tip=True)
    build('cyc_run_d',load('hero8','run_down'),189,'run_down_v2')
    build('cyc_run_u',load('hero8','run_up'),189,'run_up_v2')
