# owner 10-22 "주인공 대시 모션 그대로 가지고와": Linette's side dash = the hero's side dash (hero8 dash_right, 4 frames: stand, low lunge, hold, recover).
# Skeleton of each hero frame (estimate-skeleton) -> Linette keypoints = Linette's face-fixed side idle + 117/124 * (hero(t) - hero dash frame 0).
import json,sys,os,glob,subprocess
C=os.path.dirname(os.path.abspath(__file__));H='/tmp/claude-0/-home-user-thor-like-game/a29f4f91-dc28-5c8c-bba3-8521caf6b08f/scratchpad/herodiag';S=117/124
def est(png,out=None):
    out=out or png.replace('.png','.kp.json')
    if not os.path.exists(out):subprocess.run([sys.executable,C+'/estimate.py',png,out],check=True,capture_output=True)
    return {p['label']:p for p in json.load(open(out))['keypoints']}
L0=est(C+'/idle_east_facefix/000.png',C+'/start_facefix_east_kp.json');fs=sorted(glob.glob(H+'/dash_right/[0-9]*.png'));base=est(fs[0]);seq=[]
for f in fs:
    K=est(f);seq.append([{'x':min(1,max(0,l['x']+S*(K[k]['x']-base[k]['x']))),'y':min(1,max(0,l['y']+S*(K[k]['y']-base[k]['y']))),'label':k,'z_index':int(l.get('z_index',0))} for k,l in L0.items() if k in K])
json.dump(seq,open(C+'/kp_dash_east_fromhero.json','w'));print(len(seq),'frames')
