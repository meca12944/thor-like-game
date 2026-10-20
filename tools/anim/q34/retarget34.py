# 3D retarget for any view (side/front/back + 3/4 se/ne): exaggerate the mocap in 3D (upper-body lean about the hips, thigh + free-arm swing amplified in the sagittal plane),
# project with the view's camera (side/front/back, slight top-down) KEEPING foreshortening, then rebuild with the character's 2D bone lengths
# (scaled by each bone's projected/true length ratio). Sword arm keeps the start-frame pose; feet grounded (<=4px flight).
import json,math,sys,numpy as np
sys.path.insert(0,'.');from cycle import cycle
bvh,kpf,out,N,VIEW=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),sys.argv[5]
SWORD=sys.argv[6];LEAN=math.radians(float(sys.argv[7]));AMP=float(sys.argv[8]);AAMP=float(sys.argv[9])
n,F,dur=cycle(bvh,N);ix=lambda s:n.index(s)
KK=json.load(open(kpf))['keypoints'];K={k['label']:np.array([k['x']*256,k['y']*256]) for k in KK};Z={k['label']:int(k.get('z_index',0)) for k in KK}
L=lambda a,b:np.linalg.norm(K[a]-K[b]);neck0=(K['LEFT SHOULDER']+K['RIGHT SHOULDER'])/2;hip0=(K['LEFT HIP']+K['RIGHT HIP'])/2
# character bone lengths: for front/back the estimate is foreshortened too, so use the larger of the two sides
LEN={'torso':np.linalg.norm(neck0-hip0),'head':np.linalg.norm(K['NOSE']-neck0),'thigh':max(L('LEFT HIP','LEFT KNEE'),L('RIGHT HIP','RIGHT KNEE')),
     'shin':max(L('LEFT KNEE','LEFT LEG'),L('RIGHT KNEE','RIGHT LEG')),'upper':max(L('LEFT SHOULDER','LEFT ELBOW'),L('RIGHT SHOULDER','RIGHT ELBOW')),'fore':max(L('LEFT ELBOW','LEFT ARM'),L('RIGHT ELBOW','RIGHT ARM'))}
GROUND=max(K['LEFT LEG'][1],K['RIGHT LEG'][1]);TILT=0.30
def rz(v,c,a):  # rotate about the lateral (z) axis through c, in the x-y (sagittal) plane
    d=v-c;ca,sa=math.cos(a),math.sin(a);return c+np.array([d[0]*ca-d[1]*sa,d[0]*sa+d[1]*ca,d[2]])
def proj(v):  # mocap: +x forward, +y up, +z right
    if VIEW=='side':return np.array([v[0],-v[1]+0.18*v[2]])
    ce,se=math.cos(ELEV),math.sin(ELEV)                            # Ys VIII-like 3D camera looking down ELEV degrees
    if VIEW=='front':return np.array([-v[2],-v[1]*ce+v[0]*se])     # toward the camera: forward = down the screen
    if VIEW in ('se','ne'):  # 3/4 view: ground forward f, character right = (-f.y, f.x) in (screen-right, toward-camera) coords
        f=(0.7071,0.7071) if VIEW=='se' else (0.7071,-0.7071);r=(-f[1],f[0])
        wx=v[0]*f[0]+v[2]*r[0];wy=v[0]*f[1]+v[2]*r[1];return np.array([wx,-v[1]*ce+wy*se])
    return np.array([v[2],-v[1]*ce-v[0]*se])                       # away from the camera: forward = up the screen
def ex(f):
    f=f.copy();hp=f[ix('Hips')]
    for S in ('Left','Right'):  # thigh swing x AMP (knee/foot follow rigidly)
        h=f[ix(S+'UpLeg')];k=f[ix(S+'Leg')];a0=math.atan2(k[0]-h[0],-(k[1]-h[1]));da=a0*(AMP-1)
        for j in (S+'Leg',S+'Foot',S+'ToeBase'):
            if j in n:f[ix(j)]=rz(f[ix(j)],h,-da)
    for S in ('Left','Right'):  # free-arm swing x AAMP
        if S.upper()==SWORD:continue
        s=f[ix(S+'Arm')];e=f[ix(S+'ForeArm')];a0=math.atan2(e[0]-s[0],-(e[1]-s[1]));da=a0*(AAMP-1)
        for j in (S+'ForeArm',S+'Hand'):f[ix(j)]=rz(f[ix(j)],s,-da)
    up=[j for j in n if not any(t in j for t in ('UpLeg','Leg','Foot','Toe','Hips'))]
    for j in up:f[ix(j)]=rz(f[ix(j)],hp,-LEAN)   # lean forward (+x) about the hips
    return f
