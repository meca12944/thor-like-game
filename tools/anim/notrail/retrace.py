# Redraw a saved clip with PixelLab from the clean character art: estimate-skeleton on every saved frame (0.1 each), keep the left/right
# labels consistent along the clip, then animate-with-skeleton-v3 from the rotation image -> same motion, clean face / opaque arms / native dots.
# usage: retrace.py <frames dir> <n> <rot.png> <rot_kp.json> <direction> <out dir> <seed>
import os,sys,json,math,subprocess
fd,n,rot,rkp,dr,out,seed=sys.argv[1],int(sys.argv[2]),*sys.argv[3:8]
H=os.path.dirname(os.path.abspath(__file__));Q=H+'/../q34'
os.makedirs(out+'/kp',exist_ok=True)
for i in range(n):
    p=f'{out}/kp/{i:02d}.json'
    if not os.path.exists(p): subprocess.run(['python3',Q+'/est.py',f'{fd}/{i:02d}.png',p],check=True,capture_output=True)
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT')
def load(p): return {k['label']:(k['x'],k['y'],int(k.get('z_index',0))) for k in json.load(open(p))['keypoints']}
LIM=[l for l in load(rkp) if any(s in l for s in ('LEG','KNEE','ARM','ELBOW'))]
cost=lambda A,B,s:sum(math.dist(A[l][:2],B[sw(l) if s else l][:2]) for l in LIM)
K=[load(rkp)]+[load(f'{out}/kp/{i:02d}.json') for i in range(n)]
for i in range(1,len(K)):
    if cost(K[i-1],K[i],True)<cost(K[i-1],K[i],False): K[i]={l:K[i][sw(l)] for l in K[i]}
json.dump([[{'x':v[0],'y':v[1],'label':l,'z_index':v[2]} for l,v in k.items()] for k in K[1:]],open(out+'/seq.json','w'))
env=dict(os.environ,ACTION=os.environ.get('ACTION','sword attack, single longsword, one sword only, no effects, no trails'))
r=subprocess.run(['python3',Q+'/gen_skel.py',rot,rkp,out+'/seq.json',dr,out+'/gen',seed],env=env,capture_output=True,text=True);print(r.stdout.strip().splitlines()[-1:],r.stderr[-300:])
