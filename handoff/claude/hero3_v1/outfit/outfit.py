# 망토 색에 맞춰 옷(코트+망토, 남색 부분 전부)을 같이 바꾸는 가안
# 쓰는 법: python3 outfit.py → navy_mask.png(바뀌는 자리), outfit_sheet.png(망토별 옷 색). ic/<망토id>.webp = test128/assets/icons/grok/<id>_128.webp 복사본
# 규칙(사장님 10-31 「망토색에 따라서 옷색깔도 전부 바꿔야」 「바지색깔도」 「옷전체 색깔 다」): 살·머리 빼고 옷 전체. 색판 1458색을 classify.py로 [그대로/옷] 나눔.
# 옛 규칙: 남색(파랑-빨강 ≥ 8) 칸 = 코트+망토 → 망토 아이콘 색 띠로 밝기 순서대로 바꿈. 밝기 기준은 서기 3장에서 한 번 정해 모든 장에 똑같이 씀.
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
H=os.path.dirname(os.path.abspath(__file__))+'/'
S=H
G=H+'../game144/'
FONT=H+'../../../../godot25d/art/NanumGothic.ttf'
KS=[('c_ash_cloak','닳아빠진 잿빛 망토'),('c_ara_silk','아라크네의 실크 망토'),('c_shadow_thief','그림자 도둑의 망토'),('c_iron_knight','철혈기사의 무쇠망토'),('c_archive_parch','대서고의 양피지 망토'),('c_burning_noble','불타는 귀족의 외투'),('c_oswald_rosary','오스왈드의 철염주 망토'),('c_clock_brass','시계태엽의 황동 망토'),('c_king','박제된 군주의 망토'),('c_ian_red','이안의 붉은 소년 망토'),('c_first_ash','태초의 잿빛 망토'),('c_vault_bone','수장고의 뼈 망토'),('c_alch_lime','연금술사의 석회 망토')]
def lum(c): return c[...,0]*.299+c[...,1]*.587+c[...,2]*.114
def navy(a):
    r,g,b=[a[...,i].astype(int) for i in range(3)]
    return (a[...,3]>100)&(b-r>=8)&(b>=g-4)
def ramp(k,n=64):
    a=np.array(Image.open(S+'ic/'+k+'.webp').convert('RGBA')).reshape(-1,4)
    a=a[a[:,3]>200][:,:3].astype(float); a=a[np.argsort(lum(a))]
    a=a[int(len(a)*.08):int(len(a)*.97)]
    return np.array([a[int(i/n*len(a)):max(int(i/n*len(a))+1,int((i+1)/n*len(a)))].mean(0) for i in range(n)])
views=['down_face','right_face','up']
src={v:np.array(Image.open(G+v+'.png').convert('RGBA')) for v in views}
allv=np.concatenate([lum(src[v][...,:3].astype(float))[navy(src[v])] for v in views])
P5,P50,P95=np.percentile(allv,[5,50,95]); print('남색 밝기 기준',P5,P50,P95)
import json as _json
CLS={tuple(int(t) for t in k.split(',')):v for k,v in _json.load(open(H+'palette_class.json')).items()}   # classify.py
def outfit_mask(a,boxes=None):
    """옷 칸 = 살·머리·눈 빼고 전부. boxes = 그림판 칸 [x,y,w,h,…] 목록(없으면 그림 전체가 한 사람)."""
    r,g,b=[a[...,i].astype(int) for i in range(3)]; L=.299*r+.587*g+.114*b; op=a[...,3]>100
    nv=(b-r>=8)&(b>=g-4); warm=(r-b>=10)
    flat=a[...,:3].reshape(-1,3); keys=flat[:,0].astype(np.int64)*65536+flat[:,1].astype(np.int64)*256+flat[:,2]
    keepk=np.array([c[0]*65536+c[1]*256+c[2] for c,v in CLS.items() if v=='keep'],np.int64)
    voted_keep=np.isin(keys,keepk).reshape(a.shape[:2])
    rel=np.ones(a.shape[:2])          # 사람 키 안에서 위→아래 0..1
    if boxes is None: boxes=[(0,0,a.shape[1],a.shape[0])]
    for bx in boxes:
        x,y,w,h=bx[:4]; sub=op[y:y+h,x:x+w]; ys=np.nonzero(sub.any(1))[0]
        if len(ys)==0: continue
        t0,t1=ys.min(),ys.max()+1; yy=np.arange(h)[:,None]
        rel[y:y+h,x:x+w]=np.broadcast_to((yy-t0)/max(1,t1-t0),(h,w))
    skin=warm&(L>=95)&(r>b+30)
    head=rel<0.22
    dark=~nv&~warm&(L<50)
    keep=skin|(warm&head)|(dark&(rel<0.42))|(warm&voted_keep&(L>=70))|(~nv&~warm&(L>=50))
    return op&~keep
def recolor(a,R,boxes=None):
    # 옷 전체(사장님 10-31 「바지색깔도」 「옷전체 색깔 다 바꿔야된다구」): 코트·망토(남색) = 망토 색 띠 가운데, 바지·장화·허리띠·어깨 = 같은 띠에서 제 밝기대로. 살·머리는 그대로
    m=outfit_mask(a,boxes); nv=navy(a)&m; ot=m&~nv
    b=a.astype(float).copy(); L=lum(b[...,:3]); n=len(R)-1
    t=np.zeros(L.shape)
    t[nv]=0.5+(L[nv]-P50)/max(1,P95-P5)*0.8
    t[ot]=0.08+(L[ot]-10)/75*0.85           # 어두운 바지 = 띠 아래쪽, 밝은 청동 = 띠 위쪽
    idx=np.clip((t*n).round().astype(int),0,n)
    b[m,:3]=R[idx][m]; return b.astype(np.uint8),m
if __name__=='__main__':
    # 남색 고른 자리 보기
    vv=[]
    for v in views:
        a=src[v].copy(); m=navy(a); a[m,:3]=(a[m,:3]*.3+np.array([255,40,40])*.7).astype(np.uint8)
        im=Image.fromarray(a); im=im.crop(im.getbbox()); vv.append(im.resize((im.width*3,im.height*3),Image.NEAREST))
    c=Image.new('RGBA',(sum(i.width for i in vv)+40,vv[0].height),(120,120,128,255)); x=0
    for i in vv: c.paste(i,(x,0),i); x+=i.width+20
    c.save(S+'navy_mask.png')
    W,H=1920,1080; C=Image.new('RGB',(W,H),(34,36,42)); d=ImageDraw.Draw(C); f=ImageFont.truetype(FONT,18)
    cells=[(None,'지금 (원래 그림)')]+KS; K=1.45
    for i,(k,name) in enumerate(cells):
        cx=(i%5)*384; cy=(i//5)*360; x=cx+10
        for v in views:
            a=src[v] if k is None else recolor(src[v],ramp(k))[0]
            im=Image.fromarray(a); im=im.crop(im.getbbox()); im=im.resize((int(im.width*K),int(im.height*K)),Image.NEAREST)
            C.paste(im,(x,cy+92+int(144*K)-im.height),im); x+=im.width+6
        if k:
            ic=Image.open(S+'ic/'+k+'.webp').convert('RGBA').resize((40,40),Image.LANCZOS); C.paste(ic,(cx+12,cy+14),ic)
        d.text((cx+58 if k else cx+14,cy+24),name,font=f,fill=(255,235,150) if k is None else (235,235,235))
    C.save(S+'망토13종_옷색_가안.png')
