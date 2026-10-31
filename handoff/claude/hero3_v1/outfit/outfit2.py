# 옷 부위별 색 = 그록 망토 13종 옷 디자인 (사장님 10-31 「그록이 망토 디자인 새로 올림」)
# 그록 시트(grok13/그록_망토NN_정면옆뒤.jpg, 1280×720, 정면·옆·뒤 자리 13장 모두 같음 ±10칸)에서 부위마다 색을 뽑아 띠(32칸, 어두움→밝음)로 만들고,
# 우리 동작 그림의 옷 칸을 부위로 나눠 그 띠로 칠함: 남색(코트·망토) = 망토 띠, 어두운 무채색(바지) = 바지 띠, 따뜻한 색 = 높이로 어깨 / 허리·팔 가죽 / 장화 띠.
# 살·머리·눈은 그대로(outfit.py 의 outfit_mask 그대로). 쓰는 법: python3 outfit2.py → 비교 그림
import os, importlib.util, numpy as np
from PIL import Image, ImageDraw, ImageFont
H=os.path.dirname(os.path.abspath(__file__))+'/'
spec=importlib.util.spec_from_file_location('of',H+'outfit.py'); of=importlib.util.module_from_spec(spec); spec.loader.exec_module(of)
IDS=[k for k,_ in of.KS]          # 그록 번호 01~13 = 이 순서 (01 잿빛 … 13 석회)
N=32
BOX={ # 그록 시트 정면·뒷면 자리 (1280×720)
 'cloak':[(885,300,1095,560)],                      # 뒷면 망토 한가운데(바탕이 안 섞이는 곳만)
 'pants':[(228,400,272,468),(298,400,342,468)],
 'sh':[(188,142,242,198),(332,142,388,198)],
 'belt':[(242,268,328,292)],
 'boots':[(192,600,245,668),(322,600,375,668)]}
INSIDE={'cloak','pants','belt'}   # 몸 안쪽만 뽑는 부위: 바탕 빼기 안 함(어두운 회색 옷이 바탕색과 비슷해 같이 빠지던 것 막음)
def band(a,boxes,bg,inside=False):
    px=np.concatenate([a[y0:y1,x0:x1].reshape(-1,3) for x0,y0,x1,y1 in boxes]).astype(float)
    if not inside: px=px[np.abs(px-bg).sum(1)>40]                  # 바탕 빼기
    ch=px-of.lum(px)[:,None]; dch=np.linalg.norm(ch-np.median(ch,0),axis=1); px=px[dch<=np.percentile(dch,80)]   # 핏자국·불꽃 같은 튀는 색 빼기(효과는 코드로)
    px=px[np.argsort(of.lum(px))]; px=px[int(len(px)*.06):int(len(px)*.96)]
    return np.array([px[int(i/N*len(px)):max(int(i/N*len(px))+1,int((i+1)/N*len(px)))].mean(0) for i in range(N)])
def bands(n):
    a=np.asarray(Image.open(H+f'grok13/그록_망토{n:02d}_정면옆뒤.jpg').convert('RGB')).astype(float); bg=np.median(a[5:40,5:60].reshape(-1,3),0)
    return {k:band(a,b,bg,k in INSIDE) for k,b in BOX.items()}
# 우리 부위 밝기 기준(서기 3장에서 한 번)
def parts(a,boxes=None):
    m=of.outfit_mask(a,boxes); r,g,b=[a[...,i].astype(int) for i in range(3)]; L=.299*r+.587*g+.114*b
    nv=(b-r>=8)&(b>=g-4); warm=(r-b>=10)
    rel=np.ones(a.shape[:2])
    for bx in (boxes or [(0,0,a.shape[1],a.shape[0])]):
        x,y,w,h=bx[:4]; sub=a[y:y+h,x:x+w,3]>100; ys=np.nonzero(sub.any(1))[0]
        if len(ys)==0: continue
        t0,t1=ys.min(),ys.max()+1; rel[y:y+h,x:x+w]=((np.arange(h)[:,None]-t0)/max(1,t1-t0))*np.ones((1,w))
    import cv2
    skin=(a[...,3]>100)&warm&(L>=95)&(r>b+30); nearskin=cv2.dilate(skin.astype(np.uint8),np.ones((5,5),np.uint8))>0
    n_,lab,st,_=cv2.connectedComponentsWithStats(skin.astype(np.uint8),connectivity=8)
    small=np.isin(lab,[i for i in range(1,n_) if st[i,cv2.CC_STAT_AREA]<8])          # 살색과 같은 색이지만 작은 점 = 어깨 청동 반짝임
    skin=skin&~small; nearskin=cv2.dilate(skin.astype(np.uint8),np.ones((5,5),np.uint8))>0
    shm=(a[...,3]>100)&warm&~skin&~nearskin&(rel>=.12)&(rel<.33)          # 어깨 청동: 머리 칸 안이라 outfit_mask 가 남겨 둔 것도 칠함(살 둘레 2칸은 얼굴 그림자라 남김)
    P={'cloak':m&nv,'pants':m&~nv&~warm,'sh':(m&warm&(rel<.33))|shm,'belt':m&warm&(rel>=.33)&(rel<.75),'boots':m&warm&(rel>=.75)}
    return P,L
REF={}
for k in BOX:
    v=np.concatenate([parts(of.src[s])[1][parts(of.src[s])[0][k]] for s in of.views]); REF[k]=np.percentile(v,[5,50,95])
def recolor2(a,B,boxes=None):
    P,L=parts(a,boxes); o=a.copy()
    for k,m in P.items():
        p5,p50,p95=REF[k]; t=.5+(L-p50)/max(1,p95-p5)*.8; idx=np.clip((t*(N-1)).round().astype(int),0,N-1)
        o[m,:3]=B[k][idx][m].astype(np.uint8)
    return o
if __name__=='__main__':
    F=ImageFont.truetype(of.FONT,20)
    for part,rng in [(1,range(1,8)),(2,range(8,14))]:
        C=Image.new('RGB',(1920,1080 if part==1 else 1080),(34,36,42)); d=ImageDraw.Draw(C)
        for i,n in enumerate(rng):
            cx=(i%2)*960; cy=(i//2)*270
            g=Image.open(H+f'grok13/그록_망토{n:02d}_정면옆뒤.jpg').crop((100,30,1130,690)).resize((412,264),Image.LANCZOS); C.paste(g,(cx+4,cy+3))
            B=bands(n); x=cx+430
            for v in of.views:
                im=Image.fromarray(recolor2(of.src[v],B)); im=im.crop(im.getbbox()); im=im.resize((int(im.width*1.75),int(im.height*1.75)),Image.NEAREST)
                C.paste(im,(x,cy+266-im.height),im); x+=im.width+6
            d.text((cx+8,cy+6),f'{n:02d} {of.KS[n-1][1]}',font=F,fill=(255,235,150))
        C.save(H+f'그록옷_게임그림_비교{part}.png')
    print('ok')
