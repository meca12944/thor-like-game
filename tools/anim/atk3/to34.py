# side skeletons -> 3/4 (se = front-diagonal, ne = back-diagonal), same idea as q34/atk34.py but no in-betweens and up to 20 frames.
# torso keeps the 3/4 frame's breadth; limbs follow the side offsets foreshortened: forward dx -> (0.71dx, +-0.41dx).
# ne: legs/torso held more still (only 40% of the side lower-body motion) so the back view does not turn round.
import json,sys
side,kp3,view,out,swap=sys.argv[1:6];swap=swap=='1'   # swap=1: the 3/4 skeleton labels the sword hand LEFT (se_kp does)
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT') if swap else l
KK=json.load(open(kp3))['keypoints'];K={k['label']:(k['x']*256,k['y']*256) for k in KK};Z={k['label']:int(k.get('z_index',0)) for k in KK}
sg=1 if view=='se' else -1;low=1.0 if view=='se' else 0.4
T=lambda d,s=1:(0.71*d[0]*s,(d[1]+sg*0.41*d[0])*s)
sub=lambda a,b:(a[0]-b[0],a[1]-b[1]);add=lambda a,b:(a[0]+b[0],a[1]+b[1])
mid=lambda F,a,b:((F[a][0]+F[b][0])/2,(F[a][1]+F[b][1])/2)
kh=mid(K,'LEFT HIP','RIGHT HIP')
def frame(F,S0):
    J={};hc=add(kh,T(sub(mid(F,'LEFT HIP','RIGHT HIP'),mid(S0,'LEFT HIP','RIGHT HIP')),low))
    nk=add(add(hc,sub(K['NECK'],kh)),T(sub(sub(F['NECK'],mid(F,'LEFT HIP','RIGHT HIP')),sub(S0['NECK'],mid(S0,'LEFT HIP','RIGHT HIP'))),low))
    J['NECK']=nk
    for l in ['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','LEFT SHOULDER','RIGHT SHOULDER']:J[l]=add(nk,sub(K[l],K['NECK']))
    for l in ['LEFT HIP','RIGHT HIP']:J[l]=add(hc,sub(K[l],kh))
    for p,c,s in [('LEFT SHOULDER','LEFT ELBOW',1),('LEFT ELBOW','LEFT ARM',1),('RIGHT SHOULDER','RIGHT ELBOW',1),('RIGHT ELBOW','RIGHT ARM',1),
                ('LEFT HIP','LEFT KNEE',low),('LEFT KNEE','LEFT LEG',low),('RIGHT HIP','RIGHT KNEE',low),('RIGHT KNEE','RIGHT LEG',low)]:
        J[c]=add(add(J[p],sub(K[c],K[p])),T(sub(sub(F[c],F[p]),sub(S0[c],S0[p])),s))
    return J
D=json.load(open(side));R={}
S0={sw(k['label']):(k['x']*256,k['y']*256) for k in D['h1'][0]}   # rest = hit-1 ready pose for every hit (combo stays continuous)
for n,L in D.items():
    R[n]=[[{'x':v[0]/256,'y':v[1]/256,'label':l,'z_index':Z.get(l,0)} for l,v in frame({sw(k['label']):(k['x']*256,k['y']*256) for k in fr},S0).items()] for fr in L][:20]
json.dump(R,open(out,'w'));print(view,{n:len(L) for n,L in R.items()})
