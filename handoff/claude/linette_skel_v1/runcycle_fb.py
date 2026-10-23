# procedural run cycle for FRONT (south) / BACK (north) view, from the estimated start pose:
# legs lift toward the camera (knee rises, foot tucks), alternate every half cycle; lower foot stays on the ground (+2px flight);
# sword arm (lower wrist) keeps its trailing pose; the other arm pumps (hand rises to the chest and drops); slight head dip for the forward lean
import json,math,sys
kpf,out,N=sys.argv[1],sys.argv[2],int(sys.argv[3])
K={k['label']:(k['x']*256,k['y']*256,int(k.get('z_index',0))) for k in json.load(open(kpf))['keypoints']}
sword='RIGHT' if K['RIGHT ARM'][1]>K['LEFT ARM'][1] else 'LEFT';free='LEFT' if sword=='RIGHT' else 'RIGHT'
d=lambda a,b:math.hypot(K[a][0]-K[b][0],K[a][1]-K[b][1])
LT=max(18,(d('LEFT HIP','LEFT KNEE')+d('RIGHT HIP','RIGHT KNEE'))/2);LS=max(16,(d('LEFT KNEE','LEFT LEG')+d('RIGHT KNEE','RIGHT LEG'))/2)
LU=(d('LEFT SHOULDER','LEFT ELBOW')+d('RIGHT SHOULDER','RIGHT ELBOW'))/2;LF=(d('LEFT ELBOW','LEFT ARM')+d('RIGHT ELBOW','RIGHT ARM'))/2
GROUND=max(K['LEFT LEG'][1],K['RIGHT LEG'][1])
def leg(side,t):
    hx,hy=K[side+' HIP'][:2];lift=max(0,math.sin(2*math.pi*t));back=max(0,-math.sin(2*math.pi*t))
    kn=(hx+(1 if side=='LEFT' else -1)*1.5*lift*0,hy+LT*(1-0.55*lift)+2*back)
    an=(kn[0],kn[1]+LS*(1-0.75*lift)-4*back)
    return kn,an
frames=[]
for i in range(N):
    t=i/N
    lk,la=leg('LEFT',t);rk,ra=leg('RIGHT',t+0.5)
    dy=(GROUND-max(la[1],ra[1]))-2*max(0,math.cos(4*math.pi*t))
    J={}
    for n in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','LEFT SHOULDER','RIGHT SHOULDER',sword+' ELBOW',sword+' ARM'):J[n]=(K[n][0],K[n][1]+2)  # head/shoulders dip 2px (lean)
    f=0.5+0.5*math.sin(2*math.pi*t+math.pi)          # free arm forward when the opposite leg is forward
    sx,sy=J[free+' SHOULDER'];J[free+' ELBOW']=(sx+(4 if free=='LEFT' else -4),sy+LU*(0.95-0.35*f));J[free+' ARM']=(sx+(2 if free=='LEFT' else -2)*f,J[free+' ELBOW'][1]-LF*(0.15+0.75*f)+LF*0.5)
    J['LEFT HIP'],J['RIGHT HIP']=K['LEFT HIP'][:2],K['RIGHT HIP'][:2];J['LEFT KNEE'],J['LEFT LEG'],J['RIGHT KNEE'],J['RIGHT LEG']=lk,la,rk,ra
    J['NECK']=((J['LEFT SHOULDER'][0]+J['RIGHT SHOULDER'][0])/2,(J['LEFT SHOULDER'][1]+J['RIGHT SHOULDER'][1])/2)
    frames.append([{'x':min(1,max(0,p[0]/256)),'y':min(1,max(0,(p[1]+dy)/256)),'label':n,'z_index':K.get(n,(0,0,0))[2]} for n,p in J.items()])
json.dump(frames,open(out,'w'));print('sword arm',sword,'LT',round(LT),'LS',round(LS),'ground',round(GROUND))
