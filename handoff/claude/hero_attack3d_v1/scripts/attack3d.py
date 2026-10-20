# procedural 3D sword combo on the character's own 3D rest skeleton, projected per view (east / se / ne), applied as deltas
# to the start frame's estimated 2D skeleton -> 15-frame keypoint sequences for animate-with-skeleton-v3
import json,math,sys,numpy as np
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
S3=json.load(open(P+'q34/skeletons.json'))['3d']['keypoints']
c=np.array(S3['NECK']);foot=min(S3['LEFT LEG'][2],S3['RIGHT LEG'][2])
R0={k:np.array([-(v[1]-c[1]),v[2]-foot,-(v[0]-c[0])]) for k,v in S3.items()}  # x forward, y up, z right
LBL=list(R0)
d=lambda a,b:np.linalg.norm(R0[a]-R0[b])
UP_L,FO_L=d('LEFT SHOULDER','LEFT ELBOW'),d('LEFT ELBOW','LEFT ARM');TH_L,SH_L=d('LEFT HIP','LEFT KNEE'),d('LEFT KNEE','LEFT LEG')
HIPC=(R0['LEFT HIP']+R0['RIGHT HIP'])/2
SW='LEFT';FR='RIGHT' if SW=='LEFT' else 'LEFT'   # sword hand (all estimates label the sword wrist LEFT); free hand
SWS=1 if R0[SW+' SHOULDER'][2]>0 else -1         # which side (+z right) the sword shoulder sits on
def roty(v,a):ca,sa=math.cos(a),math.sin(a);return np.array([v[0]*ca+v[2]*sa,v[1],-v[0]*sa+v[2]*ca])
def rotz(v,a):ca,sa=math.cos(a),math.sin(a);return np.array([v[0]*ca-v[1]*sa,v[0]*sa+v[1]*ca,v[2]])  # +a pitches the top forward
def ik(s,h,la,lb,pole):
    dv=h-s;dl=min(np.linalg.norm(dv),la+lb-1e-4);u=dv/(np.linalg.norm(dv)+1e-9);h=s+u*dl
    x=(la*la-lb*lb+dl*dl)/(2*dl);y=math.sqrt(max(0,la*la-x*x));p=pole-np.dot(pole,u)*u;p/=np.linalg.norm(p)+1e-9
    return s+u*x+p*y,h
def pose(q):
    """q: lean(deg fwd), twist(deg, + turns the chest toward the sword side), crouch, step, th(swing deg), tilt(plane deg), drop(deg), reach"""
    J={}
    hip=HIPC+np.array([0,-q['crouch']*(TH_L+SH_L),0])+np.array([q['step']*0.35*(TH_L+SH_L),0,0])
    tw=math.radians(q['twist'])*SWS;ln=-math.radians(q['lean'])
    def up(p): return hip+rotz(roty(p-HIPC,tw),ln)
    for k in LBL:
        if 'HIP' in k or 'KNEE' in k or 'LEG' in k: continue
        J[k]=up(R0[k])
    # sword hand on a swing circle around its shoulder (torso-local, then twisted+leaned with the torso)
    th=math.radians(q['th']);tl=math.radians(q['tilt']);dr=math.radians(q['drop'])
    a=np.array([math.cos(dr),-math.sin(dr),0]);b=np.array([0,math.sin(tl),math.cos(tl)*SWS])
    r=(UP_L+FO_L)*q['reach'];hl=R0[SW+' SHOULDER']+r*(math.cos(th)*a+math.sin(th)*b)
    el,hd=ik(J[SW+' SHOULDER'],up(hl),UP_L,FO_L,rotz(roty(np.array([-0.2,-1,0.5*SWS]),tw),ln))
    J[SW+' ELBOW'],J[SW+' ARM']=el,hd
    # free arm swings opposite, small
    fa=math.radians(-q['th']*0.35);fl=R0[FR+' SHOULDER']+(UP_L+FO_L)*0.8*np.array([0.35*math.cos(fa),-0.8,-0.35*math.sin(fa)*SWS])
    el,hd=ik(J[FR+' SHOULDER'],up(fl),UP_L,FO_L,np.array([-1,0,-0.3*SWS]));J[FR+' ELBOW'],J[FR+' ARM']=el,hd
    # legs: front foot (free side) steps forward, back foot planted, knees bend to absorb the crouch
    for s in ('LEFT','RIGHT'):
        h=hip+(R0[s+' HIP']-HIPC);f=R0[s+' LEG'].copy()
        if s==FR: f=f+np.array([q['step']*0.7*(TH_L+SH_L),0,0])
        else: f=f+np.array([-q['step']*0.15*(TH_L+SH_L),0,0])
        kn,an=ik(h,f,TH_L,SH_L,np.array([1,0,0]));J[s+' HIP'],J[s+' KNEE'],J[s+' LEG']=h,kn,an
    return J
