# Thrust trail data for the engine (no baked effects in the sprites, same as the hero): for each atk clip find the needle tip in the
# full-lunge frame and the needle direction (principal axis of the thin pixels near the tip). Writes atlas/linette8.json "thrust".
import json,glob,os
import numpy as np
from PIL import Image
H=os.path.dirname(os.path.abspath(__file__)); A=json.load(open(H+'/atlas/linette8.json'))
def binary_opening(m,_k=None):   # 3x3 opening with numpy (erode then dilate)
    P=np.pad(m,1); er=np.ones_like(m)
    for dy in (0,1,2):
        for dx in (0,1,2): er&=P[dy:dy+m.shape[0],dx:dx+m.shape[1]]
    P=np.pad(er,1); di=np.zeros_like(m)
    for dy in (0,1,2):
        for dx in (0,1,2): di|=P[dy:dy+m.shape[0],dx:dx+m.shape[1]]
    return di
FACE={'right':(1,0),'left':(-1,0),'down':(0,1),'up':(0,-1)}   # down/up = true front/back thrusts (v2)
MAN=json.load(open(H+'/manifest.json'))['motions']
LUNGE=8                                                          # frame index of the full extension in every atk clip
out={}
for m in ('atk1','atk2','atk3'):
    for d,f in FACE.items():
        LUNGE=MAN[m][d]['lunge']; im=np.asarray(Image.open(sorted(glob.glob(f'{H}/frames_polished/{m}/{d}/*.png'))[LUNGE]))[...,3]>40
        thin=im & ~binary_opening(im) if d in ('down','up') else im   # front/back: the needle tip sits by the feet -> look at thin (1-2 px) pixels only
        ys,xs=np.nonzero(thin); fv=np.array(f)/np.hypot(*f); proj=xs*fv[0]+ys*fv[1]; i=proj.argmax(); tip=np.array([xs[i],ys[i]],float)
        ay,ax_=np.nonzero(im); near=np.hypot(ax_-tip[0],ay-tip[1])<34; P=np.stack([ax_[near],ay[near]],1).astype(float); P-=P.mean(0)
        v=np.linalg.svd(P,full_matrices=False)[2][0]; v=v if v@fv>0 else -v
        if d in ('down','up'): v=fv                                  # front/back: drive the trail straight down / up the screen
        rec={'frame':LUNGE,'tip':[round(float(tip[0])-128,1),round(float(tip[1])-189,1)],'dir':[round(float(v[0]),3),round(float(v[1]),3)],'big':m=='atk3'}
        if m=='atk3':   # both needles: second tip = farthest point off the first needle's line (>=4px away), near the front
            perp=np.abs((xs-tip[0])*v[1]-(ys-tip[1])*v[0]); cand=(perp>=4)&(proj>proj.max()-40)
            if cand.any():
                j=np.flatnonzero(cand)[proj[cand].argmax()]; rec['tip2']=[round(float(xs[j])-128,1),round(float(ys[j])-189,1)]
        out[f'{m}_{d}']=rec
A['thrust']=out; A['_doc']+=' thrust[<atk>_<dir>] = needle tip (relative to root) and direction at the full-lunge frame; the engine draws the trail.'
json.dump(A,open(H+'/atlas/linette8.json','w'),separators=(',',':')); print(json.dumps(out)[:600])
