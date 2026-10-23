# Linette running jump from the HERO's own rjump skeleton (handoff/claude/hero_runjump_v1/skeleton_east.json, CMU 127_25 retarget, 15 frames)
# (owner 10-20: "스켈레톤 주인공꺼 다시 불러와"). Bone directions = hero skeleton, bone lengths = Linette's run frame 0, hips move by the hero's
# hip offset * 117/124, both arms keep Linette's run pose (arms back), turned with the trunk. usage: rjump_from_heroskel.py <hero_skel> <first i> <last i> <out>
import json,sys,math,numpy as np,os
C=os.path.dirname(os.path.abspath(__file__));hs,a,b,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
Hs=[{p['label']:np.array([p['x'],p['y']])*256 for p in f} for f in json.load(open(hs))]
L0=json.load(open(C+'/kp_run_east_back.json'))[0];K={p['label']:np.array([p['x'],p['y']])*256 for p in L0};Z={p['label']:int(p.get('z_index',0)) for p in L0}
S=117/124;hip=lambda J:(J['LEFT HIP']+J['RIGHT HIP'])/2;h0=hip(Hs[a]);k0=hip(K)
ln=lambda J,p,q:np.linalg.norm(J[q]-J[p]);u=lambda J,p,q:(J[q]-J[p])/(ln(J,p,q)+1e-9)
LEN={(p,q):ln(K,p,q) for p,q in [('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG')]}
tor=np.linalg.norm(K['NECK']-k0);ang=lambda v:math.atan2(v[0],-v[1]);t0=ang(K['NECK']-k0)
def rot(v,t):c,s=math.cos(t),math.sin(t);return np.array([c*v[0]-s*v[1],s*v[0]+c*v[1]])
seq=[]
for i in range(a,b+1):
    H=Hs[i];J={};hc=k0+S*(hip(H)-h0)
    for s in ('LEFT','RIGHT'):
        hp=hc+(K[s+' HIP']-k0);kn=hp+LEN[(s+' HIP',s+' KNEE')]*u(H,s+' HIP',s+' KNEE');an=kn+LEN[(s+' KNEE',s+' LEG')]*u(H,s+' KNEE',s+' LEG')
        J[s+' HIP'],J[s+' KNEE'],J[s+' LEG']=hp,kn,an
    tv=(H['NECK']-hip(H));tv/=np.linalg.norm(tv);nk=hc+tor*tv;J['NECK']=nk;dt=ang(tv)-t0
    for p in ('LEFT SHOULDER','RIGHT SHOULDER','LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM','NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):
        J[p]=nk+rot(K[p]-K['NECK'],dt)
    seq.append([{'x':float(min(1,max(0,v[0]/256))),'y':float(min(1,max(0,v[1]/256))),'label':k,'z_index':Z.get(k,0)} for k,v in J.items()])
json.dump(seq,open(out,'w'));print(len(seq),'frames')
