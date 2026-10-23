# minimal BVH reader + forward kinematics -> world joint positions per frame
import numpy as np,re
def rot(axis,deg):
    a=np.radians(deg);c,s=np.cos(a),np.sin(a)
    if axis=='X':return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if axis=='Y':return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def load(path):
    tok=open(path).read().split();i=0;joints=[];stack=[];chans=[]
    while tok[i]!='MOTION':
        t=tok[i]
        if t in('ROOT','JOINT'):joints.append({'name':tok[i+1],'parent':stack[-1] if stack else -1,'off':None,'ch':[]});i+=2;continue
        if t=='End':joints.append({'name':joints[stack[-1]]['name']+'_end','parent':stack[-1],'off':None,'ch':[]});i+=2;continue
        if t=='{':stack.append(len(joints)-1)
        elif t=='}':stack.pop()
        elif t=='OFFSET':joints[stack[-1]]['off']=np.array(list(map(float,tok[i+1:i+4])));i+=4;continue
        elif t=='CHANNELS':n=int(tok[i+1]);joints[stack[-1]]['ch']=tok[i+2:i+2+n];i+=2+n;continue
        i+=1
    nf=int(tok[i+2]);ft=float(tok[i+5]);data=np.array(list(map(float,tok[i+6:])));nc=sum(len(j['ch']) for j in joints);data=data[:nf*nc].reshape(nf,nc)
    P=np.zeros((nf,len(joints),3))
    for f in range(nf):
        k=0;R=[None]*len(joints);T=[None]*len(joints)
        for j,J in enumerate(joints):
            loc=J['off'].copy();Rl=np.eye(3)
            for c in J['ch']:
                v=data[f,k];k+=1
                if c.endswith('position'):loc['XYZ'.index(c[0])]=v if J['parent']<0 else loc['XYZ'.index(c[0])]
                else:Rl=Rl@rot(c[0],v)
            if J['parent']<0:R[j]=Rl;T[j]=loc
            else:p=J['parent'];R[j]=R[p]@Rl;T[j]=T[p]+R[p]@loc
            P[f,j]=T[j]
    return [J['name'] for J in joints],P,ft