def bone(f,a,b,length):
    v3=f[ix(b)]-f[ix(a)];p=proj(f[ix(b)])-proj(f[ix(a)]);r=np.linalg.norm(p)/(np.linalg.norm(v3)+1e-9)
    return p/(np.linalg.norm(p)+1e-9)*length*r
side_sign={'LEFT':'Left','RIGHT':'Right'}
f0=F.copy();ELEV=math.radians(float(sys.argv[12]) if len(sys.argv)>12 else 35);LIFT=float(sys.argv[10]) if len(sys.argv)>10 else 0.0;BOB=float(sys.argv[11]) if len(sys.argv)>11 else 1.0
F=np.array([ex(f) for f in F]);mh=F[:,ix('Hips'),1];bob=BOB*(mh-mh.mean())*LEN['torso']/np.linalg.norm(F[0,ix('Neck')]-F[0,ix('Hips')])
frames=[]
for i,f in enumerate(F):
    J={};H=hip0.copy();H[1]-=bob[i]
    for s,S in side_sign.items():
        hp=H+(K[s+' HIP']-hip0)
        if VIEW=='side' or LIFT==0:
            kn=hp+bone(f,S+'UpLeg',S+'Leg',LEN['thigh']*1.08);an=kn+bone(f,S+'Leg',S+'Foot',LEN['shin']*1.08)
        else:
            h3,k3,a3=f0[i][ix(S+'UpLeg')],f0[i][ix(S+'Leg')],f0[i][ix(S+'Foot')]
            th=math.atan2(k3[0]-h3[0],-(k3[1]-h3[1]))                       # thigh forward angle (raw mocap)
            v1=k3-h3;v2=a3-k3;bend=math.acos(max(-1,min(1,np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))))
            lift=max(0,math.sin(th))*LIFT;tx=(K[s+' KNEE']-K[s+' HIP'])[0]*0.5
            kn=hp+np.array([tx,LEN['thigh']*1.08*(1-lift)])
            an=kn+np.array([0,LEN['shin']*1.08*(1-0.45*(1-math.cos(bend)))])
        J[s+' HIP'],J[s+' KNEE'],J[s+' LEG']=hp,kn,an
    nk=H+bone(f,'Hips','Neck',LEN['torso']);J['NECK']=nk
    for s,S in side_sign.items():
        sh=nk+(K[s+' SHOULDER']-neck0);J[s+' SHOULDER']=sh
        if s==SWORD:J[s+' ELBOW']=sh+(K[s+' ELBOW']-K[s+' SHOULDER']);J[s+' ARM']=sh+(K[s+' ARM']-K[s+' SHOULDER'])
        else:el=sh+bone(f,S+'Arm',S+'ForeArm',LEN['upper']);J[s+' ELBOW']=el;J[s+' ARM']=el+bone(f,S+'ForeArm',S+'Hand',LEN['fore'])
    hd=nk+bone(f,'Neck','Head',LEN['head']);dh=hd-K['NOSE']
    for p in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):J[p]=K[p]+dh
    lowest=max(J['LEFT LEG'][1],J['RIGHT LEG'][1]);air=max(0,GROUND-lowest);shy=GROUND-lowest-min(air,4)
    frames.append([{'x':float(min(1,max(0,v[0]/256))),'y':float(min(1,max(0,(v[1]+shy)/256))),'label':k,'z_index':Z.get(k,0)} for k,v in J.items()])
json.dump(frames,open(out,'w'));print(VIEW,'sword',SWORD,{k:round(v) for k,v in LEN.items()})
