# Build side-view (facing +x) skeleton frames from simple pose parameters, using bone lengths/head from a start-frame estimate.
# usage: pose_keys.py <start_kp.json> <out.json> <preset: dash|hurt>
import json,math,sys
kp=json.load(open(sys.argv[1]))['keypoints']; K={p['label']:(p['x']*256,p['y']*256) for p in kp}; Z={p['label']:int(p.get('z_index',0)) for p in kp}
d=lambda a,b:math.hypot(K[a][0]-K[b][0],K[a][1]-K[b][1]); mid=lambda a,b:((K[a][0]+K[b][0])/2,(K[a][1]+K[b][1])/2)
neck0=mid('LEFT SHOULDER','RIGHT SHOULDER'); hip0=mid('LEFT HIP','RIGHT HIP')
TOR=math.hypot(neck0[0]-hip0[0],neck0[1]-hip0[1]); TH=(d('LEFT HIP','LEFT KNEE')+d('RIGHT HIP','RIGHT KNEE'))/2; SH=(d('LEFT KNEE','LEFT LEG')+d('RIGHT KNEE','RIGHT LEG'))/2
UA=(d('LEFT SHOULDER','LEFT ELBOW')+d('RIGHT SHOULDER','RIGHT ELBOW'))/2; FA=(d('LEFT ELBOW','LEFT ARM')+d('RIGHT ELBOW','RIGHT ARM'))/2
GROUND=max(K['LEFT LEG'][1],K['RIGHT LEG'][1])
def V(ang,L): a=math.radians(ang); return (L*math.sin(a),L*math.cos(a))   # 0 = straight down, + = toward +x (forward)
def frame(lean,thR,knR,thL,knL,uaR,faR,uaL,faL,head=0):
    J={}
    for s,th,kn in (('RIGHT',thR,knR),('LEFT',thL,knL)):
        hx,hy=K[s+' HIP'][0]-hip0[0],K[s+' HIP'][1]-hip0[1]
        J[s+' HIP']=(hip0[0]+hx,hip0[1]+hy); k=V(th,TH); J[s+' KNEE']=(J[s+' HIP'][0]+k[0],J[s+' HIP'][1]+k[1]); a=V(th-kn,SH); J[s+' LEG']=(J[s+' KNEE'][0]+a[0],J[s+' KNEE'][1]+a[1])
    t=V(180-lean,TOR); nk=(hip0[0]+t[0],hip0[1]+t[1]); J['NECK']=nk   # torso points up, leaning forward by lean
    for s,ua,fa in (('RIGHT',uaR,faR),('LEFT',uaL,faL)):
        sx,sy=K[s+' SHOULDER'][0]-neck0[0],K[s+' SHOULDER'][1]-neck0[1]; sh=(nk[0]+sx,nk[1]+sy); J[s+' SHOULDER']=sh
        e=V(ua,UA); el=(sh[0]+e[0],sh[1]+e[1]); J[s+' ELBOW']=el; h=V(fa,FA); J[s+' ARM']=(el[0]+h[0],el[1]+h[1])
    dx,dy=nk[0]-neck0[0],nk[1]-neck0[1]; c,s_=math.cos(math.radians(head)),math.sin(math.radians(head))
    for p in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):
        x,y=K[p][0]-neck0[0],K[p][1]-neck0[1]; x,y=x*c-y*s_,x*s_+y*c; J[p]=(nk[0]+x,nk[1]+y)
    g=GROUND-max(J['LEFT LEG'][1],J['RIGHT LEG'][1])          # keep the lowest foot on the ground
    return [{'x':min(1,max(0,(v[0])/256)),'y':min(1,max(0,(v[1]+g)/256)),'label':k,'z_index':Z.get(k,0)} for k,v in J.items()]
P={ # lean, thR,knR, thL,knL, uaR,faR, uaL,faL, head
 'dash':[(8,15,30,-10,20,-20,10,20,40,0),(25,35,60,-30,30,-50,-30,-40,-20,0),(35,45,40,-45,20,-70,-50,-60,-40,5),(35,40,30,-40,25,-65,-45,-55,-35,5),(20,25,40,-20,30,-30,0,-20,10,0),(8,10,20,-5,10,-10,20,10,30,0)],
 'hurt':[(0,5,5,-5,5,5,20,-5,15,0),(-18,15,20,-10,10,40,70,-40,-10,-25),(-24,20,30,-12,15,55,90,-55,-25,-30),(-14,12,20,-8,10,30,50,-25,0,-15),(-5,6,10,-5,8,10,25,-10,10,-5),(0,5,5,-5,5,5,20,-5,15,0)]}
json.dump([frame(*p) for p in P[sys.argv[3]]],open(sys.argv[2],'w')); print(sys.argv[3],len(P[sys.argv[3]]),'frames')
