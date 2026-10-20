# Owner 10-20 "그냥 스켈레톤 써서 다시 걷는 프레임시트": front (south) / back (north) walk skeletons straight from CMU mocap 07_01 (walk),
# seen from the front/back with the game's low top-down tilt. Bone directions = mocap 3D projected (so lifted/forward legs foreshorten),
# bone lengths = Linette's front/back still; hip bob from the mocap; arms = her still arms riding on the shoulders (needles down).
# usage: mocap_ns.py <bvh> <south|north> <out.json> [N=8] [TILT=0.35]
import json,sys,os,numpy as np
C=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,C);from cycle import cycle
bvh,d,out=sys.argv[1],sys.argv[2],sys.argv[3];N=int(sys.argv[4]) if len(sys.argv)>4 else 8;TILT=float(sys.argv[5]) if len(sys.argv)>5 else 0.35
if os.environ.get('CYC'):   # explicit cycle (BVH frames a,b): contact detection in cycle.py is tuned for runs
    from bvh import load
    n,Pall,ft=load(bvh);ix=lambda s:n.index(s);a_,b_=map(int,os.environ['CYC'].split(','))
    Hh=Pall[:,ix('Hips')];dd=Hh[b_]-Hh[a_];ang=np.arctan2(dd[2],dd[0]);c_,s_=np.cos(-ang),np.sin(-ang)
    Rm=np.array([[c_,0,-s_],[0,1,0],[s_,0,c_]]);Q=(Pall-Hh[:,None,:]*np.array([1,0,1]))@Rm.T
    F=np.array([Q[int(round(t))] for t in np.linspace(a_,b_,N+1)[:-1]]);dur=(b_-a_)*ft
else:n,F,dur=cycle(bvh,N);ix=lambda s:n.index(s)
j=json.load(open(f'{C}/start_idle_{d}_kp.json'));L0={p['label']:np.array([p['x'],p['y']])*256 for p in (j['keypoints'] if isinstance(j,dict) else j)}
Z0={p['label']:int(p.get('z_index',0)) for p in (j['keypoints'] if isinstance(j,dict) else j)}
front=d=='south'
# screen x: Linette's LEFT side is where her LEFT HIP is in the still; mocap z = walker's right
sx=1 if L0['LEFT HIP'][0]>L0['RIGHT HIP'][0] else -1   # +1: her left appears to the right
def P(v):  # 3D (x fwd, y up, z right) -> screen
    lat=-v[2]*sx;fwd=v[0] if front else -v[0]   # toward the camera = +
    return np.array([lat,-v[1]+TILT*fwd])
def u3(f,a,b):
    v=f[ix(b)]-f[ix(a)];return P(v)/(np.linalg.norm(v)+1e-9)   # projected unit bone (keeps foreshortening)
ln=lambda a,b:np.linalg.norm(L0[b]-L0[a])
hip0=(L0['LEFT HIP']+L0['RIGHT HIP'])/2;H0=F[:,ix('Hips'),1].mean()
legL=(ln('LEFT HIP','LEFT KNEE')+ln('LEFT KNEE','LEFT LEG'));mocL=np.linalg.norm(F[0,ix('LeftUpLeg')]-F[0,ix('LeftLeg')])+np.linalg.norm(F[0,ix('LeftLeg')]-F[0,ix('LeftFoot')])
k=legL/mocL;GROUND=max(L0['LEFT LEG'][1],L0['RIGHT LEG'][1])
seq=[]
for f in F:
    hc=hip0+np.array([0,-(f[ix('Hips'),1]-H0)*k]);J={}
    for s,S in (('LEFT','Left'),('RIGHT','Right')):
        hp=hc+(L0[s+' HIP']-hip0);kn=hp+ln(s+' HIP',s+' KNEE')*u3(f,S+'UpLeg',S+'Leg');an=kn+ln(s+' KNEE',s+' LEG')*u3(f,S+'Leg',S+'Foot')
        J[s+' HIP'],J[s+' KNEE'],J[s+' LEG']=hp,kn,an
    dh=hc-hip0
    for p in L0:
        if p not in J:J[p]=L0[p]+dh
    g=GROUND-max(J['LEFT LEG'][1],J['RIGHT LEG'][1])   # the lower foot stays on the ground
    for p in J:J[p]=J[p]+np.array([0,g])
    # nearer leg drawn in front
    zf={s:(f[ix(S+'Foot'),0]*(1 if front else -1)) for s,S in (('LEFT','Left'),('RIGHT','Right'))}
    seq.append([{'x':float(min(1,max(0,v[0]/256))),'y':float(min(1,max(0,v[1]/256))),'label':p,
                 'z_index':(1 if zf[p.split()[0]]>zf['RIGHT' if p.startswith('LEFT') else 'LEFT'] else -1) if (p.endswith('KNEE') or p.endswith(' LEG')) else Z0.get(p,0)} for p,v in J.items()])
json.dump(seq,open(out,'w'));print(d,len(seq),'frames, cycle',round(dur,2),'s')
