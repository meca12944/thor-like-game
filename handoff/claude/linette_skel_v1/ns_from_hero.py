# Owner 10-20 "리네트 아래위 북쪽 남쪽 걷기 뛰기모션 만들라고, 스켈레톤으로 모션보고 픽셀랩": true front (south) / back (north) walk + run
# from the HERO's front/back motions. Hero frames: moves_v1 walk south/north, run_v4 down/up (key0,mid0,key1,...). Skeleton per hero frame
# (estimate-skeleton), Linette(t) = Linette front/back still + s*(hero(t) - hero walk frame 0), s = 117/124. Arms are Linette's own style:
# walk = her still arms riding on the shoulders, run = both arms pulled back (hands behind the hips). usage: ns_from_hero.py <walk|run> <south|north> <hero_dir> <out>
import json,sys,os,glob
C=os.path.dirname(os.path.abspath(__file__));m,d,hd,out=sys.argv[1:5];S=117/124;LEGX=0.4
def kp(f):
    j=json.load(open(f));k=j['keypoints'] if isinstance(j,dict) else j;return {p['label']:p for p in k}
fs=sorted(glob.glob(hd+'/*.kp.json'));base=kp(os.path.join(os.path.dirname(hd),f'walk_{d}','000.kp.json'))
L0=kp(f'{C}/start_idle_{d}_kp.json');back=d=='north'
seq=[]
for f in fs:
    H=kp(f);J={}
    for k,l in L0.items():
        if k in H and k in base:J[k]=[l['x']+S*(LEGX if ('KNEE' in k or 'LEG' in k) else 1)*(H[k]['x']-base[k]['x']),l['y']+S*(H[k]['y']-base[k]['y']),int(l.get('z_index',0))]   # front/back: feet stay under the body (no crab legs)
        else:J[k]=[l['x'],l['y'],int(l.get('z_index',0))]
    for s in ('LEFT','RIGHT'):   # legs: the hero's leg shape as drawn (keeps foreshortening = foot lifts in front/back views), scaled to Linette's leg length (owner: "주인공 다리모션 참조")
        hp,kn,an=s+' HIP',s+' KNEE',s+' LEG'
        if all(k in H and k in L0 and k in base for k in (hp,kn,an)):
            r=(L0[an]['y']-L0[hp]['y'])/max(1e-6,base[an]['y']-base[hp]['y'])
            for k in (kn,an):J[k]=[J[hp][0]+r*(H[k]['x']-H[hp]['x']),J[hp][1]+r*(H[k]['y']-H[hp]['y']),J[k][2]]
    for s in ('LEFT','RIGHT'):
        sh=s+' SHOULDER';dx,dy=J[sh][0]-L0[sh]['x'],J[sh][1]-L0[sh]['y']
        out_=1 if (L0[s+' ARM']['x']>L0[sh]['x']) else -1   # which side this arm hangs on in the still
        if m=='walk':
            for j in (s+' ELBOW',s+' ARM'):J[j]=[L0[j]['x']+dx,L0[j]['y']+dy,int(L0[j].get('z_index',0))]
        else:   # arms swept back: elbow out and back, hand behind the hip
            z=3 if back else -5
            J[s+' ELBOW']=[J[sh][0]+out_*0.035,J[sh][1]+0.075,z];J[s+' ARM']=[J[sh][0]+out_*0.05,J[sh][1]+0.14,z]
    seq.append([{'x':min(1,max(0,v[0])),'y':min(1,max(0,v[1])),'label':k,'z_index':v[2]} for k,v in J.items()])
json.dump(seq,open(out,'w'));print(m,d,len(seq),'frames')
