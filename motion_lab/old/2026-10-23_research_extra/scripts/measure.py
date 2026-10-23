import sys,json,os,numpy as np
from PIL import Image
R='/home/user/thor-like-game/motion_lab/'
def load(ch,clip):
    d=R+ch+'/frames/'+clip;return [np.array(Image.open(d+'/'+f).convert('RGBA')) for f in sorted(os.listdir(d))]
def stats(fr):
    out=[]
    for a in fr:
        m=a[...,3]>40;ys,xs=np.nonzero(m)
        top=ys.min();bot=ys.max()
        # body center x: mean x in torso band (top+25%..top+60%)
        h=bot-top;band=m[top+int(h*.25):top+int(h*.6)]
        bx=np.nonzero(band)[1].mean()
        out.append((top,bot,bx,h))
    return np.array(out,float)
def diff(a,b):
    m=(a[...,3]>40)|(b[...,3]>40);return (np.abs(a[...,:3].astype(int)-b[...,:3].astype(int)).sum(2)*m).sum()/max(1,m.sum())+ ((a[...,3]>40)!=(b[...,3]>40)).sum()/50
if __name__=='__main__':
    for ch in ['hero8','linette']:
        C=json.load(open(R+ch+'/clips.json'))
        for k in sorted(C):
            fr=load(ch,k);s=stats(fr);n=len(fr)
            dd=[diff(fr[i],fr[(i+1)%n]) for i in range(n)]
            seam=dd[-1]/max(1e-3,np.mean(dd[:-1])) if n>2 else 0
            print(f"{ch[:3]} {k:18s} n{n:2d} t{sum(C[k]['ticks']):3d} head{np.ptp(s[:,0]):4.0f} foot{np.ptp(s[:,1]):4.0f} sway{np.ptp(s[:,2]):5.1f} hgt{s[:,3].min():4.0f}-{s[:,3].max():4.0f} seam{seam:4.1f} maxjump{max(dd[:-1])/np.median(dd[:-1]) if n>2 else 0:4.1f}")
