# diagonal (3/4) hero motions: SE (front 3/4, used for down) and NE (back 3/4, used for up); left variants = mirror
import json,math,sys,subprocess
sys.argv=['x','a','b','se','c','0'];src=open('q34/atk34.py').read().split('seq=[]')[0]  # reuse the side->3/4 transform
NOFX=', no effects, no trails, no dust, no sparks'
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT')
def load(p): return {k['label']:k for k in json.load(open(p))['keypoints']}
def cost(A,B,s): return sum(math.hypot(A[l]['x']-B[sw(l) if s else l]['x'],A[l]['y']-B[sw(l) if s else l]['y']) for l in A if any(t in l for t in ('LEG','KNEE','ARM','ELBOW')))
def side_seq(name,n):
    K=[load(f'dg/{name}/k{i}_kp.json') for i in range(n)]
    for i in range(1,n):
        if cost(K[i-1],K[i],True)<cost(K[i-1],K[i],False): K[i]={l:K[i][sw(l)] for l in K[i]}
    return [[dict(x=v['x'],y=v['y'],label=l,z_index=v.get('z_index',0)) for l,v in k.items()] for k in K]
def to34(seq,view,mids):
    g=dict(SEQ=seq,json=json,sys=sys);exec(src.replace("side,kp3,view,out,swap=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]=='1'",
        f"side,kp3,view,out,swap='',{'q34/'+view+'_kp.json'!r},{view!r},'',False").replace("S=[{sw(k['label']):(k['x']*256,k['y']*256) for k in fr} for fr in json.load(open(side))]","S=[{sw(k['label']):(k['x']*256,k['y']*256) for k in fr} for fr in SEQ]"),g)
    S,frame=g['S'],g['frame'];out=[]
    for i,F in enumerate(S):
        out.append(frame(F))
        if mids and i<len(S)-1: out.append(frame({l:((F[l][0]+S[i+1][l][0])/2,(F[l][1]+S[i+1][l][1])/2) for l in F}))
    Z=g['Z'];return [[{'x':v[0]/256,'y':v[1]/256,'label':l,'z_index':Z.get(l,0)} for l,v in J.items()] for J in out[:15]]
man=json.load(open('dg/manifest.json'));jobs=[]
DN={'se':'south-east','ne':'north-east'}
for v in ['se','ne']:
    first=f'q34/rot_{DN[v]}.png';fkp=f'q34/{v}_kp.json'
    # idle breathing (12)
    K=load(fkp);UP=['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','NECK','LEFT SHOULDER','RIGHT SHOULDER','LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM'];seq=[]
    for f in range(12):
        ph=f/12*2*math.pi;br=(1-math.cos(ph))/2;sx=math.sin(ph)*1.5/256;fr=[]
        for l,k in K.items():
            x,y=k['x'],k['y']
            if l in UP: y-=br*2.5/256+(br*1.2/256 if 'SHOULDER' in l else 0);x+=sx
            elif 'HIP' in l: y-=br*0.8/256
            fr.append(dict(x=x,y=y,label=l,z_index=int(k.get('z_index',0))))
        seq.append(fr)
    json.dump(seq,open(f'dg/idle_{v}.json','w'));jobs.append(dict(first=first,fkp=fkp,kp=f'dg/idle_{v}.json',dir=DN[v],out=f'dg/out_idle_{v}',act='idle breathing, standing still'+NOFX))
    # walk / run from CMU mocap
    subprocess.run(['python3','retarget34.py','07_01.bvh',f'../{fkp}',f'../dg/walk_{v}.json','12',v,'LEFT','6','1.15','1.2','0','1.0','35'],cwd='mocap',check=True)
    subprocess.run(['python3','retarget34.py','09_01.bvh',f'../{fkp}',f'../dg/run_{v}.json','12',v,'LEFT','20','1.3','1.3','0','1.2','35'],cwd='mocap',check=True)
    jobs.append(dict(first=first,fkp=fkp,kp=f'dg/walk_{v}.json',dir=DN[v],out=f'dg/out_walk_{v}',act='walking'+NOFX))
    jobs.append(dict(first=first,fkp=fkp,kp=f'dg/run_{v}.json',dir=DN[v],out=f'dg/out_run_{v}',act='running fast, sprinting'+NOFX))
    # short motions from the in-game side clip, converted to 3/4
    for a,mids,act in [('dash_right',True,'quick dash forward'),('death_right',False,'falling down, dying'),('jump_right',True,'jumping'),('cast_s1_right',True,'casting a spell, raising the hand')]:
        json.dump(to34(side_seq(a,len(man[a])),v,mids),open(f'dg/{a.split("_")[0]}_{v}.json','w'))
        jobs.append(dict(first=first,fkp=fkp,kp=f'dg/{a.split("_")[0]}_{v}.json',dir=DN[v],out=f'dg/out_{a.split("_")[0]}_{v}',act=act+NOFX))
    hs=json.load(open('fix/hurt_seq_right.json'))  # hurt v2 designed recoil (side)
    json.dump(to34(hs[1:],v,False),open(f'dg/hurt_{v}.json','w'))
    jobs.append(dict(first=first,fkp=fkp,kp=f'dg/hurt_{v}.json',dir=DN[v],out=f'dg/out_hurt_{v}',act='getting hit hard, thrown back, then recovering'+NOFX))
json.dump(jobs,open('dg/jobs.json','w'));print(len(jobs),[ (j['out'],len(json.load(open(j['kp'])))) for j in jobs])
