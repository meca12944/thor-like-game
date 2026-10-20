# Thrust trail data for the engine (no baked effects in the sprites, same as the hero): for each atk clip find the needle tip in the
# full-lunge frame and the needle direction (principal axis of the thin pixels near the tip). Writes atlas/linette8.json "thrust".
import json,glob,os
import numpy as np
from PIL import Image
H=os.path.dirname(os.path.abspath(__file__)); A=json.load(open(H+'/atlas/linette8.json'))
FACE={'right':(1,0),'left':(-1,0),'down':(1,0.35),'up':(1,-0.45)}   # down/up use the diagonal thrust art (down-right / up-right)
LUNGE=8                                                          # frame index of the full extension in every atk clip
out={}
for m in ('atk1','atk2','atk3'):
    for d,f in FACE.items():
        im=np.asarray(Image.open(sorted(glob.glob(f'{H}/frames_polished/{m}/{d}/*.png'))[LUNGE]))[...,3]>40
        ys,xs=np.nonzero(im); fv=np.array(f)/np.hypot(*f); proj=xs*fv[0]+ys*fv[1]; i=proj.argmax(); tip=np.array([xs[i],ys[i]],float)
        near=np.hypot(xs-tip[0],ys-tip[1])<34; P=np.stack([xs[near],ys[near]],1).astype(float); P-=P.mean(0)
        v=np.linalg.svd(P,full_matrices=False)[2][0]; v=v if v@fv>0 else -v
        out[f'{m}_{d}']={'frame':LUNGE,'tip':[round(tip[0]-128,1),round(tip[1]-189,1)],'dir':[round(v[0],3),round(v[1],3)],'big':m=='atk3'}
A['thrust']=out; A['_doc']+=' thrust[<atk>_<dir>] = needle tip (relative to root) and direction at the full-lunge frame; the engine draws the trail.'
json.dump(A,open(H+'/atlas/linette8.json','w'),separators=(',',':')); print(json.dumps(out)[:600])
