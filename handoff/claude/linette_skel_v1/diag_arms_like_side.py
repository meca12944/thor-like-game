# Owner 10-20 "밑으로 대각선 양 방향 팔위치 좌우랑 틀리다": down-diagonal clips get the SIDE clip's arms.
# legs/torso/head = the current diagonal skeleton (kp_<m>_south-east_fromhero.json); each arm = diagonal shoulder + side (elbow/hand - shoulder) offset
# of the same frame phase, arms drawn behind the body like the side view. usage: diag_arms_like_side.py <motion> <side_kp.json> <out.json> [sx=1.0]
import json,sys,os
C=os.path.dirname(os.path.abspath(__file__));m,side,out=sys.argv[1],sys.argv[2],sys.argv[3];SX=float(sys.argv[4]) if len(sys.argv)>4 else 1.0
D=json.load(open(f'{C}/kp_{m}_south-east_fromhero.json'));Sd=json.load(open(side if os.path.isabs(side) else f'{C}/{side}'))
if isinstance(Sd,dict):Sd=[Sd['keypoints']]
if isinstance(Sd[0],dict):Sd=[Sd]
seq=[]
for i,f in enumerate(D):
    K={p['label']:dict(p) for p in f};F={p['label']:p for p in Sd[i*len(Sd)//len(D)]}
    for s in ('LEFT','RIGHT'):
        sh=s+' SHOULDER'
        for j in (s+' ELBOW',s+' ARM'):
            K[j]['x']=min(1,max(0,K[sh]['x']+SX*(F[j]['x']-F[sh]['x'])));K[j]['y']=min(1,max(0,K[sh]['y']+(F[j]['y']-F[sh]['y'])))
    seq.append([{'x':p['x'],'y':p['y'],'label':k,'z_index':int(p.get('z_index',0))} for k,p in K.items()])
json.dump(seq,open(out if os.path.isabs(out) else f'{C}/{out}','w'));print(m,len(seq),'frames')
