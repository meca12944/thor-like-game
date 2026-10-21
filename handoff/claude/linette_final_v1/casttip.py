# Needle tip per cast frame (owner 10-21 "몇몇 동작에서 손에 실이 안나온다"): the skill thread starts at the needle in her throwing hand.
# Tip = farthest opaque pixel along the facing (right / down-right / up-right; mirrored for left ones) in the chest band, relative to the feet root.
# Written into atlas/linette8.json as casttip[clip] = [[x,y] per entry of the clip].
import json,os,numpy as np
from PIL import Image
H=os.path.dirname(os.path.abspath(__file__));A=json.load(open(H+'/atlas/linette8.json'))
D={'right':(1,0),'left':(-1,0),'down':(0.78,0.62),'downl':(-0.78,0.62),'up':(0.78,-0.62),'upl':(-0.78,-0.62)}
sh={};A['casttip']={}
for n,L in A['anims'].items():
    if not n.startswith('cast_'):continue
    dx,dy=D[n[5:]];out=[]
    for s,c,t in L:
        if s not in sh:sh[s]=np.array(Image.open(H+'/atlas/'+os.path.basename(A['sheets'][s])).convert('RGBA'))
        x,y,w,h,ax,ay=A['cells'][s][c];al=sh[s][y:y+h,x:x+w,3]>0;ys,xs=np.nonzero(al);rx,ry=xs-ax,ys-ay
        k=(ry>-110)&(ry<-35);rx,ry=rx[k],ry[k];i=np.argmax(rx*dx+ry*dy);out.append([int(rx[i]),int(ry[i])])
    A['casttip'][n]=out
json.dump(A,open(H+'/atlas/linette8.json','w'),separators=(',',':'));print({k:v[7] for k,v in A['casttip'].items()})
