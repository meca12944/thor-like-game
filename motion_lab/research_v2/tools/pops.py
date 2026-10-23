# turnlog 기록 -> 틱마다 머리(정수리) 위치(발 기준, 그림 px) -> 순간이동(튐) 찾기
import sys,os,json,numpy as np
from PIL import Image
from scipy import ndimage
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
s=open(R+'/test128/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e])
SH={};C={}
def head(c):
    k=tuple(c[:7])
    if k in C:return C[k]
    sh,x,y,w,h,ax,ay=c[:7]
    if sh not in SH:SH[sh]=np.array(Image.open(R+'/test128/assets/'+H['sheets'][sh]).convert('RGBA'))
    a=SH[sh][y:y+h,x:x+w];col=a[...,:3].astype(int);sw=(col.min(2)>150)&(col.max(2)-col.min(2)<40)
    m=(a[...,3]>40)&~ndimage.binary_dilation(sw,iterations=1);ys=np.nonzero(m.any(1))[0];t=ys.min();row=m[t:t+10]
    lab,n=ndimage.label(row);sz=ndimage.sum(row,lab,range(1,n+1));xs=np.nonzero(lab==(np.argmax(sz)+1))[1]
    C[k]=(xs.mean()-ax,t-ay,ys.max()-t);return C[k]
def analyse(path,thr=5):
    L=json.load(open(path))['log'];hx=[];hy=[];hh=[]
    for r in L:
        c=r['cell'];x,y,hgt=head(c);x=(-x if c[7] else x)+(c[8] if len(c)>8 else 0);hx.append(x);hy.append(y);hh.append(hgt)
    hx=np.array(hx);hy=np.array(hy);d=np.abs(np.diff(hx))
    big=[(i,L[i]['seg'],L[i+1]['seg'],round(hx[i]),round(hx[i+1]),round(hy[i]),round(hy[i+1])) for i in np.nonzero(d>=thr)[0]]
    return hx,hy,np.array(hh),big
if __name__=='__main__':
    hx,hy,hh,big=analyse(sys.argv[1])
    print('머리 x 튐(5칸 이상)',len(big),'번, 합',int(sum(abs(b[4]-b[3]) for b in big)),'칸')
    for b in big:print('  틱',b[0],b[1],'->',b[2],'머리x',b[3],'->',b[4],' 머리위',b[5],'->',b[6])
    print('키(그림px) 걷기/달리기/서기 범위',hh.min(),hh.max())
def summary(path):
    L=json.load(open(path))['log'];hx,hy,hh,_=analyse(path);d=np.abs(np.diff(hx));dy=np.abs(np.diff(hy))
    return dict(최대튐=round(float(d.max()),1),튐10칸이상=int((d>=10).sum()),튐5칸이상=int((d>=5).sum()),머리위튐5칸이상=int((dy>=5).sum()),최대위튐=round(float(dy.max()),1),
                키범위=[int(hh.min()),int(hh.max())])
