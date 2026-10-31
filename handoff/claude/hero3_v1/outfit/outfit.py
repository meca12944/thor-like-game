# 망토 색에 맞춰 옷(코트+망토, 남색 부분 전부)을 같이 바꾸는 가안
# 쓰는 법: python3 outfit.py → navy_mask.png(바뀌는 자리), outfit_sheet.png(망토별 옷 색). ic/<망토id>.webp = test128/assets/icons/grok/<id>_128.webp 복사본
# 규칙(사장님 10-31 「망토색에 따라서 옷색깔도 전부 바꿔야」): 남색(파랑-빨강 ≥ 8) 칸 = 코트+망토 → 망토 아이콘 색 띠로 밝기 순서대로 바꿈. 밝기 기준은 서기 3장에서 한 번 정해 모든 장에 똑같이 씀.
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
def recolor(a,R):
    m=navy(a); b=a.astype(float).copy(); L=lum(b[...,:3])
    t=0.5+(L-P50)/max(1,P95-P5)*0.8          # 모든 장에 같은 기준(장마다 안 바뀜)
    idx=np.clip((t*(len(R)-1)).round().astype(int),0,len(R)-1)
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
