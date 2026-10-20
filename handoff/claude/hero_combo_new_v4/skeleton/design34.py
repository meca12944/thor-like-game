# diagonal (3/4) version of the new combo: the side design (newatk/design.py) projected to ↘ (se) / ↗ (ne) like the earlier
# atk34 press (forward x*0.71, y +/-0.41 per forward px), body widths / head offsets / sword arm from the 3/4 rotation keypoints.
import json,sys,numpy as np
sys.path.insert(0,'newatk');import design as D
def load(f):return {p['label']:np.array([p['x']*256,p['y']*256]) for p in json.load(open(f))['keypoints']},{p['label']:int(p.get('z_index',0)) for p in json.load(open(f))['keypoints']}
CFG={'se':dict(kp='q34/se_kp.json',sg=1,arm={'RIGHT':'LEFT','LEFT':'RIGHT'},leg={'RIGHT':'LEFT','LEFT':'RIGHT'}),
     'ne':dict(kp='q34/ne_kp.json',sg=-1,arm={'RIGHT':'RIGHT','LEFT':'LEFT'},leg={'RIGHT':'RIGHT','LEFT':'LEFT'})}
def proj(view,p,blend=1.0):
    c=CFG[view];K,Z=load(c['kp'])
    if not p.get('twoh'):p=dict(p);p['uL']=min(p['uL'],-12);p['fL']=min(p['fL'],-25)   # free hand stays behind the body (no hand crossing -> the sword keeps its hand)
    J=D.joints(p);H=(J['LEFT HIP']+J['RIGHT HIP'])/2
    hipc=(K['LEFT HIP']+K['RIGHT HIP'])/2;shc=(K['LEFT SHOULDER']+K['RIGHT SHOULDER'])/2
    pr=lambda v:np.array([v[0]*0.71,v[1]+c['sg']*0.41*v[0]])
    O={}
    nk=hipc+pr(J['NECK']-H);O['NECK']=nk
    for lab in ('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR'):O[lab]=nk+(K[lab]-K['NECK'])
    for ds,ts in c['arm'].items():   # design side ds -> 3/4 label ts
        sh=nk+(K[ts+' SHOULDER']-shc)+(shc-K['NECK']);O[ts+' SHOULDER']=sh
        O[ts+' ELBOW']=sh+pr(J[ds+' ELBOW']-J[ds+' SHOULDER']);O[ts+' ARM']=O[ts+' ELBOW']+pr(J[ds+' ARM']-J[ds+' ELBOW'])
    if p.get('twoh'):   # two-handed: the free hand grips the hilt next to the sword hand (2-bone IK from its own shoulder)
        sw=c['arm']['RIGHT'];fr=c['arm']['LEFT'];S0=O[fr+' SHOULDER'];T=O[sw+' ARM']+np.array([-3*c['sg'],2.0])
        u=np.linalg.norm(pr(J['LEFT ELBOW']-J['LEFT SHOULDER']));f=np.linalg.norm(pr(J['LEFT ARM']-J['LEFT ELBOW']))
        v=T-S0;dd=np.linalg.norm(v)
        if dd>u+f-0.5:   # out of reach: bring the GRIP in (both hands move to a shared point the free arm can reach)
            T=S0+v/dd*(u+f-0.5);Ssw=O[sw+' SHOULDER'];us=np.linalg.norm(O[sw+' ELBOW']-Ssw);fs=np.linalg.norm(O[sw+' ARM']-O[sw+' ELBOW'])
            G=T+np.array([3*c['sg'],-2.0]);w=G-Ssw;dw=np.linalg.norm(w)
            if dw>us+fs-0.5:G=Ssw+w/dw*(us+fs-0.5);w=G-Ssw;dw=np.linalg.norm(w)
            a2=(us*us-fs*fs+dw*dw)/(2*dw);h2=np.sqrt(max(0,us*us-a2*a2));e2=w/dw;n2=np.array([e2[1],-e2[0]])
            if n2[1]<0:n2=-n2
            O[sw+' ELBOW']=Ssw+e2*a2+n2*h2;O[sw+' ARM']=G;T=G+np.array([-3*c['sg'],2.0])
            v=T-S0;dd=np.linalg.norm(v)
            if dd>u+f-0.5:T=S0+v/dd*(u+f-0.5);v=T-S0;dd=np.linalg.norm(v)
        a_=(u*u-f*f+dd*dd)/(2*dd);h=np.sqrt(max(0,u*u-a_*a_));e=v/dd;nrm=np.array([e[1],-e[0]])
        if nrm[1]<0:nrm=-nrm   # elbow bends downward
        O[fr+' ELBOW']=S0+e*a_+nrm*h;O[fr+' ARM']=T
    for ds,ts in c['leg'].items():
        hp=hipc+pr(H-H)+(K[ts+' HIP']-hipc);O[ts+' HIP']=hp
        O[ts+' KNEE']=hp+pr(J[ds+' KNEE']-J[ds+' HIP']);O[ts+' LEG']=O[ts+' KNEE']+pr(J[ds+' LEG']-J[ds+' KNEE'])
    # hip travel (forward step) pressed too
    dH=pr(H-((D.hip0)+np.array([0,0])))*np.array([1,0])+np.array([0,0])
    for k in O:O[k]=O[k]+dH
    G=max(K['LEFT LEG'][1],K['RIGHT LEG'][1]);low=max(O['LEFT LEG'][1],O['RIGHT LEG'][1])
    for k in O:O[k]=O[k]+np.array([0,G-low])
    if blend<1:
        for k in O:O[k]=K[k]*(1-blend)+O[k]*blend
    return O,Z
def kp(view,p,blend=1.0):
    O,Z=proj(view,p,blend);return [{'x':float(min(1,max(0,v[0]/256))),'y':float(min(1,max(0,v[1]/256))),'label':k,'z_index':Z.get(k,0)} for k,v in O.items()]
if __name__=='__main__':
    from PIL import Image,ImageDraw
    B=[('NECK','LEFT HIP'),('NECK','RIGHT HIP'),('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG'),('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),('NECK','NOSE'),('LEFT SHOULDER','RIGHT SHOULDER'),('LEFT HIP','RIGHT HIP')]
    rows=[]
    for view in ('se','ne'):
        sword=CFG[view]['arm']['RIGHT']
        for name,fr in D.CLIPS.items():
            n=len(fr);frames=[kp(view,p,blend=(min(1,i/4) if name=='hit1' else 1)) for i,p in enumerate(fr)]
            json.dump(frames,open(f'newatk/{name}_{view}_kp.json','w'))
            o=Image.new('RGB',(n*90,150),(30,30,40));d=ImageDraw.Draw(o)
            for i,f in enumerate(frames):
                J={q['label']:(q['x']*256-128+45+i*90,q['y']*256-60) for q in f}
                for a,b in B:d.line([J[a],J[b]],fill=(255,110,110) if sword in a+b else (180,210,255),width=2)
            rows.append(o)
    W=max(r.width for r in rows);o=Image.new('RGB',(W,150*len(rows)),(30,30,40))
    for i,r in enumerate(rows):o.paste(r,(0,150*i))
    o.save('newatk/skel34_preview.png');print('ok')
