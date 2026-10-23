# True front/back thrusts (down = needle driven DOWN the screen in front of the body, up = needle driven UP past the head),
# skeleton frames built from the idle estimate. hand: RIGHT | LEFT | BOTH.  usage: atk_fb.py <idle_kp.json> <out.json> <south|north> <hand>
import json,sys
kp=json.load(open(sys.argv[1]))['keypoints']; K={p['label']:[p['x']*256,p['y']*256] for p in kp}; Z={p['label']:int(p.get('z_index',0)) for p in kp}
view,hand=sys.argv[3],sys.argv[4]; S=1 if view=='south' else -1           # +1: thrust goes down the screen, -1: up
HEAD=('NOSE','LEFT EYE','RIGHT EYE','LEFT EAR','RIGHT EAR')
def arm(J,s,e,w):   # elbow / wrist offsets from the shoulder, x given toward the body's outside (side sign applied)
    side=1 if K[s+' ELBOW'][0]>K[s+' SHOULDER'][0] else -1; sh=J[s+' SHOULDER']
    J[s+' ELBOW']=[sh[0]+side*e[0],sh[1]+e[1]]; J[s+' ARM']=[sh[0]+side*w[0],sh[1]+w[1]]
def frame(phase,drop=0,step=0):
    J={k:list(v) for k,v in K.items()}
    for s in ('LEFT','RIGHT'): J[s+' HIP'][1]+=drop; J[s+' KNEE'][1]+=drop*0.5
    lead='RIGHT' if hand!='LEFT' else 'LEFT'; J[lead+' LEG'][1]+=step*S; J[lead+' KNEE'][1]+=step*S*0.6     # front foot steps toward the thrust
    for p in list(J):
        if any(t in p for t in ('SHOULDER','ELBOW','ARM','NECK'))+any(p==h for h in HEAD): J[p][1]+=drop*0.8
    arms=['RIGHT','LEFT'] if hand=='BOTH' else [hand]
    for s in arms:
        if phase=='wind': arm(J,s,(9,10*-S if S<0 else 6),(5,20 if S<0 else -6))            # cock the needle back (up by the shoulder / down by the hip)
        if phase=='wind2': arm(J,s,(11,12 if S<0 else 3),(8,24 if S<0 else -10))
        if phase=='hit': arm(J,s,(-1 if hand=='BOTH' else 1,14*S),(-6 if hand=='BOTH' else -2,30*S))   # arm driven straight along the thrust
        if phase=='half': arm(J,s,(5,8*S),(3,14*S))
    return [{'x':min(1,max(0,v[0]/256)),'y':min(1,max(0,v[1]/256)),'label':k,'z_index':Z.get(k,0)+(5 if (phase in('hit','half') and S>0 and ('ELBOW' in k or k.endswith(' ARM'))) else 0)} for k,v in J.items()]
seq=[frame('ready'),frame('wind',1),frame('wind2',3),frame('hit',4,5),frame('hit',4,5),frame('half',2,3),frame('ready')]
json.dump(seq,open(sys.argv[2],'w')); print(view,hand,len(seq))
