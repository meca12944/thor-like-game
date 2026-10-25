# 자 ③: 정수리 → 허리띠 길이 (다리 자세와 상관없음). 허리띠 = 몸통 높이에서 갈색·청동 칸이 가장 많은 가로줄 묶음. 표시 그림으로 눈 확인
import sys,glob,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
from sizecheck import CL,fr
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
def belt(f):
    A=np.array(Image.open(f).convert('RGBA')).astype(int);r,g,b,a=[A[...,i] for i in range(4)]
    ys=np.nonzero((a>0).sum(1)>=3)[0];top=int(ys.min());H=189-top
    m=(a>0)&(r>g+8)&(g>=b)&(r>55)
    rows=m.sum(1).astype(float);lo,hi=top+int(.30*H),top+int(.55*H)
    sm=np.convolve(rows,np.ones(3)/3,'same');y=int(lo+np.argmax(sm[lo:hi]))
    return top,y
R={};ks=list(CL);S=2;W=Image.new('RGB',(len(ks)*150*S,210*S),(70,74,80));d=ImageDraw.Draw(W)
for i,k in enumerate(ks):
    v=[belt(f) for f in fr(k)];L=[y-t for t,y in v];R[k]=dict(crown_belt=float(np.median(L)),rng=[min(L),max(L)])
    t,y=v[0];im=Image.open(fr(k)[0]).convert('RGBA').crop((53,0,203,200)).resize((150*S,200*S),Image.NEAREST);ox=i*150*S;W.paste(im,(ox,20),im)
    d.line([(ox,20+t*S),(ox+150*S,20+t*S)],fill=(80,200,255));d.line([(ox,20+y*S),(ox+150*S,20+y*S)],fill=(255,80,80),width=2)
    d.text((ox+4,2),f'{k} {R[k]["crown_belt"]:.0f}',font=F,fill=(255,255,255));print(k,R[k])
W.save('beltline.png');json.dump(R,open('beltline.json','w'),indent=1)
