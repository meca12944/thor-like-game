# add the all-thrust 3-hit (handoff/claude/hero_thrust3_v1, 6 art dirs) to the sandbox atlas as sheet 'hero_thr.png': thit1..3_<dir>,
# plus 'thr' = per-clip strike tick and blade tip/dir (from trail.json) so the page can draw the Linette lance.
# usage: pack_thrust8.py <hero_thrust3_v1 dir> <atlas json> <out png>
import json,sys,os
from PIL import Image
src,aj,op=sys.argv[1:4];A=json.load(open(aj));CL=json.load(open(src+'/clips.json'));TR=json.load(open(src+'/trail.json'))
# atlas json may already have been merged once: drop old sheet entry
if os.path.basename(op) in A['sheets']:
    i=A['sheets'].index(os.path.basename(op));A['sheets'].pop(i);A['cells'].pop(i);A['anims']={k:v for k,v in A['anims'].items() if not k.startswith('thit')}
s=len(A['sheets']);cells=[];crops=[];X=Y=RH=0;W=2048
for k,T in CL.items():
    A['anims']['t'+k]=[]
    for i,t in enumerate(T):
        im=Image.open(f'{src}/frames/{k}/{i:02d}.png').convert('RGBA');b=im.getbbox();c=im.crop(b);w,h=c.size
        if X+w>W: X=0;Y+=RH+1;RH=0
        cells.append([X,Y,w,h,128-b[0],189-b[1]]);crops.append((c,X,Y));X+=w+1;RH=max(RH,h)
        A['anims']['t'+k].append([s,len(cells)-1,t])
sheet=Image.new('RGBA',(W,Y+RH));[sheet.paste(c,(x,y)) for c,x,y in crops];sheet.save(op,optimize=True)
A['sheets'].append(os.path.basename(op));A['cells'].append(cells)
A['thr']={k:{'tick':v['tick'],'tip':v['tip'],'dir':v['dir'],'big':v['big'],'heavy':v['heavy']} for k,v in TR.items()}
A['_doc']+=' | sheet hero_thr.png = all-thrust 3-hit (hero_thrust3_v1): thit<n>_<dir>; thr = strike tick + blade tip/dir for the code-drawn trail'
json.dump(A,open(aj,'w'));print(len(cells),'frames',sheet.size)
