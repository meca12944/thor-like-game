# 짧은 동작 조립: 사이 장 + 핵심 자세 → <동작>/000..., ticks.json. 동작 하나에 한 번 이동(몸 가운데 = 서기 장과 같게, 발 = 땅 189; 공중 장은 그대로 위). 크기는 그림 그대로(겹쳐 보기로 따로 확인)
import sys,glob,os,json,numpy as np
from PIL import Image
from scipy import ndimage
def clean(im):
    # 그림 도구가 넣은 먼지·글자·효과 조각 지우기: 몸(가장 큰 덩어리)에 붙은 것만 남김 (교과서 1-00 #8)
    A=np.array(im);c=A[...,:3].astype(int);wh=(A[...,3]>0)&(c.min(2)>140)&(c.max(2)-c.min(2)<45);wh[:110]=False;A[wh]=0
    gr=(A[...,3]>0)&(c.min(2)>95)&(c.max(2)-c.min(2)<28);gr[:175]=False;A[gr]=0   # 발밑 회색 먼지   # 몸 아래쪽 흰 속도선·먼지(눈 반짝임은 위쪽이라 남음)
    L,n=ndimage.label(ndimage.binary_dilation(A[...,3]>40,iterations=2))
    if n>1:
        big=np.argmax(np.bincount(L.ravel())[1:])+1;A[L!=big]=0
    return Image.fromarray(A)
def bodyx(im):
    a=np.array(im)[...,3]>0;ys,xs=np.nonzero(a[60:150]);return float(xs.mean())
PLAN={  # (장 목록, 틱) — 회피대시 17틱(교과서), 출발 순간이 가장 빠름 → 2장 만에 숙인 자세
 'dash':(lambda k:[f'in_{k}/002.png',f'in_{k}/003.png',f'key_{k}.png',f'out_{k}/001.png',f'out_{k}/002.png',f'out_{k}/003.png'],[1,1,7,3,3,2]),
 'hurt':(lambda k:[f'key_{k}.png'] if k in ('hurt_down','hurt_right') else [f'in_{k}/002.png',f'key_{k}.png',f'in_{k}/002.png'],None),   # 사이 장이 깨진 방향(흰 테두리·번짐)은 핵심 자세만
 'jump':(lambda k:[f'in_{k}/001.png',f'in_{k}/002.png',f'in_{k}/003.png',f'key_{k}.png',f'out_{k}/001.png',f'out_{k}/002.png',f'out_{k}/003.png'],[3,3,3,12,3,3,4]),
 'rjump':(lambda k:[f'in_{k}/002.png',f'in_{k}/003.png',f'key_{k}.png',f'out_{k}/001.png',f'out_{k}/002.png',f'out_{k}/003.png'],[3,3,10,3,3,3]),
 'death':(lambda k:[f'in_{k}/{i:03d}.png' for i in range(1,9)]+[f'key_{k}.png'],[3,3,3,3,3,4,4,6,60]),
}
R=json.load(open('moves.json')) if os.path.exists('moves.json') else {}
for k in sys.argv[1:]:
    kind=k.split('_')[0];fs,ticks=PLAN[kind];fs=fs(k)
    if ticks is None: ticks=[14] if len(fs)==1 else [3,9,4]
    ims=[clean(Image.open(f).convert('RGBA')) for f in fs]
    d=k.split('_',1)[1];idle=Image.open(f'idle_{d}.png').convert('RGBA') if os.path.exists(f'idle_{d}.png') else ims[0]
    dx=round(bodyx(idle)-np.median([bodyx(i) for i in ims]))
    # 땅: 이 동작에서 가장 낮은 발 = 189 (점프 공중 장은 사이 장 그대로 위에 뜸)
    ki=[i for i,f in enumerate(fs) if f.startswith('key_')][0]
    dy=189-ims[ki].getbbox()[3] if kind in ('dash','hurt','death') else 189-max(ims[0].getbbox()[3],ims[-1].getbbox()[3])   # 땅 = 핵심 자세(대시·맞기·사망) / 점프는 처음·끝 장(땅을 딛은 장)
    os.makedirs(k,exist_ok=True)
    for f in glob.glob(f'{k}/*.png'): os.remove(f)
    for i,im in enumerate(ims):
        lift=max(0,im.getbbox()[3]+dy-189)   # 땅 밑으로 파고드는 장만 들어 올림(교과서 9)
        if kind in ('jump','rjump'): lift=im.getbbox()[3]+dy-189   # 점프: 모든 장 발을 땅에(높이는 게임 코드가 올림, 교과서 6 「높이는 코드」)
        c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy-lift),im);c.save(f'{k}/{i:03d}.png')
    R[k]=dict(frames=len(ims),ticks=ticks,dx=dx,dy=dy);print(k,R[k])
json.dump(R,open('moves.json','w'),indent=1)
