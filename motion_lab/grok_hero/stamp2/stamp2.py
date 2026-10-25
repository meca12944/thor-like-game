# 얼굴 도장 v2 (10-25 확정안, 그록 얼굴 참고 + PixelLab 144 기준 얼굴): 교과서 「그록 얼굴 판 확정안」 순서
# ① 판 = 기준 얼굴의 피부(구멍 채움: 눈·눈썹·입 포함) ② 6색 = 판 피부 안 색을 6개로(피부 3 + 눈 + 반짝임 + 입), 몸 그림 피부도 이 피부 3색으로
# ③ 자리: 정면·↘ = 피부 겹침 가장 큰 곳 / 옆 = 피부 맨 위 줄 + 맨 앞(코끝) 칸 맞춤 → 장마다 dx,dy 표(place2.json)
# ④ 판은 지금 장 피부 ±1px 안만 바꿈, 둘레 1px는 지금 장 색과 판 색 중 더 어두운 쪽 ⑤ 판 크기·위치 따로 흔들지 않음(머리 따라감) ⑥ ↗·↑ 안 찍음
# usage: stamp2.py [동작...]  (기본: 정면·↘·옆 걷기·달리기 6개) 결과 ../final_stamped2/
import sys,glob,os,json,shutil,numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2
from common import load,skinmask
POS={}
R=os.path.dirname(os.path.abspath(__file__));G=f'{R}/..';OUT=f'{G}/final_stamped2'
DIR={'walk_down':'down','run_down':'down','walk_dr':'dr','run_dr':'dr','walk_right':'right','run_right':'right'}
L=lambda c:np.asarray(c,float)[...,:3].mean(-1)
def plate(dn):
    a=load(f'{R}/face_{dn}.png');sk=skinmask(a,smax=.62);core=ndimage.binary_fill_holes(ndimage.binary_closing(sk,iterations=2))
    core=ndimage.binary_dilation(core,iterations=2)&(a[...,3]>0)   # 얼굴 + 둘레 2칸(앞머리 가장자리)
    ys,xs=np.nonzero(core);y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1;P=a[y0:y1,x0:x1].copy();C=core[y0:y1,x0:x1];POS[dn]=(int(y0),int(x0))
    S6=ndimage.binary_fill_holes(ndimage.binary_closing(skinmask(a,smax=.62),iterations=2))[y0:y1,x0:x1]   # 얼굴 안(피부·눈·입)만 6색
    px=P[S6][:,:3].astype(float);pal,lab=kmeans2(px,6,seed=3,minit='++')
    Q=P.copy();Q[S6,:3]=pal[lab].astype(np.uint8)
    skin3=pal[np.argsort(-np.array([(np.sum(lab==i)) for i in range(6)]))[:3]]   # 판에서 가장 많이 쓴 3색 = 피부 3단
    return Q,C,pal,skin3
def anchor(m,dn):
    ys,xs=np.nonzero(m)
    if dn=='right': return ys.min(),xs.max()   # 옆: 피부 맨 위 + 코끝
    return None
def headfit(a,dn):
    # 자리 = 기준 얼굴을 만든 원래 장(src_<방향>.png)의 머리 모양(불투명 칸, 머리 끝~30줄)을 이 장에 가장 잘 겹치는 이동 (10-25: 피부 모양으로 찾으면 옆얼굴이 어긋남)
    s=load(f'{R}/src_{dn}.png');sa=s[...,3]>0;t=np.nonzero(sa.any(1))[0].min();S=sa[t:t+30]
    fa=a[...,3]>0;tf=np.nonzero(fa.any(1))[0].min();best=(-1,None)
    for dy in range(tf-t-4,tf-t+5):
        for dx in range(-8,9):
            Wn=np.roll(fa,(-dy,-dx),(0,1))[t:t+30];sc=(Wn&S).sum()/max(1,(Wn|S).sum())
            if sc>best[0]: best=(sc,(dy,dx))
    return best[1][0],best[1][1],round(best[0],2)
def place(a,Q,C,dn):
    dy,dx,sc=headfit(a,dn);return POS[dn][0]+dy,POS[dn][1]+dx,sc
    fs=ndimage.binary_fill_holes(skinmask(a));h,w=C.shape
    if not fs.any(): return None
    if dn=='right':
        ty,tx=anchor(fs,dn);py,px=anchor(C,dn);return ty-py,tx-px,None
    ys,xs=np.nonzero(fs);cy,cx=int(ys.mean()),int(xs.mean());best=(-1,None)
    for dy in range(-7,8):
        for dx in range(-7,8):
            y0,x0=cy-h//2+dy,cx-w//2+dx;win=fs[y0:y0+h,x0:x0+w]
            if win.shape!=C.shape: continue
            s=(win&C).sum()/max(1,(win|C).sum())
            if s>best[0]: best=(s,(y0,x0))
    return best[1][0],best[1][1],round(best[0],2)
def stamp(a,Q,C,skin3,pos):
    y0,x0=pos[0],pos[1];h,w=C.shape;o=a.copy()
    fs=ndimage.binary_fill_holes(skinmask(a));sk=skinmask(a)
    # 몸 피부도 같은 피부 3색으로
    d=((o[sk][:,:3][:,None,:].astype(float)-skin3[None])**2).sum(2);o[...,:3][sk]=skin3[d.argmin(1)].astype(np.uint8)
    put=C&(o[y0:y0+h,x0:x0+w][...,3]>0)   # 10-25: 피부 ±1px 규칙은 기준 얼굴 피부 모양이 달라 얼굴이 잘림 → 판 전체를 캐릭터 안에만
    edge=put&~ndimage.binary_erosion(put)
    reg=o[y0:y0+h,x0:x0+w];inner=put&~edge;reg[inner]=Q[inner]
    darker=L(Q)<L(reg);e2=edge&darker;reg[e2]=Q[e2]
    return o
if __name__=='__main__':
    clips=sys.argv[1:] or list(DIR);T={}
    for d in os.listdir(f'{G}/final'):
        os.makedirs(f'{OUT}/{d}',exist_ok=True)
        for f in glob.glob(f'{G}/final/{d}/*.png'): shutil.copy(f,f'{OUT}/{d}/')
    P={dn:plate(dn) for dn in set(DIR.values())}
    for c in clips:
        dn=DIR[c];Q,C,pal,skin3=P[dn]
        for f in sorted(glob.glob(f'{G}/final/{c}/*.png')):
            a=load(f);pos=place(a,Q,C,dn)
            if pos is None: T[f'{c}/{os.path.basename(f)}']=None;continue
            Image.fromarray(stamp(a,Q,C,skin3,pos)).save(f'{OUT}/{c}/{os.path.basename(f)}');T[f'{c}/{os.path.basename(f)}']=dict(dy=int(pos[0]),dx=int(pos[1]),iou=pos[2])
        print(c,'찍음',sum(1 for k,v in T.items() if k.startswith(c+'/') and v),'/',len(glob.glob(f'{G}/final/{c}/*.png')))
    json.dump(T,open(f'{R}/place2.json','w'),indent=1)
    json.dump({dn:['#%02x%02x%02x'%tuple(int(v) for v in p) for p in P[dn][2]] for dn in P},open(f'{R}/palette6.json','w'),indent=1)
