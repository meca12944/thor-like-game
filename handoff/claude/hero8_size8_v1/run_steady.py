# 달리기 한 바퀴 안에서 머리가 앞뒤로 덜컥(옆 8칸, ↘ 13칸) -> 장마다 머리 위치 차이의 절반만 되돌림(발 움직임은 장마다 4칸 이하만 바뀜).
# 칸(cell)을 복사해 기준점 x만 바꿈(그림은 그대로). 다시 돌려도 같은 결과(_steady_src에서 다시).
import json,os,sys,numpy as np
from PIL import Image
from scipy import ndimage
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));HTML=ROOT+'/test128/index.html';K=0.5
CL=['run_right','run_dr','run_up','run_down']
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
src=A.get('_steady_src') or {k:[list(f) for f in A['anims'][k]] for k in CL};A['_steady_src']=src
SH={}
def crown(f):
    if f[0] not in SH:SH[f[0]]=np.array(Image.open(ROOT+'/test128/assets/'+A['sheets'][f[0]]).convert('RGBA'))
    x,y,w,h,ax,ay=A['cells'][f[0]][f[1]][:6];a=SH[f[0]][y:y+h,x:x+w];c=a[...,:3].astype(int)
    m=(a[...,3]>40)&~ndimage.binary_dilation((c.min(2)>150)&(c.max(2)-c.min(2)<40));t=np.nonzero(m.any(1))[0].min();row=m[t:t+10]
    lab,n=ndimage.label(row);sz=ndimage.sum(row,lab,range(1,n+1));return np.nonzero(lab==(np.argmax(sz)+1))[1].mean()-ax
for k in CL:
    hx=np.array([crown(f) for f in src[k]]);sh=np.round(-(hx-hx.mean())*K).astype(int);new=[]
    for f,d in zip(src[k],sh):
        c=list(A['cells'][f[0]][f[1]]);c[4]=c[4]-int(d);L=A['cells'][f[0]]
        if c not in L:L.append(c)
        new.append([f[0],L.index(c),f[2]]+f[3:])
    A['anims'][k]=new;print(k,'머리',hx.round().astype(int).tolist(),'옮김',sh.tolist())
A['_steady_note']='owner 10-23 motion lab: run cycles keep the head steadier (half of each frame\'s head offset from the cycle mean undone via copied cells with shifted anchor x; originals in _steady_src)'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:];open(HTML,'w').write(s)
