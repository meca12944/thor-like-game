# 방향·동작마다 크기 비교 (사장님 10-25 「캐릭 크기가 달라지는 건?」)
# 자 2개: ① 머리 조각 맞추기 — 같은 방향 걷기 머리(정수리~어깨)를 0.80~1.25배로 바꿔 가며 대 보기 (같은 방향 걷기 대비 배율)
#         ② 장화 길이 — 땅에 디딘 장화(갈색) 목~밑창 세로 길이, 모든 방향에 같은 물건 (방향끼리 비교)
import sys,glob,json,numpy as np
sys.path.insert(0,'../se_test')
from PIL import Image
from pxscale import pxscale
from scipy import ndimage
G='..'
CL={'walk_s2':f'{G}/se_test/walk_s2','walk_se':f'{G}/se_test/walk_se','walk_r2':f'{G}/se_test/walk_r2','walk_ne':f'{G}/se_test/walk_ne','walk_up':f'{G}/frames/walk_up',
    'run_s':f'{G}/se_test/run_s','run_se2':f'{G}/se_test/run_se2','run_r2':f'{G}/se_test/run_r2','run_ne2':f'{G}/se_test/run_ne2','run_n':f'{G}/se_test/run_n'}
REF={'run_s':'walk_s2','run_se2':'walk_se','run_r2':'walk_r2','run_ne2':'walk_ne','run_n':'walk_up'}
fr=lambda k:sorted(glob.glob(CL[k]+'/*.png'))[:8]
def boot(f):
    A=np.array(Image.open(f).convert('RGBA')).astype(int);r,g,b,a=[A[...,i] for i in range(4)]
    m=(a>0)&(r>g)&(g>b)&(r-b>18)&(r>45)&(r<170);m[:120]=0
    L,n=ndimage.label(ndimage.binary_closing(m,iterations=1));best=0
    for s in ndimage.find_objects(L):
        if s[0].stop>=184: best=max(best,s[0].stop-s[0].start)
    return best
def head(f):
    im=Image.open(f).convert('RGBA');a=np.array(im)[...,3]>0;t=int(np.nonzero(a.any(1))[0].min())
    xs=np.nonzero(a[t:t+40].any(0))[0];return im.crop((int(xs.min()),t,int(xs.max())+1,t+40)),t
def match(ref,f):
    p,_=head(ref);T=np.array(Image.open(f).convert('RGBA')).astype(float);_,t=head(f);best=(-9,1)
    for s in np.arange(.80,1.26,.02):
        q=np.array(pxscale(p,s)).astype(float);ph,pw=q.shape[:2];mk=q[...,3]>0;pv=q[...,:3][mk];pv=pv-pv.mean()
        for y in range(max(0,t-6),t+10):
            for x in range(20,236-pw,1):
                w=T[y:y+ph,x:x+pw]
                if w.shape[:2]!=(ph,pw): continue
                ov=(w[...,3]>0)==mk
                if ov.mean()<.8: continue
                v=w[...,:3][mk];v=v-v.mean();c=(pv*v).sum()/(np.sqrt((pv**2).sum()*(v**2).sum())+1e-6)+0.5*ov.mean()
                if c>best[0]: best=(c,s)
    return best
R={}
for k in CL:
    bt=[boot(f) for f in fr(k)];R[k]=dict(boot=int(max(bt)) if bt else 0)
    if k in REF:
        ms=[match(fr(REF[k])[0],f) for f in fr(k)[::2]];R[k]['head_vs_walk']=round(float(1/np.median([s for c,s in ms])),2)
    print(k,R[k],flush=True)
json.dump(R,open('sizecheck.json','w'),ensure_ascii=False,indent=1)
