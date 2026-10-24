"""때리기 사이 장의 흰 효과 지우기: 몸에서 떨어진 덩어리 + 몸에 붙은 새하얀 큰 덩어리(칼날은 가늘어서 남음)"""
import numpy as np
from scipy import ndimage
def clean(a,white=238,big=40):
    a=a.copy();A=a[...,3]>40;lab,n=ndimage.label(A,np.ones((3,3)))
    if n>1:
        sz=ndimage.sum(A,lab,range(1,n+1));k=np.argmax(sz)+1;a[(lab!=k)&A,3]=0
    r,g,b=[a[...,c].astype(int) for c in range(3)];W=(a[...,3]>40)&(r>=white)&(g>=white)&(b>=white)
    lw,nw=ndimage.label(W,np.ones((3,3)))
    for i in range(1,nw+1):
        m=lw==i
        if m.sum()>=big and ndimage.binary_erosion(m,iterations=2).any():a[ndimage.binary_dilation(m),3]=0
    return a
