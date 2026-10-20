# Thrust clip anchored on its strike pose: the pose image (blade level, drawn by edit-images-v2) is the FIRST frame, the skeletons run
# backwards from the strike to the start, PixelLab draws them, and the frames are reversed for playback -> the blade stays level.
# usage: anchor_rev.py <pose.png> <seq.json (forward skeletons)> <direction> <out dir> <seed>
import os,sys,json,math,subprocess
from PIL import Image
pose,seqf,dr,out,seed=sys.argv[1:6];H=os.path.dirname(os.path.abspath(__file__));Q=H+'/../q34';os.makedirs(out,exist_ok=True)
im=Image.open(pose).convert('RGBA');b=im.getbbox()[3];a=Image.new('RGBA',(256,256));a.paste(im,(0,189-b));a.save(out+'/pose189.png')  # soles on 189
if not os.path.exists(out+'/pose_kp.json'): subprocess.run(['python3',Q+'/est.py',out+'/pose189.png',out+'/pose_kp.json'],check=True,capture_output=True)
S=json.load(open(seqf));R=S[::-1]
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT')
P={k['label']:k for k in json.load(open(out+'/pose_kp.json'))['keypoints']};F={k['label']:k for k in R[0]}
LIM=[l for l in F if any(s in l for s in ('LEG','KNEE','ARM','ELBOW'))]
c=lambda s:sum(math.dist((F[l]['x'],F[l]['y']),(P[sw(l) if s else l]['x'],P[sw(l) if s else l]['y'])) for l in LIM)
if c(True)<c(False): json.dump({'keypoints':[dict(v,label=sw(l)) for l,v in P.items()]},open(out+'/pose_kp.json','w'));print('pose labels swapped')
json.dump(R,open(out+'/rev.json','w'))
env=dict(os.environ,DESC=os.environ.get('DESC','young swordsman with long straight black hair, dark navy coat with gold trim, cape with red lining, gold pauldron on one shoulder, holding one longsword'))
r=subprocess.run(['python3',Q+'/gen_skel.py',out+'/pose189.png',out+'/pose_kp.json',out+'/rev.json',dr,out+'/rev',seed],env=env,capture_output=True,text=True);print(r.stdout.strip().splitlines()[-1:],r.stderr[-300:])
n=len(R);os.makedirs(out+'/fwd',exist_ok=True)
for i in range(n): Image.open(f'{out}/rev/{n-1-i:03d}.png').save(f'{out}/fwd/{i:03d}.png')
