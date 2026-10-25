# 얼굴 맞추기로 배율 재기: 기준(걷기) 얼굴 조각(정수리~턱, 머리카락 날림 빼고 얼굴 둘레만)을 0.70~1.30배로 바꿔 가며 대상 장 머리 근처에서 가장 닮은 자리를 찾음
# → 대상 얼굴이 기준보다 몇 배 큰지 = 1/가장 잘 맞는 배율
import glob,sys,numpy as np,json
sys.path.insert(0,'../se_test')
from PIL import Image
from pxscale import pxscale
from measure_ratio import CLIPS
J=json.load(open('ratio_raw.json'))
def facepatch(k,i=0):
    m=J[k][i];x0,y0,x1,y1,_=m['face'];pad=4
    return Image.open(m['f']).convert('RGBA').crop((x0-pad,y0-pad,x1+pad+1,y1+pad+1))
def best(ref,k,i=0):
    m=J[k][i];T=np.array(Image.open(m['f']).convert('RGBA')).astype(float)
    top=m['top'];res=[]
    for s in np.arange(.70,1.31,.02):
        p=np.array(pxscale(ref,s)).astype(float);ph,pw=p.shape[:2];mk=p[...,3]>0;pv=p[...,:3][mk];pv=pv-pv.mean()
        bestc=-9
        for y in range(top,top+45):
            for x in range(60,200-pw):
                w=T[y:y+ph,x:x+pw]
                if w.shape[:2]!=(ph,pw) or (w[...,3][mk]==0).mean()>.1: continue
                v=w[...,:3][mk];v=v-v.mean();c=(pv*v).sum()/(np.sqrt((pv**2).sum()*(v**2).sum())+1e-6)
                if c>bestc: bestc=c
        res.append((bestc,round(float(s),2)))
    return max(res)
if __name__=='__main__':
  PAIRS=[('walk_right','walk_right'),('walk_right','run_right'),('walk_se','walk_se'),('walk_se','run_se'),('walk_down','walk_down'),('walk_down','run_s'),('walk_down','run_down(그록)')]
  OUT={}
  for a,b in PAIRS:
      c,s=best(facepatch(a),b,0 if a!=b else 1);OUT[f'{a}->{b}']=dict(match=round(float(c),3),scale=s,face_ratio=round(1/s,2));print(a,'→',b,'닮음',round(float(c),3),'배율',s,'⇒ 얼굴이',round(1/s,2),'배')
  json.dump(OUT,open('facematch.json','w'),indent=1,ensure_ascii=False)
