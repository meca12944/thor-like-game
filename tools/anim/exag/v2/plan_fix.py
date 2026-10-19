import json,math,os
def load(p): return {k['label']:dict(x=k['x'],y=k['y'],z=int(k.get('z_index',0))) for k in json.load(open(p))['keypoints']}
def out(K): return [dict(x=v['x'],y=v['y'],label=l,z_index=v['z']) for l,v in K.items()]
DIRN={'down':'south','up':'north','right':'east'};jobs=[]
# 1) idle breathing: 12-frame loop, legs fixed, upper body rises 3px and sways 2px, shoulders lift, arms hang and swing a little
UP=['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','NECK','LEFT SHOULDER','RIGHT SHOULDER','LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM']
for d in ['right','down','up']:
    K=load(f'fix/idle_low_{d}_kp.json');seq=[]
    for f in range(12):
        ph=f/12*2*math.pi;br=(1-math.cos(ph))/2  # 0..1 inhale
        sway=math.sin(ph)*2/256
        e={}
        for l,v in K.items():
            x,y=v['x'],v['y']
            if l in UP:
                y-=br*3/256;x+=sway
                if 'SHOULDER' in l: y-=br*1.5/256
                if 'ELBOW' in l: x+=sway*0.5
                if 'ARM' in l: x+=sway*1.2;y+=br*1/256
            elif 'HIP' in l: y-=br*1/256;x+=sway*0.4
            e[l]=dict(x=x,y=y,z=v['z'])
        seq.append(out(e))
    json.dump(seq,open(f'fix/idle_seq_{d}.json','w'))
    jobs.append(dict(first=f'fix/idle_low_{d}.png',fkp=f'fix/idle_low_{d}_kp.json',kp=f'fix/idle_seq_{d}.json',dir=DIRN[d],out=f'fix/idle_{d}',act='idle breathing, cape and hair swaying gently'))
# 2) up attacks = the down attack's exaggerated skeleton seen from behind (mirror x, flip depth), drawn from the in-game back-view first frame
for h in ['hit1','hit2','hit3']:
    E=json.load(open(f'all/{h}_down/exag.json'))
    mir=[[dict(x=1-k['x'],y=k['y'],label=k['label'],z_index=-int(k['z_index'])) for k in fr] for fr in E]
    seq=[]
    for i in range(len(mir)):
        seq.append(mir[i])
        if i<len(mir)-1: seq.append([dict(x=(a['x']+b['x'])/2,y=(a['y']+b['y'])/2,label=a['label'],z_index=a['z_index']) for a,b in zip(mir[i],mir[i+1])])
    json.dump(seq[:15],open(f'fix/{h}_up_seq.json','w'))
    jobs.append(dict(first=f'all/{h}_up/k0.png',fkp=f'all/{h}_up/k0_kpfix.json',kp=f'fix/{h}_up_seq.json',dir='north',out=f'fix/{h}_up',act='sword slash seen from behind, character keeps facing away from the camera'))
json.dump(jobs,open('fix/jobs.json','w'));print(len(jobs))
