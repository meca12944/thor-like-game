# atk2 = atk1 with the arm poses swapped: estimate the skeleton on every atk1 frame, then put the right arm's shoulder->elbow->wrist
# vectors on the left shoulder and vice versa. Body, legs and timing stay identical to atk1; only the thrusting hand changes.
# usage: swap_seq.py <atk1 frame dir> <out_kp.json> <first_kp.json out>
import sys,os,glob,json,subprocess
fs=sorted(glob.glob(sys.argv[1]+'/*.png')); D=os.path.dirname(os.path.abspath(__file__)); seq=[]
for i,f in enumerate(fs):
    kpf=f'{sys.argv[2]}.f{i}.json'
    if not os.path.exists(kpf): subprocess.run([sys.executable,D+'/estimate.py',f,kpf],check=True,capture_output=True)
    K={p['label']:p for p in json.load(open(kpf))['keypoints']}
    if i==0: json.dump({'keypoints':list(K.values())},open(sys.argv[3],'w'))
    v=lambda a,b:(K[b]['x']-K[a]['x'],K[b]['y']-K[a]['y'])
    arm={s:(v(s+' SHOULDER',s+' ELBOW'),v(s+' ELBOW',s+' ARM')) for s in ('LEFT','RIGHT')}
    out={k:dict(p) for k,p in K.items()}
    for s,o in (('LEFT','RIGHT'),('RIGHT','LEFT')):
        (se,ew)=arm[o]; out[s+' ELBOW']['x']=K[s+' SHOULDER']['x']+se[0]; out[s+' ELBOW']['y']=K[s+' SHOULDER']['y']+se[1]
        out[s+' ARM']['x']=out[s+' ELBOW']['x']+ew[0]; out[s+' ARM']['y']=out[s+' ELBOW']['y']+ew[1]
    seq.append([{'x':min(1,max(0,p['x'])),'y':min(1,max(0,p['y'])),'label':p['label'],'z_index':int(p.get('z_index',0))} for p in out.values()])
json.dump(seq,open(sys.argv[2],'w')); print(len(seq),'frames')
