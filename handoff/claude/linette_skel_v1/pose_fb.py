# Front/back view skeleton frames (south/north) built from the idle estimate: feet stay planted under the body (no splayed "crab" legs);
# motion = hip drop with knees bending forward, torso foreshortening (lean), arm angle, head tilt.
# usage: pose_fb.py <start_kp.json> <out.json> <dash|hurt>
import json,math,sys
kp=json.load(open(sys.argv[1]))['keypoints']; K={p['label']:[p['x']*256,p['y']*256] for p in kp}; Z={p['label']:int(p.get('z_index',0)) for p in kp}
HEAD=('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR')
def frame(drop,tor,arm,elb,head,hx=0):
    J={k:list(v) for k,v in K.items()}
    for s in ('LEFT','RIGHT'):
        J[s+' HIP'][1]+=drop; J[s+' KNEE'][1]+=drop*0.45; J[s+' HIP'][0]+=hx; J[s+' KNEE'][0]+=hx*0.5    # feet unchanged
    hip=[(J['LEFT HIP'][i]+J['RIGHT HIP'][i])/2 for i in (0,1)]; hip0=[(K['LEFT HIP'][i]+K['RIGHT HIP'][i])/2 for i in (0,1)]
    neck0=[(K['LEFT SHOULDER'][i]+K['RIGHT SHOULDER'][i])/2 for i in (0,1)]
    up=(hip0[1]-neck0[1])*tor; nk=[hip[0]+(neck0[0]-hip0[0])+hx*0.3,hip[1]-up]; dn=[nk[0]-neck0[0],nk[1]-neck0[1]]
    for p in HEAD: J[p]=[K[p][0]+dn[0],K[p][1]+dn[1]+head]
    if 'NECK' in J: J['NECK']=[K['NECK'][0]+dn[0],K['NECK'][1]+dn[1]]
    for s,sg in (('LEFT',1),('RIGHT',-1)):
        sh=[K[s+' SHOULDER'][0]+dn[0],K[s+' SHOULDER'][1]+dn[1]]; J[s+' SHOULDER']=sh
        lu=math.dist(K[s+' SHOULDER'],K[s+' ELBOW']); lf=math.dist(K[s+' ELBOW'],K[s+' ARM'])
        side=1 if K[s+' ELBOW'][0]>K[s+' SHOULDER'][0] else -1      # which screen side this arm hangs on
        a=math.radians(arm); el=[sh[0]+side*lu*math.sin(a),sh[1]+lu*math.cos(a)]; b=math.radians(arm+elb)
        J[s+' ELBOW']=el; J[s+' ARM']=[el[0]+side*lf*math.sin(b),el[1]+lf*math.cos(b)]
    return [{'x':min(1,max(0,v[0]/256)),'y':min(1,max(0,v[1]/256)),'label':k,'z_index':Z.get(k,0)} for k,v in J.items()]
P={
 'dash3':[(0,1,12,10,0),(4,0.97,10,8,0),(6,0.95,8,6,0),(6,0.95,8,6,0),(3,0.97,10,8,0),(1,1,12,10,0)],   # v3 front: less foreshortening (v2 made the ponytail spike up) # drop, torso scale, arm angle (deg out from body), elbow extra, head dy, hip dx
 'dash':[(0,1,12,10,0),(6,0.93,10,8,1),(8,0.88,8,6,2),(8,0.88,8,6,2),(4,0.94,10,8,1),(1,1,12,10,0)],   # v2: arms tucked to the body (v1 arms flew out sideways)
 'hurt':[(0,1,12,10,0),(4,1.02,20,12,-3),(6,1.0,26,16,-4),(5,0.98,20,12,-2),(2,1,15,10,-1),(0,1,12,10,0)]}   # v2: smaller arm flinch
json.dump([frame(*p) for p in P[sys.argv[3]]],open(sys.argv[2],'w')); print(sys.argv[3],'ok')
