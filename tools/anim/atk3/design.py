# 3-hit sword combo, side view (facing east), designed as poses -> per-frame skeletons (no API calls).
# angles: 0 = straight down, 90 = forward (+x), 180 = up, -90 = back. bone lengths fixed (shins never shortened).
import json,math,sys
# usage: design.py <outdir> <east_kp.json>  - bone lengths, head/shoulder/hip offsets and z from estimate-skeleton of the east rotation
E={k['label']:(k['x']*256,k['y']*256,int(k.get('z_index',0))) for k in json.load(open(sys.argv[2]))['keypoints']}
d=lambda a,b:math.dist(E[a][:2],E[b][:2])
UA,FA=d('RIGHT SHOULDER','RIGHT ELBOW'),d('RIGHT ELBOW','RIGHT ARM')
TH,SH=d('RIGHT HIP','RIGHT KNEE'),d('RIGHT KNEE','RIGHT LEG')
HX,HY=(E['LEFT HIP'][0]+E['RIGHT HIP'][0])/2,(E['LEFT HIP'][1]+E['RIGHT HIP'][1])/2
TO=math.dist((HX,HY),E['NECK'][:2])
GY=(E['LEFT LEG'][1]+E['RIGHT LEG'][1])/2   # ankle height (feet on the 189 baseline)
def P(a,L): r=math.radians(a); return (L*math.sin(r),L*math.cos(r))
add=lambda p,q:(p[0]+q[0],p[1]+q[1])
def leg(hip,fx,bend=1):                  # 2-bone IK, knee bends forward
    ax,ay=fx,GY;dx,dy=ax-hip[0],ay-hip[1];d=min(math.hypot(dx,dy),TH+SH-0.5)
    a=math.atan2(dy,dx);c=math.acos((TH*TH+d*d-SH*SH)/(2*TH*d))
    k=(hip[0]+TH*math.cos(a-bend*c),hip[1]+TH*math.sin(a-bend*c))
    an=(hip[0]+d*math.cos(a),hip[1]+d*math.sin(a));return k,an
def pose(p):
    hip=(HX+0.4*p.get('dx',0),HY+p.get('dy',0));lean=p.get('lean',0)  # root travel kept at 40%: the game's FEELYS adds the forward lunge
    nk=add(hip,(TO*math.sin(math.radians(lean)),-TO*math.cos(math.radians(lean))))
    J={'NECK':nk}
    for l in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','LEFT SHOULDER','RIGHT SHOULDER'): J[l]=add(nk,(E[l][0]-E['NECK'][0],E[l][1]-E['NECK'][1]))
    for l in ('LEFT HIP','RIGHT HIP'): J[l]=add(hip,(E[l][0]-HX,E[l][1]-HY))
    for s in 'RL':
        S='RIGHT' if s=='R' else 'LEFT';u,f=p[s+'a']
        e=add(J[S+' SHOULDER'],P(u,UA));J[S+' ELBOW']=e;J[S+' ARM']=add(e,P(f,FA))
    for s in 'RL':
        S='RIGHT' if s=='R' else 'LEFT';k,a=leg(J[S+' HIP'],HX-0.6*p.get('dx',0)+p[s+'f']);J[S+' KNEE']=k;J[S+' LEG']=a
    J['_sw']=p.get('sw',p[ 'Ra'][1])     # sword angle (preview only)
    return J
def kp(J): return [dict(x=v[0]/256,y=v[1]/256,label=l,z_index=E[l][2]) for l,v in J.items() if l[0]!='_']
ease=lambda t:t*t*(3-2*t)
def lerp(A,B,t):
    t=ease(t);O={}
    for k in A:
        a,b=A[k],B[k]
        O[k]=[x+(y-x)*t for x,y in zip(a,b)] if isinstance(a,list) else a+(b-a)*t
    return O
# poses (exaggerated ~1.5x a normal swing; feet: Rf/Lf = ankle x offset)
R=dict(dx=0,dy=0,lean=4,Ra=[10,70],La=[20,70],Rf=0,Lf=-10,sw=110)                       # combat ready, blade forward
H1=[R,
 dict(dx=-4,dy=1,lean=-12,Ra=[195,235],La=[60,30],Rf=6,Lf=-12,sw=250),                # wind-up: blade cocked high behind head
 dict(dx=4,dy=3,lean=4,Ra=[165,140],La=[40,20],Rf=16,Lf=-12,sw=150),                  # step in, arm comes over
 dict(dx=10,dy=6,lean=24,Ra=[95,80],La=[-30,-60],Rf=24,Lf=-14,sw=90),                 # impact: arm straight forward
 dict(dx=12,dy=7,lean=30,Ra=[45,25],La=[-45,-70],Rf=24,Lf=-14,sw=20),                 # follow-through low front
 dict(dx=12,dy=7,lean=30,Ra=[42,22],La=[-45,-70],Rf=24,Lf=-14,sw=15)]                 # hold
H2=[H1[-1],
 dict(dx=8,dy=6,lean=18,Ra=[-35,-55],La=[60,90],Rf=20,Lf=-14,sw=-80),                 # blade drawn back low behind (backhand load)
 dict(dx=14,dy=4,lean=14,Ra=[60,95],La=[0,-30],Rf=20,Lf=4,sw=120),                    # rising sweep, back foot steps up
 dict(dx=20,dy=2,lean=6,Ra=[140,165],La=[-40,-60],Rf=20,Lf=30,sw=170),                # impact high front (rising slash)
 dict(dx=22,dy=3,lean=2,Ra=[175,200],La=[-50,-70],Rf=20,Lf=32,sw=210),                # follow-through overhead
 dict(dx=22,dy=3,lean=2,Ra=[178,205],La=[-50,-70],Rf=20,Lf=32,sw=212)]
H3=[H2[-1],
 dict(dx=18,dy=8,lean=-16,Ra=[200,245],La=[195,240],Rf=20,Lf=24,sw=265),              # deep crouch, both hands cocked behind head
 dict(dx=26,dy=-4,lean=6,Ra=[170,160],La=[168,158],Rf=46,Lf=22,sw=170),               # big lunge step, blade overhead
 dict(dx=36,dy=12,lean=34,Ra=[90,70],La=[86,66],Rf=52,Lf=14,sw=80),                   # cleave impact
 dict(dx=38,dy=14,lean=38,Ra=[55,40],La=[52,38],Rf=52,Lf=14,sw=40),                   # blade buried low front
 dict(dx=38,dy=14,lean=38,Ra=[54,39],La=[51,37],Rf=52,Lf=14,sw=38)]
# frames per segment: wind-up slow, swing fast, hold long (<=20 skeletons per hit)
SEG={'h1':[5,3,2,2,2],'h2':[4,3,2,2,2],'h3':[5,3,2,2,3]}
OUT={}
for n,K in (('h1',H1),('h2',H2),('h3',H3)):
    fr=[]
    for i,c in enumerate(SEG[n]):
        if i==0: fr.append(K[0])
        for j in range(c): fr.append(lerp(K[i],K[i+1],(j+1)/c))
    OUT[n]=[pose(f) for f in fr]
json.dump({n:[kp(J) for J in L] for n,L in OUT.items()},open(sys.argv[1]+'/side_kp.json','w'))
json.dump({n:[{'hand':J['RIGHT ARM'],'sw':J['_sw']} for J in L] for n,L in OUT.items()},open(sys.argv[1]+'/side_sword.json','w'))
print({n:len(L) for n,L in OUT.items()})
