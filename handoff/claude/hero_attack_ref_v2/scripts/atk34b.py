# side attack skeleton -> 3/4 view: torso keeps the 3/4 frame's breadth (translated with the hips / leaned with the neck),
# limbs take the side motion's offsets, foreshortened: forward dx -> (0.71 dx, +-0.41 dx)
import json,sys
side,kp3,view,out,swap=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]=='1'
LEGS=float(sys.argv[6]) if len(sys.argv)>6 else 1.0  # <1 damps the leg motion (back 3/4: big steps make PixelLab turn the body)
sw=lambda l:l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT') if swap else l
S=[{sw(k['label']):(k['x']*256,k['y']*256) for k in fr} for fr in json.load(open(side))]
KK=json.load(open(kp3))['keypoints'];K={k['label']:(k['x']*256,k['y']*256) for k in KK};Z={k['label']:int(k.get('z_index',0)) for k in KK}
sg=1 if view=='se' else -1
T=lambda d:(0.71*d[0],d[1]+sg*0.41*d[0])
sub=lambda a,b:(a[0]-b[0],a[1]-b[1]);add=lambda a,b:(a[0]+b[0],a[1]+b[1])
mid=lambda F,a,b:((F[a][0]+F[b][0])/2,(F[a][1]+F[b][1])/2)
S0=S[0];kh=mid(K,'LEFT HIP','RIGHT HIP')
def frame(F):
    J={};dh=T(sub(mid(F,'LEFT HIP','RIGHT HIP'),mid(S0,'LEFT HIP','RIGHT HIP')));hc=add(kh,(dh[0]*LEGS,dh[1]*LEGS))
    nk=add(add(hc,sub(K['NECK'],kh)),T(sub(sub(F['NECK'],mid(F,'LEFT HIP','RIGHT HIP')),sub(S0['NECK'],mid(S0,'LEFT HIP','RIGHT HIP')))))
    J['NECK']=nk
    for l in ['NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR','LEFT SHOULDER','RIGHT SHOULDER']:J[l]=add(nk,sub(K[l],K['NECK']))
    for l in ['LEFT HIP','RIGHT HIP']:J[l]=add(hc,sub(K[l],kh))
    for p,c in [('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),
                ('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG')]:
        d=T(sub(sub(F[c],F[p]),sub(S0[c],S0[p])))
        if 'KNEE' in c or 'LEG' in c: d=(d[0]*LEGS,d[1]*LEGS)
        J[c]=add(add(J[p],sub(K[c],K[p])),d)
    return J
seq=[]
for i,F in enumerate(S):
    seq.append(frame(F))
    if i<len(S)-1:
        G={l:((F[l][0]+S[i+1][l][0])/2,(F[l][1]+S[i+1][l][1])/2) for l in F};seq.append(frame(G))
json.dump([[{'x':v[0]/256,'y':v[1]/256,'label':l,'z_index':Z.get(l,0)} for l,v in J.items()] for J in seq[:15]],open(out,'w'));print(view,len(seq[:15]))
