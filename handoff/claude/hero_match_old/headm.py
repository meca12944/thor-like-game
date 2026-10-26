import sys;sys.path.insert(0,'.')
from h8lib import *;import numpy as np
from fxclean import skin
def metr(im):
    a=np.array(im);al=a[...,3]>40;ys,xs=np.where(al);top=ys.min();bot=ys.max();H=bot-top
    sk=np.array([[skin(tuple(p)) for p in row] for row in a])
    fy,fx=np.where(sk[:top+int(H*.3)] if True else sk)
    face=(fy.max()-fy.min()+1, fx.max()-fx.min()+1) if len(fy) else (0,0)
    def w(fr0,fr1):
        r=[(np.where(al[y])[0]) for y in range(top+int(H*fr0),top+int(H*fr1))];ws=[x.max()-x.min() for x in r if len(x)];return round(float(np.median(ws)),1)
    return dict(H=int(H),face_h=int(face[0]),face_w=int(face[1]),head_w=w(.02,.15),shoulder_w=w(.22,.30))
if __name__=='__main__':
    s,j,k,H=load('fix2')
    for n,i in [('idle_down',0),('hurt_down',0),('walk_down',0),('idle_right',0),('hurt_right',0),('dash_up',1),('dash_up',2),('dash_up',3)]:
        f=H['anims'][n][i];im,ax,ay=cell('fix2',H,f[0],f[1]);print(n,i,metr(im))
    for g in ['01_hit_down','02_hit_right','06_dash_ur']:
        print(g,metr(Image.open('g81/'+g+'_game.png')))
