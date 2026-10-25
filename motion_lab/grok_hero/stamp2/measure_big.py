# 「얼굴이 커 보임」 원인 나눠 재기 (팀장 10-25): 살색 넓이·높이·폭 / 원래 머리카락이던 칸이 살색이 된 수(앞머리 지움) / 피부 밝기·채도 / 눈(진한 칸) 크기
import sys,glob,json,numpy as np,colorsys
from PIL import Image
from scipy import ndimage
def sk(a):
    r,g,b,al=[a[...,i].astype(int) for i in range(4)];m=(al>0)&(r>110)&(r-b>25)
    t=np.nonzero(al.any(1))[0].min();m[:t]=0;m[t+40:]=0
    lab,n=ndimage.label(m)
    if n==0: return m
    k=np.argmax(ndimage.sum(m,lab,range(1,n+1)))+1;return lab==k
def stats(a,o=None):
    m=sk(a);ys,xs=np.nonzero(m);px=a[m][:,:3].astype(float)/255
    hsv=np.array([colorsys.rgb_to_hsv(*p) for p in px]);r=dict(area=int(m.sum()),h=int(np.ptp(ys)+1),w=int(np.ptp(xs)+1),top=int(ys.min()),V=round(float(hsv[:,2].mean()),3),S=round(float(hsv[:,1].mean()),3))
    if o is not None:
        mo=sk(o);hair=(o[...,:3].astype(int).mean(2)<70)&(o[...,3]>0);r['hair_to_skin']=int((m&~mo&hair).sum())
    return r
if __name__=='__main__':
    R={}
    for c in sys.argv[1:]:
        for f in sorted(glob.glob(f'../final/{c}/*.png'))[:8:3]:
            n=f.split('/')[-1];o=np.array(Image.open(f).convert('RGBA'));R[f'{c}/{n}']={'원래':stats(o)}
            for lab,root in (('v2','../final_stamped2'),('A','../final_stampedA'),('B','../final_stampedB')):
                try: R[f'{c}/{n}'][lab]=stats(np.array(Image.open(f'{root}/{c}/{n}').convert('RGBA')),o)
                except FileNotFoundError: pass
    for k,v in R.items(): print(k,' | '.join(f"{lab} 넓이{s['area']} {s['w']}x{s['h']} 밝기{s['V']} 채도{s['S']}"+(f" 머리→살{s['hair_to_skin']}" if 'hair_to_skin' in s else '') for lab,s in v.items()))
    json.dump(R,open('measure_big.json','w'),ensure_ascii=False,indent=1)
