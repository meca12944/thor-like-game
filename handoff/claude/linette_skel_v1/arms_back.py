# Run with both arms and needles pulled BACK (owner 10-20, like the hero's sword-dragging run).
# side:  arms_back.py side <in_kp.json> <out.json>            -> both arms angled back behind the body, near-straight, small bob with the stride
# front: arms_back.py fb   <frames_kp_glob_prefix> <n> <out.json> -> per-frame estimates of the existing front/back run, arms replaced by low arms held out/back at the sides
import json,math,sys,glob
def arm_set(f,s,sh,ua,fa,lu,lf,side=1):
    e=[sh['x']*256+side*lu*math.sin(math.radians(ua)),sh['y']*256+lu*math.cos(math.radians(ua))]
    w=[e[0]+side*lf*math.sin(math.radians(fa)),e[1]+lf*math.cos(math.radians(fa))]
    for p in f:
        if p['label']==s+' ELBOW': p['x'],p['y']=e[0]/256,e[1]/256
        if p['label']==s+' ARM': p['x'],p['y']=w[0]/256,w[1]/256
mode=sys.argv[1]; V1='--v1' in sys.argv
if mode=='side':
    F=json.load(open(sys.argv[2])); n=len(F)
    for i,f in enumerate(F):
        P={p['label']:p for p in f}; ph=math.sin(2*math.pi*i/n)
        for s,off in (('RIGHT',0),('LEFT',8)):
            sh=P[s+' SHOULDER']; lu=lf=14
            arm_set(f,s,sh,(-62 if V1 else -100)-off+4*ph,(-78 if V1 else -104)-off+5*ph,lu,lf)        # negative angle = behind (facing +x); v2: arms straight back (owner: needle no longer pokes forward)
    json.dump(F,open(sys.argv[3],'w'))
else:
    pre,n,out=sys.argv[2],int(sys.argv[3]),sys.argv[4]; F=[]
    for i in range(n):
        f=json.load(open(f'{pre}.f{i}.json'))['keypoints']; P={p['label']:p for p in f}; ph=math.sin(2*math.pi*i/n)
        for s in ('LEFT','RIGHT'):
            sh=P[s+' SHOULDER']; side=1 if P[s+' ELBOW']['x']>sh['x'] else -1
            arm_set(f,s,sh,22+3*ph*(1 if s=='LEFT' else -1),40,13,13,side)   # hands low and out at the sides, needles trail outward/back
        F.append([{'x':min(1,max(0,p['x'])),'y':min(1,max(0,p['y'])),'label':p['label'],'z_index':int(p.get('z_index',0))} for p in f])
    json.dump(F,open(out,'w'))
print('ok',mode)
