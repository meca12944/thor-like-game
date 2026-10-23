# Make the "other hand" thrust key pose from a right-hand lunge frame: the extended arm's shoulder->elbow->wrist vectors are copied onto the
# other shoulder, and the formerly extended arm is pulled back by the hip. Writes [orig, mid, swapped] keypoint frames for animate-with-skeleton.
# usage: swap_arms.py <lunge_kp.json> <out.json> <EXTENDED: LEFT|RIGHT> <back dir x: -1 facing right, +1 facing left>
import json,sys
kp=json.load(open(sys.argv[1]))['keypoints']; E=sys.argv[3]; O='LEFT' if E=='RIGHT' else 'RIGHT'; bx=float(sys.argv[4])
K={p['label']:dict(p) for p in kp}
def v(a,b): return (K[b]['x']-K[a]['x'],K[b]['y']-K[a]['y'])
se,ew=v(E+' SHOULDER',E+' ELBOW'),v(E+' ELBOW',E+' ARM')
T={k:dict(p) for k,p in K.items()}
T[O+' ELBOW']['x']=K[O+' SHOULDER']['x']+se[0]; T[O+' ELBOW']['y']=K[O+' SHOULDER']['y']+se[1]
T[O+' ARM']['x']=T[O+' ELBOW']['x']+ew[0];      T[O+' ARM']['y']=T[O+' ELBOW']['y']+ew[1]
T[E+' ELBOW']['x']=K[E+' SHOULDER']['x']+bx*12/256; T[E+' ELBOW']['y']=K[E+' SHOULDER']['y']+10/256
T[E+' ARM']['x']=K[E+' SHOULDER']['x']+bx*24/256;   T[E+' ARM']['y']=K[E+' SHOULDER']['y']+21/256
M={k:{**p,'x':(K[k]['x']+T[k]['x'])/2,'y':(K[k]['y']+T[k]['y'])/2} for k,p in K.items()}
clean=lambda D:[{'x':min(1,max(0,p['x'])),'y':min(1,max(0,p['y'])),'label':p['label'],'z_index':int(p.get('z_index',0))} for p in D.values()]
json.dump([clean(K),clean(M),clean(T)],open(sys.argv[2],'w')); print('swap',E,'->',O)
