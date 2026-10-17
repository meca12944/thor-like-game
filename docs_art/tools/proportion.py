# Full-body proportion normalizer (docs_art/ref/user_proportion_ref.png template).
# usage: proportion.py <landmarks.txt> <src_root> <dst_root> [id ...]
#  landmarks line: <rel path w/o .png> <eye_y> <chin_y> <face_cx> [crotch=<y>] [child] [hunch] [aspect=<f>]
#  coords are in the source 900x1320 canvas. eye_y = eye line, chin_y = jaw tip (under any beard), crotch = top of leg split
#  (omit when hidden by robes/skirts: default legs = 0.60 of chin->feet, measured on the visible-leg cast).
#  Adult template : eye 207, chin 284 (eye-chin 77px ~ head 184px), hip/crotch 694, feet 1260.
#  Child template : eye 648, chin 716 (71px), hip 1037, feet 1260.
#  hunch: head size + leg length kept to template, torso keeps leg scale so a stooped pose stays stooped.
#  aspect: extra torso width factor (used for outfits_v3 so shoulder widths match the normalized busts).
import sys,json,numpy as np, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from normalize import warp
from PIL import Image
AD=dict(eye=207,chin=284,crotch=694,feet=1260); CH=dict(eye=648,chin=716,crotch=1037,feet=1260); LEGF=0.60
lmf,SRC,DST=sys.argv[1:4]; only=set(sys.argv[4:]); info={}
for l in open(lmf):
    if not l.strip() or l.startswith('#'): continue
    t=l.split(); p=t[0]; e,c,cx=map(int,t[1:4]); fl={}
    for x in t[4:]:
        k,_,v=x.partition('='); fl[k]=v
    cid=os.path.basename(p)
    if only and cid not in only: continue
    im=np.array(Image.open(f'{SRC}/{p}.png').convert('RGBA')); H,W=im.shape[:2]
    a=im[...,3]>100; feet=int(np.nonzero(a)[0].max())
    cr=int(fl['crotch']) if fl.get('crotch') else int(round(feet-LEGF*(feet-c)))
    T=dict(CH if 'child' in fl else AD)
    dt=T['chin']-T['eye']; s_h=dt/(c-e); legv=(T['feet']-T['crotch'])/(feet-cr)
    if 'hunch' in fl:
        T['chin']=int(round(T['crotch']-(cr-c)*legv)); T['eye']=T['chin']-dt; torv=legv
    else: torv=(T['crotch']-T['chin'])/(cr-c)
    asp=float(fl.get('aspect',1.0))
    band=a[int(c+0.3*(cr-c)):cr]; bx=cx if 'group' in fl else float(np.median(np.nonzero(band)[1]))
    sh_t=T['chin']+0.55*dt
    o=warp(im,(W,H),[T['eye'],T['chin'],T['crotch'],T['feet']],[e,c,cr,feet],
           [0,T['chin'],sh_t,T['crotch'],H],[s_h,s_h,torv*asp,legv,legv],W/2,[T['chin'],T['crotch']],[cx,bx])
    os.makedirs(os.path.dirname(f'{DST}/{p}.png'),exist_ok=True)
    Image.fromarray(o,'RGBA').save(f'{DST}/{p}.png',optimize=True)
    info[cid]=dict(src_eye=e,src_chin=c,src_crotch=cr,head_scale=round(s_h,3),torso_scale=round(torv,3),leg_scale=round(legv,3),aspect=asp,
                   eye=T['eye'],chin=T['chin'],hip=T['crotch'],feet=T['feet'],template='child' if 'child' in fl else 'adult')
    print(cid,info[cid])
jf=os.path.join(os.path.dirname(os.path.abspath(lmf)),'proportion_applied.json')
old=json.load(open(jf)) if os.path.exists(jf) else {}
old.update(info); json.dump(old,open(jf,'w'),ensure_ascii=False,indent=1)
