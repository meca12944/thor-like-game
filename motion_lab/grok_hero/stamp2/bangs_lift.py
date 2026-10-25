# 앞머리 1~2칸 걷기 (사장님 10-25 팀장 추천 컨펌, A9): 얼굴 B 판 위에서, 열마다 살색 맨 위 칸 바로 위의 앞머리 칸을 아래 살색으로 바꿈(최대 2칸)
# 살색 넓이는 원래 +10% 이하로 막음(넘으면 그 장은 1칸만). 결과 ../final_stampedB2/
import glob,os,shutil,numpy as np
from PIL import Image
from scipy import ndimage
from common import load,skinmask
G='..';OUT=f'{G}/final_stampedB2'
CL=['walk_down','run_down','walk_dr','run_dr','walk_right','run_right']
def lift(a,n):
    o=a.copy();sk=skinmask(a);ys,xs=np.nonzero(sk)
    if len(ys)<10: return o,0
    add=0
    for x in range(xs.min(),xs.max()+1):
        col=np.nonzero(sk[:,x])[0]
        if not len(col): continue
        t=col.min()
        for k in range(1,n+1):
            y=t-k
            if y<0 or o[y,x,3]==0 or o[y,x,:3].astype(int).mean()>70: break   # 머리카락(어두운 칸)만
            o[y,x]=o[t,x];add+=1
    return o,add
for d in os.listdir(f'{G}/final_stampedB'):
    os.makedirs(f'{OUT}/{d}',exist_ok=True)
    for f in glob.glob(f'{G}/final_stampedB/{d}/*.png'): shutil.copy(f,f'{OUT}/{d}/')
for c in CL:
    r=[]
    for f in sorted(glob.glob(f'{G}/final_stampedB/{c}/*.png')):
        a=load(f);base=int(skinmask(load(f.replace('final_stampedB','final'))).sum())
        for n in (2,1,0):
            o,add=lift(a,n) if n else (a,0)
            if skinmask(o).sum()<=base*1.10: break
        Image.fromarray(o).save(f'{OUT}/{c}/{os.path.basename(f)}');r.append((n,int(skinmask(o).sum()),base))
    print(c,[f'{n}칸 {s}/{b}' for n,s,b in r][:4])
