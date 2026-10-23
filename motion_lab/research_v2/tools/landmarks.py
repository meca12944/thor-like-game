# 몸 표시점: 머리 위, 허리띠(금색 줄), 장화 위, 발바닥 — 동작·방향이 달라도 같은 몸 길이를 재려고
import numpy as np
from scipy import ndimage
def marks(a):
    A=a[...,3]>40;r,g,b=[a[...,i].astype(int) for i in range(3)]
    c=a[...,:3].astype(int);sw=(c.min(2)>150)&(c.max(2)-c.min(2)<40);A2=A&~ndimage.binary_dilation(sw,iterations=1)
    ys=np.nonzero(A2.any(1))[0];top,bot=ys.min(),ys.max();h=bot-top
    gold=A&(r>85)&(g>55)&(b<70)&(r-b>45)&(g-b>20)
    boot=A&(r>=45)&(r>=b+20)&(r>=g+8)&(g>=b)&~gold
    rows=gold.sum(1).astype(float);rows[:top+int(h*.3)]=0;rows[top+int(h*.62):]=0
    belt=int(np.argmax(ndimage.uniform_filter1d(rows,3)))
    br=ndimage.binary_opening(boot).sum(1);br[:top+int(h*.6)]=0
    bt=np.nonzero(br>=3)[0];btop=int(bt.min()) if len(bt) else np.nan
    return dict(top=top,belt=belt,boot=btop,bot=bot)
