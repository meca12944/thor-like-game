# owner 10-23 "대시 모션 방향별로 (정면) 만들어": Linette's straight front dash = the hero's straight front dash (index.html H8 dash_down, hero8_front sheet, 9 frames)
# by skeleton: Linette keypoints = her front idle + s * (hero(t) - hero frame 0), s = Linette front height / hero front height.
import json,sys,os,glob,subprocess
from PIL import Image
C=os.path.dirname(os.path.abspath(__file__));H='/tmp/claude-0/-home-user-thor-like-game/a29f4f91-dc28-5c8c-bba3-8521caf6b08f/scratchpad/herodiag'
def est(png,out=None):
    out=out or png.replace('.png','.kp.json')
    if not os.path.exists(out):subprocess.run([sys.executable,C+'/estimate.py',png,out],check=True,capture_output=True)
    return {p['label']:p for p in json.load(open(out))['keypoints']}
hh=lambda f:(lambda b:b[3]-b[1])(Image.open(f).getbbox())
fs=sorted(glob.glob(H+'/dash_front/[0-9]*.png'));S=hh(C+'/start_front_idle.png')/hh(fs[0])
L0=est(C+'/start_front_idle.png',C+'/start_front_idle_kp.json');base=est(fs[0]);seq=[]
for f in fs:
    K=est(f);seq.append([{'x':min(1,max(0,l['x']+S*(K[k]['x']-base[k]['x']))),'y':min(1,max(0,l['y']+S*(K[k]['y']-base[k]['y']))),'label':k,'z_index':int(l.get('z_index',0))} for k,l in L0.items() if k in K])
json.dump(seq,open(C+'/kp_dash_south_fromhero.json','w'));print(len(seq),'frames, s',round(S,3))
