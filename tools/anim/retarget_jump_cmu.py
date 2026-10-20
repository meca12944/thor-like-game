# CMU running jump -> 15 side-view skeletons on the hero's own 2D bone lengths (facing +x = east).
# window: 2 run steps before take-off .. landing; bone DIRECTIONS from the mocap, LENGTHS from the start-frame kp; sword arm (RIGHT)
# keeps its trailing start pose; hips stay near standing height in the sprite (flight height is the game's z), only a little rise/tuck kept.
# usage: bvh kp out [LIFT=0.35] [LEAN_DEG=0]
import json,math,sys,numpy as np
sys.path.insert(0,'.');import bvh
fn,kpf,out=sys.argv[1:4];LIFT=float(sys.argv[4]) if len(sys.argv)>4 else 0.35;LEAN=math.radians(float(sys.argv[5]) if len(sys.argv)>5 else 0);N=15
n,P,ft=bvh.load(fn);ix=n.index
lt,rt=P[:,ix('LeftToeBase'),1],P[:,ix('RightToeBase'),1];g=np.percentile(np.minimum(lt,rt),5);air=(lt>g+3)&(rt>g+3)
best=(0,0,0);i=0
while i<len(air):
    if air[i]:
        j=i
        while j<len(air) and air[j]:j+=1
        if j-i>best[0]:best=(j-i,i,j)
        i=j
    else:i+=1
L,a,b=best;fps=1/ft;a0=int(a-0.22*fps);b0=int(b+0.12*fps)
idx=np.linspace(a0,b0,N).round().astype(int);W=P[idx].copy()
H=W[:,ix('Hips')].copy();d=P[b0,ix('Hips')]-P[a0,ix('Hips')];ang=math.atan2(d[2],d[0]);c,s=math.cos(-ang),math.sin(-ang)
Rm=np.array([[c,0,-s],[0,1,0],[s,0,c]]);Q=(W-H[:,None,:]*np.array([1,0,1]))@Rm.T
K={k['label']:np.array([k['x']*256,k['y']*256]) for k in (lambda j:j['keypoints'] if isinstance(j,dict) else j)(json.load(open(kpf)))}
Z={k['label']:int(k.get('z_index',0)) for k in (lambda j:j['keypoints'] if isinstance(j,dict) else j)(json.load(open(kpf)))}
Ln=lambda p,q:np.linalg.norm(K[p]-K[q]);neck0=K['NECK'];hip0=(K['LEFT HIP']+K['RIGHT HIP'])/2
LEN={'torso':np.linalg.norm(neck0-hip0),'thigh':(Ln('LEFT HIP','LEFT KNEE')+Ln('RIGHT HIP','RIGHT KNEE'))/2,'shin':(Ln('LEFT KNEE','LEFT LEG')+Ln('RIGHT KNEE','RIGHT LEG'))/2,
     'upper':Ln('LEFT SHOULDER','LEFT ELBOW'),'fore':Ln('LEFT ELBOW','LEFT ARM')}
GROUND=max(K['LEFT LEG'][1],K['RIGHT LEG'][1]);standY=Q[0,ix('Hips'),1]
bh=P[0,ix('Head'),1]-g
def P2(v):return np.array([v[0],-v[1]+0.18*v[2]])
def rot(v,t):c,s=math.cos(t),math.sin(t);return np.array([c*v[0]-s*v[1],s*v[0]+c*v[1]])
def dirv(f,p,q):dd=P2(f[ix(q)])-P2(f[ix(p)]);return dd/(np.linalg.norm(dd)+1e-9)
frames=[]
for i,f in enumerate(Q):
    J={};rise=(f[ix('Hips'),1]-standY)/bh*(GROUND-K['NOSE'][1])*LIFT;Hc=hip0-np.array([0,rise])
    for S,lab in (('Left','LEFT'),('Right','RIGHT')):
        hp=Hc+(K[lab+' HIP']-hip0);kn=hp+LEN['thigh']*dirv(f,S+'UpLeg',S+'Leg');an=kn+LEN['shin']*dirv(f,S+'Leg',S+'Foot');J[lab+' HIP'],J[lab+' KNEE'],J[lab+' LEG']=hp,kn,an
    tv=rot(dirv(f,'Hips','Neck'),LEAN);nk=Hc+LEN['torso']*tv;J['NECK']=nk;tilt=math.atan2(tv[0],-tv[1])-math.atan2(*(neck0-hip0)*np.array([1,-1]))
    for lab in ('LEFT','RIGHT'):J[lab+' SHOULDER']=nk+(K[lab+' SHOULDER']-neck0)
    # free arm (LEFT, near side) follows the mocap; sword arm keeps its trailing pose, turned with the trunk
    sh=J['LEFT SHOULDER'];el=sh+LEN['upper']*dirv(f,'LeftArm','LeftForeArm');J['LEFT ELBOW']=el;J['LEFT ARM']=el+LEN['fore']*dirv(f,'LeftForeArm','LeftHand')
    sh=J['RIGHT SHOULDER'];J['RIGHT ELBOW']=sh+(K['RIGHT ELBOW']-K['RIGHT SHOULDER']);J['RIGHT ARM']=sh+(K['RIGHT ARM']-K['RIGHT SHOULDER'])
    dh=nk-neck0
    for p in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):J[p]=K[p]+dh
    low=max(J['LEFT LEG'][1],J['RIGHT LEG'][1]);onground=not air[idx[i]]
    if onground or low>GROUND:
        for k in J:J[k]=J[k]+np.array([0,GROUND-low])
    frames.append([{'x':float(min(1,max(0,v[0]/256))),'y':float(min(1,max(0,v[1]/256))),'label':k,'z_index':Z.get(k,0)} for k,v in J.items()])
json.dump(frames,open(out,'w'));print('window',a0,b0,'air frames',[int(air[k]) for k in idx],'take-off..land',a,b)
