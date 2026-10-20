# new hero combo (owner 2026-10-20): 1 thrust, 2 from the thrust lift the sword up, 3 big two-handed overhead -> downward cut.
# Side view facing +x, sword in the RIGHT (near) hand. Bone lengths from the in-game east idle keypoints; poses = joint angles
# (0 = straight down, 90 = forward +x, 180 = up), interpolated in angle space so every frame keeps the same proportions.
import json,math,numpy as np
K={p['label']:np.array([p['x']*256,p['y']*256]) for p in json.load(open('skel/east_idle_kp.json'))['keypoints']}
Z={p['label']:float(p.get('z_index',0)) for p in json.load(open('skel/east_idle_kp.json'))['keypoints']}
L=lambda a,b:float(np.linalg.norm(K[a]-K[b]))
hip0=(K['LEFT HIP']+K['RIGHT HIP'])/2;neck0=K['NECK']
LEN=dict(torso=float(np.linalg.norm(neck0-hip0)),uR=L('RIGHT SHOULDER','RIGHT ELBOW'),fR=L('RIGHT ELBOW','RIGHT ARM'),uL=L('LEFT SHOULDER','LEFT ELBOW'),fL=L('LEFT ELBOW','LEFT ARM'),
         tR=L('RIGHT HIP','RIGHT KNEE'),sR=L('RIGHT KNEE','RIGHT LEG'),tL=L('LEFT HIP','LEFT KNEE'),sL=L('LEFT KNEE','LEFT LEG'))
GROUND=max(K['LEFT LEG'][1],K['RIGHT LEG'][1])
def V(a):r=math.radians(a);return np.array([math.sin(r),math.cos(r)])
def ang(v):return math.degrees(math.atan2(v[0],v[1]))
# idle angles measured from the kp (so pose 'idle' reproduces the first frame)
IDLE=dict(dx=0,dy=0,torso=ang(neck0-hip0),uR=ang(K['RIGHT ELBOW']-K['RIGHT SHOULDER']),fR=ang(K['RIGHT ARM']-K['RIGHT ELBOW']),
          uL=ang(K['LEFT ELBOW']-K['LEFT SHOULDER']),fL=ang(K['LEFT ARM']-K['LEFT ELBOW']),tR=ang(K['RIGHT KNEE']-K['RIGHT HIP']),sR=ang(K['RIGHT LEG']-K['RIGHT KNEE']),
          tL=ang(K['LEFT KNEE']-K['LEFT HIP']),sL=ang(K['LEFT LEG']-K['LEFT KNEE']),twoh=0)
def pose(**kw):p=dict(IDLE);p.update(kw);return p
P=dict(
 idle=pose(),
 # hit 1: thrust
 h1_wind=pose(dx=-4,dy=4,torso=172,uR=-35,fR=55,uL=20,fL=60,tR=30,sR=-5,tL=-28,sL=-38),
 h1_thrust=pose(dx=12,dy=11,torso=158,uR=92,fR=90,uL=-35,fL=-55,tR=62,sR=8,tL=-58,sL=-72),
 h1_hold=pose(dx=13,dy=11,torso=160,uR=90,fR=88,uL=-32,fL=-50,tR=60,sR=6,tL=-56,sL=-70),
 # hit 2: from the thrust, lift the sword up
 h2_mid=pose(dx=10,dy=7,torso=170,uR=130,fR=150,uL=-20,fL=-30,tR=50,sR=4,tL=-45,sL=-60),
 h2_up=pose(dx=8,dy=4,torso=178,uR=160,fR=178,uL=-10,fL=-15,tR=40,sR=0,tL=-38,sL=-50),
 # hit 3: two hands, overhead -> big downward cut
 h3_wind=pose(dx=2,dy=3,torso=182,uR=172,fR=205,uL=168,fL=200,tR=30,sR=-4,tL=-30,sL=-42,twoh=1),
 h3_top=pose(dx=8,dy=4,torso=178,uR=160,fR=150,uL=157,fL=147,tR=40,sR=0,tL=-38,sL=-50,twoh=1),
 h3_mid=pose(dx=14,dy=7,torso=170,uR=122,fR=100,uL=120,fL=98,tR=52,sR=3,tL=-48,sL=-62,twoh=1),
 h3_low=pose(dx=18,dy=11,torso=158,uR=88,fR=66,uL=86,fL=64,tR=62,sR=6,tL=-56,sL=-70,twoh=1),
 h3_cut=pose(dx=20,dy=14,torso=150,uR=62,fR=40,uL=60,fL=38,tR=70,sR=10,tL=-62,sL=-78,twoh=1),
 h3_follow=pose(dx=22,dy=15,torso=146,uR=30,fR=8,uL=28,fL=6,tR=72,sR=12,tL=-64,sL=-80,twoh=1),
 h3_end=pose(dx=18,dy=10,torso=155,uR=25,fR=20,uL=22,fL=18,tR=60,sR=8,tL=-55,sL=-68,twoh=1),
)
def joints(p):
    H=hip0+np.array([p['dx'],p['dy']]);J={}
    J['LEFT HIP']=H+(K['LEFT HIP']-hip0);J['RIGHT HIP']=H+(K['RIGHT HIP']-hip0)
    for s,t,sh in (('RIGHT','tR','sR'),('LEFT','tL','sL')):
        kn=J[s+' HIP']+LEN[t]*V(p[t]);J[s+' KNEE']=kn;J[s+' LEG']=kn+LEN[sh]*V(p[sh])
    nk=H+LEN['torso']*V(p['torso']);J['NECK']=nk;rot=math.radians(p['torso']-IDLE['torso'])
    def R(v):c,s=math.cos(rot),math.sin(rot);return np.array([c*v[0]+s*v[1],-s*v[0]+c*v[1]])
    for lab in ('LEFT SHOULDER','RIGHT SHOULDER'):J[lab]=nk+R(K[lab]-neck0)
    for lab in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):J[lab]=nk+(K[lab]-neck0)   # head keeps looking forward
    for s,u,f in (('RIGHT','uR','fR'),('LEFT','uL','fL')):
        el=J[s+' SHOULDER']+LEN[u]*V(p[u]);J[s+' ELBOW']=el;J[s+' ARM']=el+LEN[f]*V(p[f])
    if p['twoh']:J['LEFT ARM']=J['RIGHT ARM']+np.array([-2,1])   # both hands on the hilt
    low=max(J['LEFT LEG'][1],J['RIGHT LEG'][1]);d=GROUND-low   # feet stay on the ground
    for k in J:J[k]=J[k]+np.array([0,d])
    return J
