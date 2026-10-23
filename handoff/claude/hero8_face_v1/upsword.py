"""주인공 뒷모습(대각선 위) 서기·대시·맞기·점프: 칼이 손에 없고 머리 옆에 칼끝만 보임 → 걷기·달리기처럼 오른손에 칼을 쥐게 함.
 칼 그림은 같은 그림판의 jump_up 5번(오른손에 아래로 든 칼)에서 가져와 손 위치에 붙임. 머리 옆 칼끝은 머리카락 색으로 메움."""
import numpy as np
from PIL import Image
from scipy import ndimage
from faces import H,cell
def blade(a,v=95):
    r,g,b,al=[a[...,c].astype(int) for c in range(4)];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    return (al>40)&(mx-mn<40)&(mx>v)
def sword_layer():
    a,ax,ay=cell(H['anims']['jump_up'][5]);m=blade(a);lab,n=ndimage.label(m);k=np.argmax(ndimage.sum(m,lab,range(1,n+1)))+1;m=lab==k
    ys,xs=np.nonzero(m);gi=np.argmin(ys+xs);gy,gx=ys[gi],xs[gi]   # 칼자루 쪽 끝(왼쪽 위)
    hilt=np.zeros_like(m);hilt[max(0,gy-5):gy+3,max(0,gx-5):gx+3]=True
    L=(ndimage.binary_dilation(m,iterations=1)|hilt)&(a[...,3]>40)
    ys,xs=np.nonzero(L);y0,x0=ys.min(),xs.min();S=np.zeros((ys.max()-y0+1,xs.max()-x0+1,4),np.uint8);S[ys-y0,xs-x0]=a[ys,xs]
    return S,(gy-y0,gx-x0)
def hand(a,ax,ay):
    """오른손: 몸 오른쪽 아래(허리 높이) 가장 오른쪽 덩어리"""
    al=a[...,3]>40;best=None
    for y in range(max(0,ay-75),ay-45):
        xs=np.nonzero(al[y])[0]
        if len(xs) and (best is None or xs.max()>best[0]):best=(xs.max(),y)
    return best[0]-3,best[1]
def remove_tip(a,ax,ay):
    """머리 옆으로 튀어나온 하얀 칼끝을 테두리째 지움(투명하게). 머리카락과 맞닿은 쪽은 머리카락이 그대로 남음"""
    a=a.copy();m=blade(a,120);m[ay-60:]=False;n=int(m.sum())
    if not n:return a,0
    R=ndimage.binary_dilation(m,iterations=2)&(a[...,3]>40)
    hair=(a[...,3]>40)&~R;hair_near=ndimage.binary_dilation(hair,iterations=1)
    # 칼끝 둘레 중 머리카락 쪽(안쪽)은 둠: R 안에서 '칼끝 + 칼끝의 검은 테두리'만 지움
    border=R&~m;r,g,b=[a[...,c].astype(int) for c in range(3)];dark=(r+g+b)<150
    kill=m|(border&dark&~ndimage.binary_erosion(hair|m,iterations=1))
    a[kill,3]=0
    lab,k=ndimage.label(a[...,3]>40);sz=ndimage.sum(np.ones_like(lab),lab,range(1,k+1))
    for q,v in enumerate(sz):
        if v<40:a[lab==q+1,3]=0
    return a,n
def fix(a,ax,ay,S,G,sword=True):
    a,n=remove_tip(a,ax,ay)
    if not sword:return a,n,False
    if blade(a)[ay-70:].sum()>40:return a,n,False     # 이미 칼을 들고 있음
    hx,hy=hand(a,ax,ay);pad=60;big=np.zeros((a.shape[0]+pad,a.shape[1]+pad,4),np.uint8);big[:a.shape[0],:a.shape[1]]=a
    y0,x0=hy-G[0],hx-G[1];h,w=S.shape[:2];reg=big[y0:y0+h,x0:x0+w];m=S[...,3]>40;reg[m]=S[m]
    return big,n,True
