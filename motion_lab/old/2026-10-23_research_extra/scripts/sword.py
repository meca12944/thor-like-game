"""주인공 대각선 위 달리기 8~11번 장: 사라진 칼을 4~7번 장의 칼(진짜 그림)을 거꾸로 순서로 손에 붙여 채움"""
import numpy as np
from PIL import Image
from fix import load
from scipy import ndimage
fr=load('hero8','run_up')
def blade(a,v=75):
    r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    m=(al>40)&(np.abs(r-g)<22)&(np.abs(g-b)<34)&((r+g+b)/3>v);m[:95]=False;m[:, :150]=False
    lab,n=ndimage.label(m)
    if not n:return m
    k=np.argmax(ndimage.sum(m,lab,range(1,n+1)))+1;return lab==k
def layer(a):
    m=blade(a);ys,xs=np.nonzero(m)
    gi=np.argmax(ys-0.3*xs);grip=(xs[gi],ys[gi])          # lowest-left end of the blade = where the hand holds it
    near=ndimage.binary_dilation(m,iterations=2)
    hilt=np.zeros_like(m);gx,gy=grip;hilt[gy-3:gy+4,gx-3:gx+4]=True
    L=(near|hilt)&(a[...,3]>40);return L,grip
def hand(a):
    al=a[...,3]>40;best=None
    for y in range(122,136):
        xs=np.nonzero(al[y])[0]
        if len(xs) and (best is None or xs.max()>best[0]):best=(xs.max(),y)
    return best[0]-3,best[1]
out=[f.copy() for f in fr]
# 8번 장의 흐릿한 칼 자국(몸 뒤로 반쯤 사라진 칼)을 둘레의 머리·망토 색으로 메움
for k in (8,9,10,11):
    a=out[k];g=blade(a,62);g=ndimage.binary_dilation(g,iterations=1)&(a[...,3]>40)
    ys,xs=np.nonzero(g);n=0
    for y,x in sorted(zip(ys,xs)):
        for d in (1,-1,2,-2,3,-3,4,-4,5,-5,6,-6,8,-8):
            if 0<=x-d<256 and not g[y,x-d] and a[y,x-d,3]>40:a[y,x]=a[y,x-d];n+=1;break
        else:a[y,x,3]=0
    print(k,'번 흐린 칼 지움',len(ys))
# 8번: 칼 자국 지운 자리에 남은 가는 검은 선(배경 위에 떠 있음) 정리 — 이웃이 적은 점부터 깎음
a=out[8]
for it in range(4):
    al=a[...,3]>40;nb=ndimage.convolve(al.astype(int),np.ones((3,3),int),mode='constant')-al
    kill=al&(nb<=3);kill[:,:150]=False;kill[115:]=False;a[kill,3]=0
lab,n=ndimage.label(a[...,3]>40);sz=ndimage.sum(np.ones_like(lab),lab,range(1,n+1));keep=np.argmax(sz)+1
a[(lab!=keep)&(lab>0),3]=0   # 몸과 떨어진 작은 점 지움
g2=ndimage.binary_dilation(blade(fr[8],62),iterations=3);ref=fr[9][...,3]>40
rm=g2&~ref;rm[:,:150]=False;a[rm,3]=0;print('8번 칼 테두리 남은 점',int(rm.sum()))
print('8번 떨어진 점',int(sz.sum()-sz.max()))
for t,s in [(8,7),(9,6),(10,5),(11,4)]:
    L,(gx,gy)=layer(fr[s]);hx,hy=hand(fr[t]);dx,dy=hx-gx,hy-gy
    sw=np.zeros_like(fr[s]);sw[L]=fr[s][L];sw=np.roll(sw,(dy,dx),(0,1))
    # the blade stays behind the body only where it would cross the cape/back: draw it on top (held in the right hand at the side)
    m=sw[...,3]>40;o=out[t].copy();o[m]=sw[m];out[t]=o
    print(t,'칼 출처',s,'손',(hx,hy),'옮김',(dx,dy))
im=Image.new('RGBA',(12*120,150),(60,70,60,255))
for i,a in enumerate(out):t=Image.fromarray(a).crop((68,50,188,200));im.paste(t,(i*120,0),t)
im.resize((12*120*2,300),Image.NEAREST).save('sword_try.png')
z=Image.new('RGBA',(5*80,90),(60,70,60,255))
for j,i in enumerate(range(7,12)):t=Image.fromarray(out[i]).crop((110,80,190,170));z.paste(t,(j*80,0),t)
z.resize((5*80*4,360),Image.NEAREST).save('sword_zoom.png')
np.save('run_up_sword.npy',np.array(out))
