import json,math
def load(p): return {k['label']:dict(x=k['x']*256,y=k['y']*256,z=int(k.get('z_index',0))) for k in json.load(open(p))['keypoints']}
def out(K): return [dict(x=v['x']/256,y=v['y']/256,label=l,z_index=v['z']) for l,v in K.items()]
FACE=['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR']
UPPER=FACE+['NECK','LEFT SHOULDER','RIGHT SHOULDER','LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM']
jobs=[]
# up attacks again: same mirrored down motion, but head/face joints copied from the back-view frame (moved with the neck) so it stays facing away
for h in ['hit1','hit2','hit3']:
    K0=load(f'all/{h}_up/k0_kpfix.json');S=json.load(open(f'fix/{h}_up_seq.json'))
    for fr in S:
        d={k['label']:k for k in fr};nx,ny=d['NECK']['x']*256-K0['NECK']['x'],d['NECK']['y']*256-K0['NECK']['y']
        for l in FACE: d[l]['x']=(K0[l]['x']+nx)/256;d[l]['y']=(K0[l]['y']+ny)/256;d[l]['z_index']=K0[l]['z']
    json.dump(S,open(f'fix/{h}_up_seq2.json','w'))
    jobs.append(dict(first=f'all/{h}_up/k0.png',fkp=f'all/{h}_up/k0_kpfix.json',kp=f'fix/{h}_up_seq2.json',dir='north',out=f'fix/{h}_up2',act='sword slash seen from behind, back view, facing away from the camera the whole time'))
# hurt: designed recoil from the standing frame. impact = upper body thrown back, arms flung, knees bent, back foot slid; then recover
def rot(p,c,a): s,co=math.sin(a),math.cos(a);x,y=p['x']-c[0],p['y']-c[1];return c[0]+x*co-y*s,c[1]+x*s+y*co
def recoil(K,d,k):
    E={l:dict(v) for l,v in K.items()}
    hip=((K['LEFT HIP']['x']+K['RIGHT HIP']['x'])/2,(K['LEFT HIP']['y']+K['RIGHT HIP']['y'])/2)
    cx=(K['LEFT SHOULDER']['x']+K['RIGHT SHOULDER']['x'])/2
    for l in UPPER:
        if d=='right':  # facing +x, thrown back toward -x
            E[l]['x'],E[l]['y']=rot(K[l],hip,-0.40*k)
        else:           # front/back view: head snaps back (drops 5px toward the hips) and the body twists a little
            E[l]['y']=K[l]['y']+5*k*(1 if l in FACE+['NECK'] else 0.6);E[l]['x']=K[l]['x']+3*k
    for side in ['LEFT','RIGHT']:  # arms flung out from the body
        s=E[f'{side} SHOULDER'];w=E[f'{side} ARM'];el=E[f'{side} ELBOW']
        if d=='right':
            w['x']+=14*k;w['y']-=10*k;el['x']+=6*k;el['y']-=4*k
        else:
            sgn=1 if K[f'{side} ARM']['x']>cx else -1
            w['x']+=sgn*16*k;w['y']-=14*k;el['x']+=sgn*8*k;el['y']-=5*k
    for l in ['LEFT HIP','RIGHT HIP','LEFT KNEE','RIGHT KNEE']: E[l]['y']+=5*k  # knees give
    for l in ['LEFT KNEE','RIGHT KNEE']: E[l]['x']+=(4 if d=='right' else 0)*k
    if d=='right': E['LEFT LEG']['x']-=10*k;E['LEFT KNEE']['x']-=5*k  # back foot slides
    return E
CURVE=[0,1.0,0.95,0.7,0.45,0.25,0.1,0]
for d,src in [('right','all/hurt_right/k0'),('down','all/hurt_down/k0'),('up','all/hurt_up/k0')]:
    K=load(src+'_kpfix.json');json.dump([out(recoil(K,d,k)) for k in CURVE],open(f'fix/hurt_seq_{d}.json','w'))
    jobs.append(dict(first=src+'.png',fkp=src+'_kpfix.json',kp=f'fix/hurt_seq_{d}.json',dir={'right':'east','down':'south','up':'north'}[d],out=f'fix/hurt3_{d}',act='getting hit hard, thrown back by the blow, then recovering'+(', back view, facing away from the camera' if d=='up' else '')))
json.dump(jobs,open('fix/jobs2.json','w'));print(len(jobs))