EASE=lambda x:x*x*(3-2*x)
def seq(keys,n=15):
    ts=[k[0] for k in keys];out=[]
    for i in range(n):
        t=i/(n-1);j=max(0,min(len(ts)-2,sum(1 for x in ts if x<=t)-1));u=(t-ts[j])/(ts[j+1]-ts[j]);u=EASE(min(1,max(0,u)))
        out.append({k:keys[j][1][k]+(keys[j+1][1][k]-keys[j][1][k])*u for k in keys[j][1]})
    return out
def Q(lean,twist,crouch,step,th,tilt,drop,reach=0.95):return dict(lean=lean,twist=twist,crouch=crouch,step=step,th=th,tilt=tilt,drop=drop,reach=reach)
# lean x1.4 (owner: +40%). th: + = toward the sword side; hit1 ends on the left, hit2 on the right, hit3 = 80 deg plane, big
REST=Q(6,0,0,0,40,60,0,0.8)
COMBO={  # th: 0 = straight ahead, + = toward the sword side (180 = behind), - = across the body
 'hit1':[(0,REST),(0.24,Q(10,30,0.04,0,150,12,-5,0.9)),(0.4,Q(16,15,0.06,0.2,90,12,-8)),(0.56,Q(28,-30,0.09,0.45,-20,12,-8,1.0)),
         (0.72,Q(28,-50,0.09,0.45,-95,12,-5)),(1,Q(16,-25,0.04,0.25,-70,25,15,0.85))],
 'hit2':[(0,REST),(0.24,Q(10,-40,0.04,0,-100,12,-5,0.85)),(0.4,Q(16,-20,0.06,0.2,-50,12,-8)),(0.56,Q(28,30,0.09,0.45,40,12,-8,1.0)),
         (0.72,Q(28,50,0.09,0.45,130,12,-5)),(1,Q(16,20,0.04,0.25,90,25,15,0.85))],
 'hit3':[(0,REST),(0.26,Q(2,30,0.05,0,165,80,0,1.0)),(0.42,Q(12,20,0.08,0.15,120,80,0,1.0)),(0.6,Q(34,-20,0.13,0.55,-10,80,0,1.0)),
         (0.78,Q(34,-30,0.13,0.55,-55,80,0,1.0)),(1,Q(18,-10,0.06,0.3,-35,60,10,0.85))]}
def proj(v,view,el=math.radians(35)):
    ce,se=math.cos(el),math.sin(el)
    if view=='east':f,r=(1,0),(0,1)
    elif view=='se':f=(0.7071,0.7071);r=(-f[1],f[0])
    else:f=(0.7071,-0.7071);r=(-f[1],f[0])
    wx=v[0]*f[0]+v[2]*r[0];wy=v[0]*f[1]+v[2]*r[1];return np.array([wx,-v[1]*ce+wy*se]),wy
if __name__=='__main__':
    view,kpf,out,name=sys.argv[1:5]
    KK=json.load(open(kpf))['keypoints'];K={k['label']:np.array([k['x']*256,k['y']*256]) for k in KK}
    rest=pose(REST);hc=lambda J:(J['LEFT HIP']+J['RIGHT HIP'])/2
    scale=np.linalg.norm(K['NECK']-(K['LEFT HIP']+K['RIGHT HIP'])/2)/np.linalg.norm(proj(rest['NECK'],view)[0]-proj(hc(rest),view)[0])
    P0={k:proj(v,view)[0]*scale for k,v in rest.items()}
    fr=[]
    for q in seq(COMBO[name]):
        J=pose(q);D0={k:proj(v,view) for k,v in J.items()};nk=D0['NECK'][1]
        fr.append([{'x':float((K[k][0]+D0[k][0][0]*scale-P0[k][0])/256),'y':float((K[k][1]+D0[k][0][1]*scale-P0[k][1])/256),'label':k,
                    'z_index':int(max(-3,min(3,round((D0[k][1]-nk)*12))))} for k in LBL])
    json.dump(fr,open(out,'w'));print(view,name,len(fr),'scale',round(scale,1))
