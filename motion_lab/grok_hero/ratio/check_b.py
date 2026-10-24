# 해결안 B 확인: ① 얼굴 맞추기 배율(걷기 얼굴 기준, 0.95~1.05) ② 팔 폭(손 높이 몸 앞쪽 끝, 걷기 20+ / 달리기 33+) ③ 키
# usage: check_b.py <클립폴더> <기준걷기키 walk_right|walk_se|walk_down|없음> <walk|run>
import sys,glob,json,numpy as np
sys.path.insert(0,'../se_test')
from PIL import Image
from facematch import facepatch
from pxscale import pxscale
d,ref,kind=sys.argv[1:4];fs=sorted(glob.glob(d+'/*.png'))[:8]
def top(a): return int(np.nonzero(a.any(1))[0].min())
H=[];fr=[]
for f in fs:
    a=np.array(Image.open(f).convert('RGBA'))[...,3]>0;t=top(a);h=189-t;H.append(h)
    band=a[t+int(.45*h):t+int(.62*h)];xs=np.nonzero(band.any(0))[0];fr.append(int(xs.max()))
out=dict(clip=d,H=[min(H),max(H)],arm=max(fr)-min(fr),front=fr)
if ref!='없음':
    p=facepatch(ref);T=np.array(Image.open(fs[0]).convert('RGBA')).astype(float);t=top(T[...,3]>0);res=[]
    for s in np.arange(.80,1.21,.02):
        q=np.array(pxscale(p,s)).astype(float);ph,pw=q.shape[:2];mk=q[...,3]>0;pv=q[...,:3][mk];pv=pv-pv.mean();bc=-9
        for y in range(t,t+45):
            for x in range(40,216-pw):
                w=T[y:y+ph,x:x+pw]
                if w.shape[:2]!=(ph,pw) or (w[...,3][mk]==0).mean()>.1: continue
                v=w[...,:3][mk];v=v-v.mean();c=(pv*v).sum()/(np.sqrt((pv**2).sum()*(v**2).sum())+1e-6);bc=max(bc,c)
        res.append((bc,s))
    c,s=max(res);out.update(face_scale=round(float(1/s),2),face_match=round(float(c),2))
need=20 if kind=='walk' else 33;out['arm_ok']=out['arm']>=need
print(json.dumps(out,ensure_ascii=False))
