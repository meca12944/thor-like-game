import sys;sys.path.insert(0,'.')
from h8lib import *;import h8lib
def lean(R,n):
    h8lib._im.clear();s,j,k,H=load(R);L=H['anims'].get(n)
    if not L: return None
    out=[]
    for f in L:
        im,ax,ay=cell(R,H,f[0],f[1]);a=im.split()[3].load();W,Hh=im.size;b=im.split()[3].point(lambda v:255 if v>40 else 0).getbbox()
        def cx(y0,y1):
            xs=[x for y in range(max(0,y0),min(Hh,y1)) for x in range(W) if a[x,y]>40];return sum(xs)/len(xs) if xs else None
        top=b[1];h=b[3]-b[1]
        head=cx(top,top+int(h*.18));hip=cx(top+int(h*.45),top+int(h*.6))
        out.append((head-hip)/(h*.4))   # 머리-엉덩이 x 차 / 그 사이 높이 = 기울기(tan)
    import math;m=sum(out)/len(out);return round(math.degrees(math.atan(m)),1)
for n in ['walk_right','walk_dr','walk_up','walk_down','walk_n','run_right','run_dr','run_up','run_down','run_n']:
    print(n,'옛',lean('old0',n),'도 | 새',lean('fix2',n),'도')