def lerp(a,b,t):
    o={}
    for k in a:
        if k=='twoh':o[k]=b[k] if t>=.5 else a[k];continue
        da=b[k]-a[k]
        if k not in('dx','dy'):da=(da+180)%360-180
        o[k]=a[k]+da*t
    return o
ease=lambda t:t*t*(3-2*t)
def seq(keys,counts):
    out=[]
    for (a,b),n in zip(zip(keys,keys[1:]),counts):
        for i in range(n):out.append(lerp(P[a],P[b],ease(i/n)))
    out.append(P[keys[-1]]);return out
CLIPS={'hit1':seq(['idle','h1_wind','h1_thrust','h1_hold'],[5,4,5]),
       'hit2':seq(['h1_hold','h2_mid','h2_up'],[7,7]),
       'hit3':seq(['h2_up','h3_wind','h3_top','h3_mid','h3_low','h3_cut','h3_follow'],[3,2,2,2,2,3])}
def kp(p):return [{'x':float(min(1,max(0,v[0]/256))),'y':float(min(1,max(0,v[1]/256))),'label':k,'z_index':int(Z.get(k,0))} for k,v in joints(p).items()]
if __name__=='__main__':
    from PIL import Image,ImageDraw
    B=[('NECK','LEFT HIP'),('NECK','RIGHT HIP'),('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG'),('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),('NECK','NOSE'),('LEFT SHOULDER','RIGHT SHOULDER')]
    rows=[]
    for name,fr in CLIPS.items():
        json.dump([kp(p) for p in fr],open(f'newatk/{name}_kp.json','w'));print(name,len(fr),'frames')
        o=Image.new('RGB',(len(fr)*90,150),(30,30,40));d=ImageDraw.Draw(o)
        for i,p in enumerate(fr):
            J=joints(p);T=lambda q:(q[0]-128+45+i*90,q[1]-60)
            for a,b in B:d.line([T(J[a]),T(J[b])],fill=(255,110,110) if 'RIGHT' in a+b else (180,210,255),width=2)
            # sword in the right hand: along the forearm direction, 55 px
            hd=J['RIGHT ARM'];fo=hd-J['RIGHT ELBOW'];fo=fo/np.linalg.norm(fo);d.line([T(hd),T(hd+fo*55)],fill=(255,255,120),width=2)
        rows.append(o)
    W=max(r.width for r in rows);o=Image.new('RGB',(W,150*len(rows)),(30,30,40))
    for i,r in enumerate(rows):o.paste(r,(0,150*i))
    o.save('newatk/skel_preview.png')
