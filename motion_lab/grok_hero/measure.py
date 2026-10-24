# 크기 재기: 키(머리 꼭대기→발바닥), 머리→옷 아랫단(망토 끝), 머리(꼭대기→턱), 등신 = 키 / 머리, 발 기준점(발바닥 가운데)
import numpy as np
from PIL import Image
from scipy import ndimage
def meas(im):
    a=np.array(im.convert('RGBA')).astype(int);al=a[...,3]>40;ys,xs=np.nonzero(al);top,bot=ys.min(),ys.max()
    r,g,b=a[...,0],a[...,1],a[...,2]
    skin=al&(r>120)&(r>g+12)&(g>b)&(r-b>35)&(r<250)
    sk=np.nonzero(skin[:top+(bot-top)//3]);chin=sk[0].max() if len(sk[0]) else top+(bot-top)//6
    boot=al&(r>=50)&(r>b+18)&(r>g+8)&(np.arange(a.shape[0])[:,None]>top+(bot-top)*.6)   # 갈색 장화
    bt=np.nonzero(boot.any(1))[0];boot_top=bt.min() if len(bt) else bot
    # 옷 아랫단: 장화 위쪽에서 가장 아래까지 내려온 망토·옷 (어두운 남색·자주)
    cloth=al&(r<90)&(b>=r-12)&~boot;cy=np.nonzero(cloth.any(1))[0];hem=cy.max()
    feet_x=int(xs[ys>=bot-3].mean())
    H=bot-top+1;head=chin-top+1
    return dict(H=int(H),head=int(head),hem=int(hem-top+1),boot_top=int(boot_top-top),deung=round(H/head,2),feet=[feet_x,int(bot)],w=int(xs.max()-xs.min()+1))
