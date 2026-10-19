# one run cycle from a CMU BVH: left-foot contact -> next left-foot contact, root translation removed (keeps the bob),
# rotated so the run direction is +x, resampled to N frames -> 3D joints (x fwd, y up, z right)
import numpy as np,sys
sys.path.insert(0,'.');from bvh import load
GAP=float(__import__("os").environ.get("CYCLE_GAP","0.17"))
def cycle(fn,N=12):
    n,P,ft=load(fn);ix=lambda s:n.index(s)
    H=P[:,ix('Hips')];d=H[-1]-H[0];ang=np.arctan2(d[2],d[0]);c,s=np.cos(-ang),np.sin(-ang)
    Rm=np.array([[c,0,-s],[0,1,0],[s,0,c]]);Q=(P-H[:,None,:]*np.array([1,0,1]))@Rm.T   # in place, facing +x
    h=P[:,ix('LeftToeBase') if 'LeftToeBase' in n else ix('LeftFoot'),1]
    # contacts = local minima of left toe height with the foot moving backward relative to the hips
    cand=[k for k in range(3,len(h)-3) if h[k]<=h[k-3:k+4].min()+0.05]
    cs=[];[cs.append(k) for k in cand if not cs or k-cs[-1]>int(GAP/ft)]
    a,b=cs[0],cs[1]
    t=np.linspace(a,b,N+1)[:-1];F=np.array([Q[int(np.floor(x))]*(1-(x%1))+Q[min(len(Q)-1,int(np.floor(x))+1)]*(x%1) for x in t])
    return n,F,(b-a)*ft
if __name__=='__main__':
    from PIL import Image,ImageDraw
    n,F,dur=cycle(sys.argv[1],12);print('cycle s',round(dur,3))
    B=[('Hips','Spine'),('Spine','Spine1'),('Spine1','Neck'),('Neck','Head'),('Neck','LeftArm'),('LeftArm','LeftForeArm'),('LeftForeArm','LeftHand'),('Neck','RightArm'),('RightArm','RightForeArm'),('RightForeArm','RightHand'),('Hips','LeftUpLeg'),('LeftUpLeg','LeftLeg'),('LeftLeg','LeftFoot'),('Hips','RightUpLeg'),('RightUpLeg','RightLeg'),('RightLeg','RightFoot')]
    B=[(a,b) for a,b in B if a in n and b in n]
    o=Image.new('RGB',(12*110,160),(40,40,50));g=ImageDraw.Draw(o);s=3.2
    for i,f in enumerate(F):
        for a,b in B:
            A,Bp=f[n.index(a)],f[n.index(b)];g.line([(i*110+55+A[0]*s,150-A[1]*s),(i*110+55+Bp[0]*s,150-Bp[1]*s)],fill=(255,120,120) if 'Right' in a+b else (120,200,255),width=2)
    o.save(sys.argv[1]+'_side.png')
