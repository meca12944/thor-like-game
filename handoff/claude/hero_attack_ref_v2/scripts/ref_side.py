# reference = the in-game side combo (owner-approved). keys from its estimated skeletons (L/R made consistent),
# + forward lean x1.4 (upper body rotated about the hips), finisher arm swing widened toward 80 deg, bones kept, mids -> 15 frames
import json,math
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
man=json.load(open(P+'all/manifest.json'))
UPPER=['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','NECK','LEFT SHOULDER','RIGHT SHOULDER','LEFT ELBOW','RIGHT ELBOW','LEFT ARM','RIGHT ARM']
BONES=[('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG')]
def load(p): return {k['label']:[k['x']*256,k['y']*256,int(k.get('z_index',0))] for k in json.load(open(p))['keypoints']}
def rot(p,c,a): s,co=math.sin(a),math.cos(a);x,y=p[0]-c[0],p[1]-c[1];return [c[0]+x*co-y*s,c[1]+x*s+y*co,p[2]]
for h in ['hit1','hit2','hit3']:
    N=len(man[h+'_right']);K=[load(P+f'all/{h}_right/k{i}_kpfix.json') for i in range(N)];E=[]
    for k in K:
        hip=((k['LEFT HIP'][0]+k['RIGHT HIP'][0])/2,(k['LEFT HIP'][1]+k['RIGHT HIP'][1])/2)
        nk=k['NECK'];lean=math.atan2(nk[0]-hip[0],hip[1]-nk[1])  # current forward lean (facing +x)
        add=max(0.0,lean)*0.4+math.radians(6)                       # +40% of the lean (and a little even when upright)
        e={l:list(v) for l,v in k.items()}
        for l in UPPER: e[l]=rot(k[l],hip,add)
        if h=='hit3':  # finisher: open the sword arm's swing toward 80 deg from its start
            sh=e['LEFT SHOULDER'];a0=math.atan2(K[0]['LEFT ARM'][1]-K[0]['LEFT SHOULDER'][1],K[0]['LEFT ARM'][0]-K[0]['LEFT SHOULDER'][0])
            for l in ['LEFT ELBOW','LEFT ARM']:
                a=math.atan2(e[l][1]-sh[1],e[l][0]-sh[0]);d=(a-a0+math.pi)%(2*math.pi)-math.pi;e[l]=rot(e[l],sh,d*0.35)
        for p,c in BONES:  # keep the key's bone lengths
            L=math.dist(k[p][:2],k[c][:2]);dx,dy=e[c][0]-e[p][0],e[c][1]-e[p][1];dd=math.hypot(dx,dy) or 1;e[c][0]=e[p][0]+dx/dd*L;e[c][1]=e[p][1]+dy/dd*L
        E.append(e)
    seq=[]
    for i,e in enumerate(E):
        seq.append(e)
        if i<N-1: seq.append({l:[(e[l][0]+E[i+1][l][0])/2,(e[l][1]+E[i+1][l][1])/2,e[l][2]] for l in e})
    out=[[{'x':v[0]/256,'y':v[1]/256,'label':l,'z_index':v[2]} for l,v in f.items()] for f in seq[:15]]
    json.dump(out,open(P+f'a4/{h}_east.json','w'))
    json.dump(out,open(P+f'a4/{h}_east_exag.json','w'));print(h,len(out))
