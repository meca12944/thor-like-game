# up attacks v4: torso and legs stay in the back-view stance (small forward step + lean), only the arms take the swing from the mirrored down attack
import json,math
jobs=[]
for h in ['hit1','hit2','hit3']:
    K0={k['label']:dict(k) for k in json.load(open(f'all/{h}_up/k0_kpfix.json'))['keypoints']}
    S=json.load(open(f'fix/{h}_up_seq2.json'))
    def sc(d):return ((d['LEFT SHOULDER']['x']+d['RIGHT SHOULDER']['x'])/2,(d['LEFT SHOULDER']['y']+d['RIGHT SHOULDER']['y'])/2)
    s0=sc({k['label']:k for k in S[0]});w0={l:(S[0][i]['x'],S[0][i]['y']) for i,l in enumerate([k['label'] for k in S[0]])}
    amp=[];out=[]
    for fr in S:
        d={k['label']:k for k in fr};c=sc(d)
        a=sum(math.hypot(d[l]['x']-c[0]-(w0[l][0]-s0[0]),d[l]['y']-c[1]-(w0[l][1]-s0[1])) for l in ['LEFT ARM','RIGHT ARM'])
        amp.append(a)
    mx=max(amp) or 1
    for fr,a in zip(S,amp):
        d={k['label']:k for k in fr};c=sc(d);k=a/mx;px=1/256
        e={l:dict(x=v['x'],y=v['y'],label=l,z_index=int(v.get('z_index',0))) for l,v in K0.items()}
        kc=sc(K0)
        for l in ['LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM']:  # arm swing relative to the shoulders
            e[l]['x']=kc[0]+(d[l]['x']-c[0]);e[l]['y']=kc[1]+(d[l]['y']-c[1])
        for l in ['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','NECK','LEFT SHOULDER','RIGHT SHOULDER','LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM']:
            e[l]['y']-=4*k*px  # lean into the swing (away from camera = up the screen)
        for l in ['LEFT HIP','RIGHT HIP']: e[l]['y']-=2*k*px
        e['LEFT KNEE']['y']-=5*k*px;e['LEFT LEG']['y']-=9*k*px  # front foot steps forward
        out.append(list(e.values()))
    json.dump(out,open(f'fix/{h}_up_seq4.json','w'))
    jobs.append(dict(first=f'all/{h}_up/k0.png',fkp=f'all/{h}_up/k0_kpfix.json',kp=f'fix/{h}_up_seq4.json',dir='north',out=f'fix/{h}_up4',act='sword slash, back view, facing away from the camera, body does not turn'))
json.dump(jobs,open('fix/jobs4.json','w'))
