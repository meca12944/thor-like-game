# idle4_up 다시 만들기: walk4_up 007(template_up 3% 통과 프레임)에서 픽셀 편집만으로 숨쉬기 12프레임(8틱).
# 가슴/어깨 위 띠 1px 상승, 머리카락·망토 아래 띠는 1~2프레임 늦게 따라감. 다리/발은 그대로(기준선 y=160).
import numpy as np,os,sys
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__)); import back_kp as K
V='/workspace/town-demo/char_v4/pixellab/hero/vid'; src=np.array(Image.open(f'{V}/px_walk4_up/007.png').convert('RGBA'))
# STANCE: 왼쪽(화면) 다리만 안쪽으로 4px 옮겨 다른 idle처럼 두 발을 모음(망토 자락은 그대로)
import numpy as _np
yy,xx=_np.mgrid[0:src.shape[0],0:src.shape[1]]
LM=(src[...,3]>0)&(xx>=93)&(xx<110)&(yy>=134)&(yy<=160)&((yy>=148)|(xx>=100))&~((src[...,0].astype(int)-src[...,2]>60)&(src[...,1]<50))
Lp=src.copy(); src[LM]=0; DX=4
for y,x in zip(*_np.where(LM)):
    if src[y,x+DX,3]==0 or x+DX<110: src[y,x+DX]=Lp[y,x]
_c=Lp[140:146,100:104].reshape(-1,4); _c=_c[_c[:,3]>0]; _c=_c[_c[:,:3].astype(int).sum(1).argmin()]
for y,x in zip(*_np.where(LM&(src[...,3]==0)&(yy<150))): src[y,x]=_c   # 다리 뒤 빈칸 = 안쪽 코트 그림자
a=src[...,3]>0; ys=np.where(a.any(1))[0]; crown,sole=ys[0],ys[-1]; H=sole-crown
yS=crown+int(.30*H); yB=crown+int(.47*H); yC=crown+int(.80*H)   # 어깨, 허리(망토 갈라짐), 망토 아래
U=[0,0,0,1,1,1,1,1,1,0,0,0]                                       # 숨 들이쉼 1px
def band(o,img,y0,y1,dy):
    if not dy: return
    seg=img[y0:y1].copy(); m=seg[...,3]>0; tgt=o[y0-dy:y1-dy]; tgt[m]=seg[m]  # 위로 겹쳐 그림(빈틈 없음)
out=[]
for t in range(12):
    o=src.copy()
    band(o,src,crown,yS+6,U[t])                 # 머리·어깨·가슴
    band(o,src,yS+6,yB,U[(t-1)%12])             # 등 머리카락·몸통 1프레임 늦게
    band(o,src,yB,yC,U[(t-2)%12] if U[(t-2)%12] and t%2==0 else 0)  # 망토 자락 2프레임 늦게(가끔)
    out.append(o)
od=f'{V}/px_idle4_up'
for t,o in enumerate(out): Image.fromarray(o).save(f'{od}/{t:03d}.png')
for t in (0,4):
    m=(out[t][...,3]>0)&~K.PP.steel(out[t]); q=K.meas(m); print(t,{k:q[k] for k in ('H','headw','shw','torso','sole')}, {k:round(100*(q[k]/K.TGT[k]-1),1) for k in ('H','headw','shw')})
