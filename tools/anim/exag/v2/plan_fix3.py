# up hit1/hit3: keep the torso facing away (shoulder and hip pairs keep the back-view width and angle, only translated), limbs follow
import json
TOR=[('LEFT SHOULDER','RIGHT SHOULDER','NECK'),('LEFT HIP','RIGHT HIP',None)]
jobs=[]
for h in ['hit1','hit3']:
    K0={k['label']:k for k in json.load(open(f'all/{h}_up/k0_kpfix.json'))['keypoints']}
    S=json.load(open(f'fix/{h}_up_seq2.json'))
    for fr in S:
        d={k['label']:k for k in fr}
        for a,b,_ in TOR:
            cx=(d[a]['x']+d[b]['x'])/2;cy=(d[a]['y']+d[b]['y'])/2;kx=(K0[a]['x']+K0[b]['x'])/2;ky=(K0[a]['y']+K0[b]['y'])/2
            for l in (a,b):
                ox,oy=d[l]['x'],d[l]['y'];d[l]['x']=K0[l]['x']-kx+cx;d[l]['y']=K0[l]['y']-ky+cy;d[l]['z_index']=int(K0[l].get('z_index',0))
                # drag the limb chain hanging off this joint by the same shift
                ch={'LEFT SHOULDER':['LEFT ELBOW','LEFT ARM'],'RIGHT SHOULDER':['RIGHT ELBOW','RIGHT ARM'],'LEFT HIP':['LEFT KNEE'],'RIGHT HIP':['RIGHT KNEE']}[l]
                for c in ch: d[c]['x']+=d[l]['x']-ox;d[c]['y']+=d[l]['y']-oy
    json.dump(S,open(f'fix/{h}_up_seq3.json','w'))
    jobs.append(dict(first=f'all/{h}_up/k0.png',fkp=f'all/{h}_up/k0_kpfix.json',kp=f'fix/{h}_up_seq3.json',dir='north',out=f'fix/{h}_up3',act='sword slash seen from behind, back view, shoulders square to the camera, never turning around'))
json.dump(jobs,open('fix/jobs3.json','w'))
