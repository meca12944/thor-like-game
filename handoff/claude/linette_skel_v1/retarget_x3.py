# retarget a CMU mocap cycle onto the character's estimated 2D skeleton (side view, facing +x = east):
# bone DIRECTIONS from the mocap (projected), bone LENGTHS from the character; sword arm keeps the start-frame pose; feet grounded; mocap hip bob kept (scaled)
import json,math,sys,numpy as np
sys.path.insert(0,'.');from cycle import cycle
bvh,kpf,out,N=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]);SWORD=sys.argv[5] if len(sys.argv)>5 else 'RIGHT'
LEAN=math.radians(float(sys.argv[6]) if len(sys.argv)>6 else 0);AMP=float(sys.argv[7]) if len(sys.argv)>7 else 1.0;AAMP=float(sys.argv[8]) if len(sys.argv)>8 else 1.0
n,F,dur=cycle(bvh,N);ix=lambda s:n.index(s)
K={k['label']:np.array([k['x']*256,k['y']*256]) for k in json.load(open(kpf))['keypoints']};Z={k['label']:int(k.get('z_index',0)) for k in json.load(open(kpf))['keypoints']}
L=lambda a,b:np.linalg.norm(K[a]-K[b])
neck0=(K['LEFT SHOULDER']+K['RIGHT SHOULDER'])/2;hip0=(K['LEFT HIP']+K['RIGHT HIP'])/2
LEN={'torso':np.linalg.norm(neck0-hip0),'head':np.linalg.norm(K['NOSE']-neck0),'thigh':(L('LEFT HIP','LEFT KNEE')+L('RIGHT HIP','RIGHT KNEE'))/2,'shin':(L('LEFT KNEE','LEFT LEG')+L('RIGHT KNEE','RIGHT LEG'))/2,
     'upper':(L('LEFT SHOULDER','LEFT ELBOW')+L('RIGHT SHOULDER','RIGHT ELBOW'))/2,'fore':(L('LEFT ELBOW','LEFT ARM')+L('RIGHT ELBOW','RIGHT ARM'))/2}
GROUND=max(K['LEFT LEG'][1],K['RIGHT LEG'][1])
def P2(v):return np.array([v[0],-v[1]+0.18*v[2]])   # side view, slight top-down: screen y down, near side (z) a bit lower
def dirv(f,a,b):d=P2(f[ix(b)])-P2(f[ix(a)]);return d/(np.linalg.norm(d)+1e-9)
def rotv(v,a):c,s_=math.cos(a),math.sin(a);return np.array([v[0]*c-v[1]*s_,v[0]*s_+v[1]*c])
DOWN=np.array([0.0,1.0])
def legdir(f,a,b):  # amplify the swing angle away from straight down
    d=dirv(f,a,b);ang=math.atan2(d[0],d[1]);ang*=AMP;return np.array([math.sin(ang),math.cos(ang)])
mh=F[:,ix('Hips'),1];bob=(mh-mh.mean())/np.ptp([F[0,ix('Hips'),1],F[0,ix('Neck'),1]])*LEN['torso']*0.9
frames=[]
for i,f in enumerate(F):
    J={};H=hip0.copy();H[1]-=bob[i]
    for s,S in (('LEFT','Left'),('RIGHT','Right')):
        hp=H+(K[s+' HIP']-hip0);kn=hp+LEN['thigh']*1.08*legdir(f,S+'UpLeg',S+'Leg');an=kn+LEN['shin']*1.08*dirv(f,S+'Leg',S+'Foot')
        J[s+' HIP'],J[s+' KNEE'],J[s+' LEG']=hp,kn,an
    nk=H+LEN['torso']*dirv(f,'Hips','Neck');J['NECK']=nk
    for s,S in (('LEFT','Left'),('RIGHT','Right')):
        sh=nk+(K[s+' SHOULDER']-neck0);J[s+' SHOULDER']=sh
        if s==SWORD:J[s+' ELBOW']=sh+(K[s+' ELBOW']-K[s+' SHOULDER']);J[s+' ARM']=sh+(K[s+' ARM']-K[s+' SHOULDER'])
        else:
            du=dirv(f,S+'Arm',S+'ForeArm');a=math.atan2(du[0],du[1])*AAMP;du=np.array([math.sin(a),math.cos(a)])
            el=sh+LEN['upper']*du;J[s+' ELBOW']=el;J[s+' ARM']=el+LEN['fore']*dirv(f,S+'ForeArm',S+'Hand')
    hd=nk+LEN['head']*dirv(f,'Neck','Head');dh=hd-K['NOSE']
    for p in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):J[p]=K[p]+dh
    for k in list(J):
        if not any(t in k for t in ('HIP','KNEE','LEG')):J[k]=H+rotv(J[k]-H,LEAN)
    g=GROUND-max(J['LEFT LEG'][1],J['RIGHT LEG'][1])
    if g<0 or i==0 or True:
        for k in J:J[k]=J[k]+np.array([0,min(0,g) if False else g*0+ (g if g<0 else min(g,0))])
    lowest=max(J['LEFT LEG'][1],J['RIGHT LEG'][1]);air=max(0,GROUND-lowest)
    sh=GROUND-lowest-min(air,4)   # touch the ground unless the mocap is clearly airborne (keep up to 4px of flight)
    frames.append([{'x':float(min(1,max(0,v[0]/256))),'y':float(min(1,max(0,(v[1]+sh)/256))),'label':k,'z_index':Z.get(k,0)} for k,v in J.items()])
json.dump(frames,open(out,'w'));print('cycle',round(dur,3),'s; lengths',{k:round(v) for k,v in LEN.items()})
