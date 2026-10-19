# exaggerate the in-game keys' skeletons and write the PixelLab job list (no API calls here)
import json,math,os
man=json.load(open('all/manifest.json'))
F={'walk':1.35,'idle':1.8,'hurt':1.45,'hit1':1.3,'hit2':1.3,'hit3':1.3}
LOOP={'walk','idle'}
ACT={'walk':'walk','idle':'idle breathing','hurt':'getting hit, flinching back','hit1':'sword slash','hit2':'sword slash','hit3':'heavy sword slash'}
DIRN={'down':'south','up':'north','right':'east'}
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT')
BONES=[('NECK','LEFT SHOULDER'),('NECK','RIGHT SHOULDER'),('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),
       ('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG')]
FACE=['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR']
def load(p): return {k['label']:dict(x=k['x'],y=k['y'],z=int(k.get('z_index',0))) for k in json.load(open(p))['keypoints']}
def lim(K): return [l for l in K if any(s in l for s in ('LEG','KNEE','ARM','ELBOW'))]
def cost(A,B,s): return sum(math.hypot(A[l]['x']-B[sw(l) if s else l]['x'],A[l]['y']-B[sw(l) if s else l]['y']) for l in lim(A))
def out(K): return [dict(x=v['x'],y=v['y'],label=l,z_index=v['z']) for l,v in K.items()]
jobs=[]
for n,ticks in man.items():
    a,dr=n.split('_');N=len(ticks)
    K=[load(f'all/{n}/k{i}_kp.json') for i in range(N)]
    for i in range(1,N):  # keep L/R labels consistent along the sequence
        if cost(K[i-1],K[i],True)<cost(K[i-1],K[i],False): K[i]={l:K[i][sw(l)] for l in K[i]}
    for i in range(N): json.dump({'keypoints':out(K[i])},open(f'all/{n}/k{i}_kpfix.json','w'))
    ref={l:dict(x=sum(k[l]['x'] for k in K)/N,y=sum(k[l]['y'] for k in K)/N) for l in K[0]} if a in LOOP else K[0]
    f=F[a];E=[]
    for k in K:
        e={l:dict(x=ref[l]['x']+f*(v['x']-ref[l]['x']),y=ref[l]['y']+f*(v['y']-ref[l]['y']),z=v['z']) for l,v in k.items()}
        for l in FACE: e[l]=dict(x=k[l]['x']+e['NECK']['x']-k['NECK']['x'],y=k[l]['y']+e['NECK']['y']-k['NECK']['y'],z=k[l]['z'])
        for p,c in BONES:  # keep each bone as long as in the key (no short shins)
            L=math.hypot(k[c]['x']-k[p]['x'],k[c]['y']-k[p]['y']);dx,dy=e[c]['x']-e[p]['x'],e[c]['y']-e[p]['y'];d=math.hypot(dx,dy) or 1
            e[c]['x']=e[p]['x']+dx/d*L;e[c]['y']=e[p]['y']+dy/d*L
        E.append(e)
    mid=lambda A,B:{l:dict(x=(A[l]['x']+B[l]['x'])/2,y=(A[l]['y']+B[l]['y'])/2,z=A[l]['z']) for l in A}
    json.dump([out(e) for e in E],open(f'all/{n}/exag.json','w'))
    if dr=='right':
        seq=[]
        for i in range(N):
            seq.append(E[i])
            if i<N-1 or a in LOOP: seq.append(mid(E[i],E[(i+1)%N]))
        seq=seq[:15];json.dump([out(s) for s in seq],open(f'all/{n}/seq_side.json','w'))
        jobs.append(dict(n=n,first=f'all/{n}/k0.png',fkp=f'all/{n}/k0_kpfix.json',kp=f'all/{n}/seq_side.json',dir=DIRN[dr],out=f'all/{n}/gen_side',act=ACT[a]))
    else:
        for i in range(N if a in LOOP else N-1):
            j=(i+1)%N;json.dump([out(E[i]),out(mid(E[i],E[j])),out(E[j])],open(f'all/{n}/seq_{i}.json','w'))
            jobs.append(dict(n=n,first=f'all/{n}/k{i}.png',fkp=f'all/{n}/k{i}_kpfix.json',kp=f'all/{n}/seq_{i}.json',dir=DIRN[dr],out=f'all/{n}/gen_{i}',act=ACT[a]))
json.dump(jobs,open('all/jobs.json','w'));print(len(jobs),'jobs')
