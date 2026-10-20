# True front (↓, facing the viewer) / back (↑) attacks, two approaches (owner 2026-10-20 "C D 둘다"):
#  C = "3D mannequin": the side thrust skeletons are lifted to 3D (forward = toward/away from the camera) and projected for the low
#      top-down camera: forward dx -> screen y (+0.45 dx toward the viewer, -0.45 away) plus a little lateral drift to the sword side,
#      so arms shorten (foreshortening) instead of swinging sideways. Torso width stays the front/back art's.
#  D = front slash: the sword hand sweeps across the body in front (sword side high -> opposite hip low), short step; the code adds the
#      down/up trail. Built directly in the front/back skeleton.
# sword arm = LEFT label in both rot_south / rot_north estimates (PixelLab draws the sword in the screen-right hand facing us).
# usage: updown.py <side_kp.json (thrust, tucked off-hand)> <s_kp.json> <n_kp.json> <outdir>
import json,sys,math
side,skp,nkp,out=sys.argv[1:5]
L=lambda p:{k['label']:(k['x']*256,k['y']*256,int(k.get('z_index',0))) for k in json.load(open(p))['keypoints']}
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT')
sub=lambda a,b:(a[0]-b[0],a[1]-b[1]);add=lambda a,b:(a[0]+b[0],a[1]+b[1])
mid=lambda F,a,b:((F[a][0]+F[b][0])/2,(F[a][1]+F[b][1])/2)
def dump(seq,Z,name): json.dump([[{'x':v[0]/256,'y':v[1]/256,'label':l,'z_index':Z.get(l,0)} for l,v in J.items()] for J in seq],open(f'{out}/{name}.json','w'))
D=json.load(open(side))
for view,kp,s in (('s',skp,.45),('n',nkp,-.45)):
    K=L(kp);Z={l:v[2] for l,v in K.items()};K={l:v[:2] for l,v in K.items()};kh=mid(K,'LEFT HIP','RIGHT HIP')
    side_x=1 if K['LEFT SHOULDER'][0]>K['RIGHT SHOULDER'][0] else -1      # screen side of the sword (LEFT) arm
    T=lambda d,lat=0:(side_x*lat*d[0],d[1]+s*d[0])   # lateral drift only for the arms
    S0={sw(k['label']):(k['x']*256,k['y']*256) for k in D['h1'][0]}       # side RIGHT (sword) -> LEFT label here
    for n,seq in D.items():
        res=[]
        for fr in seq:
            F={sw(k['label']):(k['x']*256,k['y']*256) for k in fr};J={}
            hc=add(kh,T(sub(mid(F,'LEFT HIP','RIGHT HIP'),mid(S0,'LEFT HIP','RIGHT HIP'))))
            nk=add(add(hc,sub(K['NECK'],kh)),T(sub(sub(F['NECK'],mid(F,'LEFT HIP','RIGHT HIP')),sub(S0['NECK'],mid(S0,'LEFT HIP','RIGHT HIP')))));J['NECK']=nk
            for l in ['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','LEFT SHOULDER','RIGHT SHOULDER']:J[l]=add(nk,sub(K[l],K['NECK']))
            for l in ['LEFT HIP','RIGHT HIP']:J[l]=add(hc,sub(K[l],kh))
            for p,c in [('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),
                        ('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG')]:
                J[c]=add(add(J[p],sub(K[c],K[p])),T(sub(sub(F[c],F[p]),sub(S0[c],S0[p])),.15 if ('ARM' in c or 'ELBOW' in c) else 0))
            res.append(J)
        dump(res,Z,f'C_{view}_{n}')
    # D: front slash keys (offsets from the rest pose, screen px; x positive = sword side)
    def pose(hand,elbow,lean=0,step=0,off=(0,0)):
        J=dict(K);sx=side_x
        for l in J:
            if l in('LEFT LEG','LEFT KNEE','RIGHT LEG','RIGHT KNEE'):continue
            J[l]=(J[l][0],J[l][1]+lean)
        J['LEFT ELBOW']=add(J['LEFT SHOULDER'],(sx*elbow[0],elbow[1]));J['LEFT ARM']=add(J['LEFT SHOULDER'],(sx*hand[0],hand[1]))
        J['RIGHT ELBOW']=add(J['RIGHT SHOULDER'],(-sx*6+off[0],12+off[1]));J['RIGHT ARM']=add(J['RIGHT SHOULDER'],(-sx*2+off[0],20+off[1]))
        fw=1 if s>0 else -1
        J['LEFT KNEE']=(K['LEFT KNEE'][0],K['LEFT KNEE'][1]+fw*step*.6);J['LEFT LEG']=(K['LEFT LEG'][0],K['LEFT LEG'][1]+fw*step)   # sword-side foot steps forward
        return J
    keys=[dict(K),
          pose(hand=(22,-26),elbow=(16,-8),lean=-1),                 # wind-up: sword hand high and out on the sword side
          pose(hand=(4,16),elbow=(12,8),lean=2,step=5),              # cut: hand sweeps in front of the chest
          pose(hand=(-20,30),elbow=(-4,16),lean=3,step=6),           # follow-through: low on the far side
          pose(hand=(-18,28),elbow=(-3,15),lean=3,step=6),
          pose(hand=(6,22),elbow=(8,10),lean=1,step=3)]              # recover
    seg=[3,2,2,2,3];seq=[keys[0]]
    e=lambda t:t*t*(3-2*t)
    for i,c in enumerate(seg):
        for j in range(c):
            t=e((j+1)/c);seq.append({l:(keys[i][l][0]+(keys[i+1][l][0]-keys[i][l][0])*t,keys[i][l][1]+(keys[i+1][l][1]-keys[i][l][1])*t) for l in K})
    dump(seq,Z,f'D_{view}')
print('ok')
