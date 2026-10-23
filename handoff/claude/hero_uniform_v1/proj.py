# side (east) skeleton frames -> south-east 3/4 (x*0.71, y+0.41*x like newatk/design34), body widths / face from q34/se_kp.json;
# back run frames -> rot_north ground. writes uni/<name>_kp.json
import json,glob,numpy as np
def L(f):
    d=json.load(open(f));d=d['keypoints'] if isinstance(d,dict) and 'keypoints' in d else d
    return {p['label']:np.array([p['x']*256,p['y']*256]) for p in d},{p['label']:int(p.get('z_index',0)) for p in d}
def out(O,Z):return [{'x':float(np.clip(v[0]/256,0,1)),'y':float(np.clip(v[1]/256,0,1)),'label':k,'z_index':Z.get(k,0)} for k,v in O.items()]
K,Z=L('q34/se_kp.json');SW={'RIGHT':'LEFT','LEFT':'RIGHT'}
pr=lambda v:np.array([v[0]*0.71,v[1]+0.41*v[0]])
def se(J):
    H=(J['LEFT HIP']+J['RIGHT HIP'])/2;hipc=(K['LEFT HIP']+K['RIGHT HIP'])/2;O={}
    O['NECK']=hipc+pr(J['NECK']-H)
    for lab in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):O[lab]=O['NECK']+(K[lab]-K['NECK'])
    for ds,ts in SW.items():
        sh=O['NECK']+(K[ts+' SHOULDER']-K['NECK']);O[ts+' SHOULDER']=sh;O[ts+' ELBOW']=sh+pr(J[ds+' ELBOW']-J[ds+' SHOULDER']);O[ts+' ARM']=O[ts+' ELBOW']+pr(J[ds+' ARM']-J[ds+' ELBOW'])
        hp=hipc+(K[ts+' HIP']-hipc)+(pr(H-H));O[ts+' HIP']=hp;O[ts+' KNEE']=hp+pr(J[ds+' KNEE']-J[ds+' HIP']);O[ts+' LEG']=O[ts+' KNEE']+pr(J[ds+' LEG']-J[ds+' KNEE'])
    return O
for name,src in (('walk_se','uni/walk_e'),('run_se','uni/run_e')):
    fr=[L(f)[0] for f in sorted(glob.glob(src+'/*_kp.json'))]
    # bob: keep the side clip's hip height change; ground the lowest foot of the clip on the idle ground
    P=[se(J) for J in fr];bob=[((J['LEFT HIP']+J['RIGHT HIP'])/2)[1] for J in fr];b0=min(bob)
    G=max(K['LEFT LEG'][1],K['RIGHT LEG'][1]);Pl=[]
    low=max(max(O['LEFT LEG'][1],O['RIGHT LEG'][1]) for O in P)
    for O,b in zip(P,bob):
        for k in O:O[k]=O[k]+np.array([0,G-low+(b-b0)*0])
        Pl.append(out(O,Z))
    json.dump(Pl,open(f'uni/{name}_kp.json','w'));print(name,len(Pl))
# back run: old back-run skeleton, grounded on rot_north
N,ZN=L('q34/north_kp.json');GN=max(N['LEFT LEG'][1],N['RIGHT LEG'][1])
fr=[L(f) for f in sorted(glob.glob('uni/run_n_old/*_kp.json'))];low=max(max(J['LEFT LEG'][1],J['RIGHT LEG'][1]) for J,_ in fr)
cx=np.mean([((J['LEFT HIP']+J['RIGHT HIP'])/2)[0] for J,_ in fr]);nc=((N['LEFT HIP']+N['RIGHT HIP'])/2)[0]
json.dump([out({k:v+np.array([nc-cx,GN-low]) for k,v in J.items()},ZN) for J,_ in fr],open('uni/run_n_kp.json','w'));print('run_n',len(fr))
