# Linette diagonal clips from the HERO's diagonal motions (owner 10-20): skeleton of every hero ↘/↗ frame (estimate-skeleton),
# Linette keypoints(t) = Linette diagonal still + s * (hero(t) - hero idle frame 0), s = 117/124. For run the arms come from Linette's own
# side run (hands at the waist, arms back) so she keeps her running style. usage: diag_from_hero.py <motion> <down|up>
import json,sys,os,glob,subprocess
m,d=sys.argv[1],sys.argv[2]   # d: down | up | right (side)
H='/tmp/claude-0/-home-user-thor-like-game/a29f4f91-dc28-5c8c-bba3-8521caf6b08f/scratchpad/herodiag'; C=os.path.dirname(os.path.abspath(__file__))
dd={'down':'south-east','up':'north-east','right':'east'}[d]; S=117/124
def est(png):
    out=png.replace('.png','.kp.json')
    if not os.path.exists(out): subprocess.run([sys.executable,C+'/estimate.py',png,out],check=True,capture_output=True)
    return {p['label']:p for p in json.load(open(out))['keypoints']}
base=est(f'{H}/idle_{d}/000.png'); L0={p['label']:p for p in json.load(open(f'{C}/'+('start_idle_east_kp.json' if d=='right' else f'start_still_{dd}_kp.json')))['keypoints']}
frames=sorted(glob.glob(f'{H}/{m}_{d}/[0-9]*.png')); seq=[]
side=json.load(open(f'{C}/kp_run_east_back.json')) if m=='run' else None; side0={p['label']:p for p in side[0]} if side else None
ARM=('LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM')
for i,f in enumerate(frames):
    K=est(f); fr=[]
    for k,l in L0.items():
        if k not in K: continue
        x=l['x']+S*(K[k]['x']-base[k]['x']); y=l['y']+S*(K[k]['y']-base[k]['y'])
        if side and k in ARM:   # Linette's run arms: side-run arm offsets from the shoulder, squeezed for the 3/4 view
            sh=k.split()[0]+' SHOULDER'; F={p['label']:p for p in side[i%len(side)]}
            x=(l['x']+S*(K[sh]['x']-base[sh]['x']))+0.8*(F[k]['x']-F[sh]['x'])*(1 if d=='down' else 1); y=(l['y']+S*(K[sh]['y']-base[sh]['y']))+(F[k]['y']-F[sh]['y'])
        fr.append({'x':min(1,max(0,x)),'y':min(1,max(0,y)),'label':k,'z_index':int(l.get('z_index',0))})
    seq.append(fr)
json.dump(seq,open(f'{C}/kp_{m}_{dd}_fromhero.json','w')); print(m,d,len(seq),'frames')
