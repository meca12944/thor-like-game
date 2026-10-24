# 그록 새 주인공 시트 자르기 (사장님 10-24 「기존 주인공 교본 보고, 이거로 주인공 다시 만들어」, 크레딧 0)
#  걷기·달리기 4줄(정면·오른쪽·뒷면·왼쪽) × 6장 → 장마다: 회색 배경(가장자리에서 기울기까지 맞춤) 지움, 바닥 그림자 지움, 먼지(밝은 베이지)는 따로 떼어 냄
#  python3 motion_lab/grok_hero/cut.py  → motion_lab/grok_hero/cut/<동작>_<방향>/NNN.png, dust/…, 원본 크기 그대로 (크기 맞추기는 assemble 에서 한 번만)
import os,json,numpy as np
from PIL import Image
from scipy import ndimage
import sys
R=os.path.dirname(os.path.abspath(__file__));SRC=sys.argv[1] if len(sys.argv)>1 and __name__=='__main__' else os.path.join(R,'../../docs_art/grok_hero_20261024')   # 새 그림이 오면: python3 cut.py <그림 폴더>
DIRS=['down','right','up','left']
def plane(c):  # 가장자리 픽셀로 배경 기울기(평면) 맞추기
    h,w=c.shape[:2];ys,xs=np.mgrid[:h,:w];b=np.zeros((h,w),bool);b[:4]=b[-4:]=True;b[:,:4]=b[:,-4:]=True
    X=np.c_[xs[b],ys[b],np.ones(b.sum())];bg=np.zeros((h,w,3))
    for k in range(3):co,*_=np.linalg.lstsq(X,c[...,k][b],rcond=None);bg[...,k]=co[0]*xs+co[1]*ys+co[2]
    return bg
def bgimage(a):  # 시트 전체 배경: 그림 자리를 빼고 남은 회색을 크게 흐려 채움 (가장자리 어두워짐까지 따라감)
    a=a.astype(float);med=np.median(a.reshape(-1,3),0);fig=ndimage.binary_dilation(np.abs(a-med).sum(2)>30,iterations=12);w=(~fig).astype(float);out=np.zeros_like(a)
    for k in range(3):
        num=ndimage.gaussian_filter(a[...,k]*w,25);den=ndimage.gaussian_filter(w,25);out[...,k]=num/np.maximum(den,1e-3)
    return out
def cut(c,bg):
    c=c.astype(float);d=np.abs(c-bg).sum(2);lum=c.mean(2);blum=bg.mean(2)
    r,g,b=c[...,0],c[...,1],c[...,2];sat=c.max(2)-c.min(2)
    dust=(lum>blum+12)&(r>=g)&(r-b>6)&(sat<60)             # 먼지: 배경보다 밝은 따뜻한 베이지 (칼날은 회색·푸른 기 → 제외)
    dl,dn=ndimage.label(ndimage.binary_opening(dust),np.ones((3,3)));dm=np.zeros_like(dust);H=c.shape[0]
    for i,sl in enumerate(ndimage.find_objects(dl)):
        m=dl[sl]==i+1;hh=sl[0].stop-sl[0].start;ww=sl[1].stop-sl[1].start
        if m.sum()>=30 and sl[0].stop>H*.7 and m.sum()>.3*hh*ww:dm[sl]|=m   # 발 높이의 뭉툭한 덩어리만 (긴 칼날은 칸을 적게 채움 → 몸 쪽)
    dm=ndimage.binary_dilation(dm,iterations=1)&(lum>blum+4)
    core=(d>60)&~dm
    soft=(d>26)&~dm
    shadow=(sat<14)&(lum<blum)&(lum>blum-38)               # 바닥 그림자: 배경보다 조금 어두운 무채색
    lab,n=ndimage.label(soft&~shadow|core,np.ones((3,3)))
    keep=np.zeros_like(core)
    for i,sl in enumerate(ndimage.find_objects(lab)):
        m=lab[sl]==i+1
        if (core[sl]&m).sum()>=40 and (sl[1].stop-sl[1].start)>4:keep[sl]|=m   # 가는 세로줄(시트 칸 경계) 버림
    keep=ndimage.binary_fill_holes(keep)&(soft|core|ndimage.binary_erosion(keep,iterations=2))
    out=np.zeros(c.shape[:2]+(4,),np.uint8);out[...,:3]=c.clip(0,255);out[...,3]=keep*255
    du=np.zeros_like(out);du[...,:3]=c.clip(0,255);du[...,3]=(dm&~keep)*255
    return out,du
def bands(a,axis,thr):
    bg=np.median(a.reshape(-1,3),0);m=np.abs(a-bg).sum(2)>40;v=m.sum(axis);B=[];inb=False
    for i,x in enumerate(v):
        if x>thr and not inb:inb=True;s=i
        if x<=thr and inb:inb=False;B.append((s,i))
    if inb:B.append((s,len(v)))
    return B
info={}
if __name__=='__main__':
    for mo in ('walk','run'):
        a=np.array(Image.open(f'{SRC}/hero_{mo}_4dir.jpg').convert('RGB')).astype(int);H,W=a.shape[:2];BG=bgimage(a)
        rows=sorted(sorted(bands(a,1,3),key=lambda b:b[1]-b[0])[-4:])   # 큰 줄 4개 = 정면·오른쪽·뒷면·왼쪽
        for ri,(y0,y1) in enumerate(rows):
            y0=max(0,y0-6);y1=min(H,y1+6)
            # 6칸: 그림 사이 빈 세로줄로 나눔 (그록 시트는 칸 간격이 고르지 않음 — 1280/6 로 자르면 그림이 잘림)
            d=DIRS[ri];os.makedirs(f'{R}/cut/{mo}_{d}',exist_ok=True);os.makedirs(f'{R}/dust/{mo}_{d}',exist_ok=True)
            sub=a[y0:y1];m=(np.abs(sub-BG[y0:y1]).sum(2)>40).sum(0)>1;xs=[];inb=False
            for x,v in enumerate(m):
                if v and not inb:inb=True;s0=x
                if not v and inb:inb=False;xs.append([s0,x])
            if inb:xs.append([s0,W])
            while len(xs)>6:   # 가까운 조각끼리 합침 (칼·머리카락 끝)
                g=[xs[i+1][0]-xs[i][1] for i in range(len(xs)-1)];i=int(np.argmin(g));xs[i]=[xs[i][0],xs[i+1][1]];del xs[i+1]
            assert len(xs)==6,(mo,d,xs)
            mids=[(xs[i][1]+xs[i+1][0])//2 for i in range(5)];edges=[0]+mids+[W]
            for ci in range(6):
                x0,x1=edges[ci],edges[ci+1];c=a[y0:y1,x0:x1];o,du=cut(c,BG[y0:y1,x0:x1])
                Image.fromarray(o).save(f'{R}/cut/{mo}_{d}/{ci:03d}.png');Image.fromarray(du).save(f'{R}/dust/{mo}_{d}/{ci:03d}.png')
                info[f'{mo}_{d}_{ci}']=dict(src=[int(x0),int(y0),int(x1),int(y1)],px=int((o[...,3]>0).sum()),dust=int((du[...,3]>0).sum()))
    json.dump(info,open(f'{R}/cut/info.json','w'),indent=0)
    print('cells',len(info))
