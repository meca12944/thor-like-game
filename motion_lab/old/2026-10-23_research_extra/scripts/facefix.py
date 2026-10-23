"""얼굴 도장: 사장님이 본 서기 얼굴(방향마다 1장)을 모든 동작의 얼굴 자리에 맞춰 찍음(교과서 13-2 리네트 방식을 주인공에)"""
import numpy as np
from PIL import Image
from scipy import ndimage
from faces import H,cell,face
def skinmask(a,top_rows=45):
    r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    m=(al>200)&(r>150)&(g>95)&(b>70)&(r>g+15)&(g>b)&(r<250)
    top=np.nonzero((al>40).any(1))[0].min();m[top+top_rows:]=False
    lab,n=ndimage.label(m)
    if not n:return m
    k=np.argmax(ndimage.sum(m,lab,range(1,n+1)))+1;return lab==k
def ref_patch(a):
    m=ndimage.binary_fill_holes(skinmask(a))            # 피부 + 그 안의 눈·입
    m=ndimage.binary_closing(m,iterations=2);ys,xs=np.nonzero(m)
    y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    return a[y0:y1,x0:x1].copy(),m[y0:y1,x0:x1],(y0,x0)
def place(a,P,M,org):
    """그림 a의 얼굴 자리에 맞는 위치를 찾아(피부 모양 겹침 최대) 도장. 맞는 정도가 낮으면 안 찍음"""
    sm=skinmask(a);f=face(a)
    if f is None or sm.sum()<0.5*M.sum():return a,None
    cy,cx=f[0],f[1];h,w=M.shape;best=(-1,None)
    for dy in range(-6,7):
        for dx in range(-6,7):
            y0=cy-h//2+dy;x0=cx-w//2+dx
            if y0<0 or x0<0 or y0+h>a.shape[0] or x0+w>a.shape[1]:continue
            fill=ndimage.binary_fill_holes(sm)[y0:y0+h,x0:x0+w]
            sc=(fill&M).sum()/max(1,(fill|M).sum())
            if sc>best[0]:best=(sc,(y0,x0))
    if best[0]<0.55:return a,best[0]
    y0,x0=best[1];o=a.copy();reg=o[y0:y0+h,x0:x0+w]
    # 프레임에서 앞을 가리는 것(머리카락·칼·손)은 남김: 지금 그림에서도 피부였던 자리 + 도장 얼굴 안쪽(눈·입)만 바꿈
    fillnow=ndimage.binary_fill_holes(sm)[y0:y0+h,x0:x0+w]
    put=M&fillnow
    reg[put]=P[put];return o,best[0]
def ref_head(a,grow=2):
    """얼굴 + 둘레 앞머리까지(얼굴 테두리 grow칸) — 얼굴 모양 자체가 다른 그림에도 같은 얼굴이 되게"""
    m=ndimage.binary_fill_holes(skinmask(a));m=ndimage.binary_closing(m,iterations=2)
    m=ndimage.binary_dilation(m,iterations=grow)&(a[...,3]>40);ys,xs=np.nonzero(m)
    y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    return a[y0:y1,x0:x1].copy(),m[y0:y1,x0:x1]
def place2(a,P,M,maxd=7,thr=0.5):
    """얼굴 둘레까지 통째로 찍기. 자리 찾기: 지금 그림의 피부(채움)와 도장 피부가 가장 많이 겹치는 곳"""
    sm=ndimage.binary_fill_holes(skinmask(a));f=face(a)
    if f is None:return a,None
    PS=ndimage.binary_fill_holes(skinmask(np.dstack([P[...,:3],P[...,3]*M]).astype(np.uint8)))
    cy,cx=f[0],f[1];h,w=M.shape;best=(-1,None)
    for dy in range(-maxd,maxd+1):
        for dx in range(-maxd,maxd+1):
            y0=cy-h//2+dy;x0=cx-w//2+dx
            if y0<0 or x0<0 or y0+h>a.shape[0] or x0+w>a.shape[1]:continue
            win=sm[y0:y0+h,x0:x0+w];sc=(win&PS).sum()/max(1,(win|PS).sum())
            if sc>best[0]:best=(sc,(y0,x0))
    if best[0]<thr:return a,best[0]
    y0,x0=best[1];o=a.copy();reg=o[y0:y0+h,x0:x0+w];reg[M]=P[M];return o,round(best[0],2)
