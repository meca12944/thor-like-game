# atk2 as a real dual-needle chain from the end of atk1: right needle (extended) pulls back while the LEFT needle thrusts, hold, then settle
# back to the ready stance (keypoints of atk1 frame 0). usage: atk2_chain.py <dir>  (needs start_lunge_<dir>_kp.json, kp_swap_<dir>.json,
# kp_atk2swap_<dir>.json.f0.json) -> kp_atk2chain_<dir>.json
import json,sys
d=sys.argv[1]; L=json.load(open(f'kp_swap_{d}.json')); lunge,mid,sw=L[0],L[1],L[2]
stand={p['label']:p for p in json.load(open(f'kp_atk2swap_{d}.json.f0.json'))['keypoints']}
def lerp(A,t): return [{**p,'x':p['x']+(stand[p['label']]['x']-p['x'])*t,'y':p['y']+(stand[p['label']]['y']-p['y'])*t} for p in A]
seq=[lunge,mid,sw,sw,lerp(sw,0.35),lerp(sw,0.7),lerp(sw,1.0)]
json.dump([[{'x':min(1,max(0,p['x'])),'y':min(1,max(0,p['y'])),'label':p['label'],'z_index':int(p.get('z_index',0))} for p in f] for f in seq],open(f'kp_atk2chain_{d}.json','w')); print(d,len(seq))
