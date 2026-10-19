# procedural Ys8-style run cycle for PixelLab animate-with-skeleton-v3 (side view, facing east; mirror x for west)
# rest joints from /estimate-skeleton of the idle frame; legs: thigh swing +-38 deg, knee flex 20..100 deg in swing; torso lean 14 deg;
# sword (right) arm trails back-low, free (left) arm pumps opposite the left leg; pelvis bob keeps the lower foot on the ground, +3 px in flight
import json,math,sys
N=int(sys.argv[1]) if len(sys.argv)>1 else 12
K={k['label']:(k['x']*256,k['y']*256,k.get('z_index',0)) for k in json.load(open('reftrail_kp.json'))['keypoints']}
P=((K['LEFT HIP'][0]+K['RIGHT HIP'][0])/2,(K['LEFT HIP'][1]+K['RIGHT HIP'][1])/2)
d=lambda a,b:math.hypot(K[a][0]-K[b][0],K[a][1]-K[b][1])
LT=(d('LEFT HIP','LEFT KNEE')+d('RIGHT HIP','RIGHT KNEE'))/2;LS=(d('LEFT KNEE','LEFT LEG')+d('RIGHT KNEE','RIGHT LEG'))/2
LU=(d('LEFT SHOULDER','LEFT ELBOW')+d('RIGHT SHOULDER','RIGHT ELBOW'))/2;LF=(d('LEFT ELBOW','LEFT ARM')+d('RIGHT ELBOW','RIGHT ARM'))/2
GROUND=max(K['LEFT LEG'][1],K['RIGHT LEG'][1]);LEAN=math.radians(5)
def rot(pt,c,a):x,y=pt[0]-c[0],pt[1]-c[1];return (c[0]+x*math.cos(a)-y*math.sin(a)*-1*0+x*0+ (x*math.cos(a)+y*math.sin(a))-x , c[1]+(-x*math.sin(a)+y*math.cos(a)))
def lean(pt):  # rotate upper body forward (toward +x) about the pelvis
    x,y=pt[0]-P[0],pt[1]-P[1];a=LEAN;return (P[0]+x*math.cos(a)-y*math.sin(a),P[1]+x*math.sin(a)+y*math.cos(a))
def leg(hip,t):
    th=math.radians(38)*math.sin(2*math.pi*t)+math.radians(4);ph=math.radians(20+80*max(0,math.cos(2*math.pi*t)))
    kn=(hip[0]+LT*math.sin(th),hip[1]+LT*math.cos(th));an=(kn[0]+LS*math.sin(th-ph),kn[1]+LS*math.cos(th-ph));return kn,an
def arm(sh,a_up,bend):
    el=(sh[0]+LU*math.sin(a_up),sh[1]+LU*math.cos(a_up));fo=a_up+bend;wr=(el[0]+LF*math.sin(fo),el[1]+LF*math.cos(fo));return el,wr
frames=[]
for i in range(N):
    t=i/N
    lh,rh=K['LEFT HIP'][:2],K['RIGHT HIP'][:2]
    lk,la=leg(lh,t+0.5);rk,ra=leg(rh,t)
    drop=GROUND-max(la[1],ra[1]);fl=3*max(0,math.cos(4*math.pi*t))  # lower foot on the ground; small lift in flight
    dy=drop-fl
    J={}
    for n in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','LEFT SHOULDER','RIGHT SHOULDER'):J[n]=lean(K[n][:2])
    J['RIGHT ELBOW'],J['RIGHT ARM']=(lean(K['RIGHT ELBOW'][:2]),lean(K['RIGHT ARM'][:2]))   # sword arm: keep the trailing pose of the first frame
    sw=math.radians(45)*math.sin(2*math.pi*(t+0.5)+math.pi)                                                                # free arm opposite the left leg
    J['LEFT ELBOW'],J['LEFT ARM']=arm(J['LEFT SHOULDER'],sw,math.radians(95))
    J['LEFT HIP'],J['RIGHT HIP'],J['LEFT KNEE'],J['LEFT LEG'],J['RIGHT KNEE'],J['RIGHT LEG']=lh,rh,lk,la,rk,ra
    J['NECK']=((J['LEFT SHOULDER'][0]+J['RIGHT SHOULDER'][0])/2,(J['LEFT SHOULDER'][1]+J['RIGHT SHOULDER'][1])/2)
    frames.append([{'x':min(1,max(0,(p[0])/256)),'y':min(1,max(0,(p[1]+dy)/256)),'label':n,'z_index':int(K.get(n,(0,0,0))[2]) if n in K else 0} for n,p in J.items()])
json.dump(frames,open(f'run_kp_{N}_ref.json','w'))
from PIL import Image,ImageDraw
B=[('NECK','NOSE'),('NECK','LEFT SHOULDER'),('NECK','RIGHT SHOULDER'),('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),
   ('NECK','LEFT HIP'),('NECK','RIGHT HIP'),('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG')]
o=Image.new('RGB',(N*128,140),(40,40,50));g=ImageDraw.Draw(o)
for i,f in enumerate(frames):
    J={k['label']:(k['x']*256/2+i*128,k['y']*256/2-50) for k in f}
    for a,b in B:g.line([J[a],J[b]],fill=(255,120,120) if 'RIGHT' in a+b else (120,200,255),width=2)
    g.line([(i*128,GROUND/2-50),(i*128+127,GROUND/2-50)],fill=(90,90,90))
o.save(f'stick_{N}_ref.png');print('LT',round(LT),'LS',round(LS),'ground',round(GROUND))
