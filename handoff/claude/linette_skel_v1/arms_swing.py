# Big run arm swing for side view (facing +x): each arm swings opposite its same-side thigh. Upper arm +-AMP deg from vertical, elbow bent BEND deg forward.
# usage: arms_swing.py <in_kp.json> <out_kp.json> [AMP=65] [BEND=80]
import json,math,sys
inp,out=sys.argv[1],sys.argv[2]; AMP=float(sys.argv[3]) if len(sys.argv)>3 else 65; BEND=float(sys.argv[4]) if len(sys.argv)>4 else 80
F=json.load(open(inp))
P=lambda f,l:[p for p in f if p['label']==l][0]
def thigh(f,s):  # signed thigh angle (rad), + = knee forward
    h,k=P(f,s+' HIP'),P(f,s+' KNEE'); return math.atan2(k['x']-h['x'],k['y']-h['y'])
mx=max(abs(thigh(f,s)) for f in F for s in ('LEFT','RIGHT')) or 1
for f in F:
    for s,o in (('LEFT','RIGHT'),('RIGHT','LEFT')):
        sh,el,hd=P(f,s+' SHOULDER'),P(f,s+' ELBOW'),P(f,s+' ARM')
        lu=math.hypot(el['x']-sh['x'],el['y']-sh['y']); lf=math.hypot(hd['x']-el['x'],hd['y']-el['y'])
        a=math.radians(AMP)*(thigh(f,o)/mx)          # arm follows the OPPOSITE leg
        b=a+math.radians(BEND)*(0.6+0.4*max(0,math.sin(a)))   # forearm bends forward, more when the arm is forward
        el['x']=sh['x']+lu*math.sin(a); el['y']=sh['y']+lu*math.cos(a)
        hd['x']=el['x']+lf*math.sin(b); hd['y']=el['y']+lf*math.cos(b)
        for p in (el,hd): p['x']=min(1,max(0,p['x'])); p['y']=min(1,max(0,p['y']))
json.dump(F,open(out,'w')); print('arm swing',AMP,BEND)
