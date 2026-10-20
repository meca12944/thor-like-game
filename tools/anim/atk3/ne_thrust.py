# ↗ thrusts built in the 3/4-back view itself (projecting the side motion hid the blade): blend the NE rotation skeleton (ready) and
# the NE lunge pose skeleton. chamber = ready with the sword arm pulled back toward the hip. amounts: h1 0.7, h2 0.85, h3 1.0 (+coil).
# usage: ne_thrust.py <ne_kp.json> <pose_kp.json (label-matched)> <outdir>
import json,sys,math
A0={k['label']:k for k in json.load(open(sys.argv[1]))['keypoints']};L0={k['label']:k for k in json.load(open(sys.argv[2]))['keypoints']}
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT')
LIM=[l for l in A0 if any(s in l for s in ('ARM','ELBOW'))]
# the sword arm is the one reaching furthest toward the upper right in the lunge
arm='RIGHT' if (L0['RIGHT ARM']['x']-L0['RIGHT ARM']['y'])>(L0['LEFT ARM']['x']-L0['LEFT ARM']['y']) else 'LEFT'
A={l:(v['x'],v['y'],v.get('z_index',0)) for l,v in A0.items()};L={l:(v['x'],v['y'],v.get('z_index',0)) for l,v in L0.items()}
def mix(P,Q,t): return {l:(P[l][0]+(Q[l][0]-P[l][0])*t,P[l][1]+(Q[l][1]-P[l][1])*t,Q[l][2] if t>.5 else P[l][2]) for l in P}
def chamber(P,k=1.0,down=0.0):
    C=dict(P);sh=P[arm+' SHOULDER']
    for j,f in ((arm+' ELBOW',.6),(arm+' ARM',1.0)): C[j]=(P[j][0]-10/256*f*k,P[j][1]+6/256*f*k,P[j][2])
    if down:
        for l in C:C[l]=(C[l][0],C[l][1]+down/256*(1 if 'LEG' not in l else 0),C[l][2])
    return C
ease=lambda t:t*t*(3-2*t)
def seq(keys,seg):
    out=[keys[0]]
    for i,c in enumerate(seg):
        for j in range(c): out.append(mix(keys[i],keys[i+1],ease((j+1)/c)))
    return out
H1=seq([A,chamber(A),mix(A,L,.7),mix(A,L,.72),chamber(mix(A,L,.4),.5)],[4,2,3,3])
H2=seq([H1[-1],chamber(mix(A,L,.3),1.2,4),mix(A,L,.85),mix(A,L,.87),chamber(mix(A,L,.5),1.0)],[4,2,3,4])
H3=seq([H2[-1],chamber(mix(A,L,.35),1.6,8),L,L,L],[5,2,4,3])
out=lambda S:[[{'x':v[0],'y':v[1],'label':l,'z_index':int(round(v[2]))} for l,v in k.items()] for k in S]
for n,S in (('h1',H1),('h2',H2),('h3',H3)): json.dump(out(S),open(f'{sys.argv[3]}/ne2_{n}.json','w'))
print('sword arm',arm,len(H1),len(H2),len(H3))
