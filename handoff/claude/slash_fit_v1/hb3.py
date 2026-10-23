# 게임이 실제로 맞힌 자리(hitgrid.js) vs 검기 그림이 몹 몸(폭 2r+4, 키 h)에 닿아 보인 자리(빈 화면 녹화)
import json,sys,numpy as np
from PIL import Image
def masks(vd):
    info=json.load(open(vd+'info.json')); M=[]
    for i in range(3):
        U=np.zeros((720,1280),bool)
        for f,r in enumerate(info):
            if not r['gk'] or any(x['i']!=i for x in r['gk']): continue
            hx,hy=r['hx'],r['hy']
            a=np.asarray(Image.open(f'{vd}{f:03d}a.png').convert('RGB'),int); b=np.asarray(Image.open(f'{vd}{f:03d}b.png').convert('RGB'),int)
            U|=np.abs(a-b).sum(-1)>24
        M.append((np.cumsum(np.cumsum(U,0),1),hx,hy))
    return M
def score(vd,gj,quiet=False):
    G=json.load(open(gj)); M=masks(vd); W=G['r']+2; H=G['h']; out=[]
    for i,(ci,hx,hy) in enumerate(M):
        tp=fn=fp=0
        for gx,gy,hm in G['list']:
            hit=bool(hm>>i&1); sx,sy=hx+gx*3,hy+gy*3
            x0,y0,x1,y1=[int(round(v)) for v in (sx-W*3,sy-H*3,sx+W*3,sy)]
            vis=(ci[y1,x1]-ci[y0-1,x1]-ci[y1,x0-1]+ci[y0-1,x0-1])>0
            tp+=hit and vis; fn+=hit and not vis; fp+=vis and not hit
        out.append((tp,fn,fp))
        if not quiet: print(f"  {i+1}타: 맞은 자리 {tp+fn} 중 닿아 보임 {tp/max(1,tp+fn)*100:.0f}% | 닿아 보이는데 안 맞음 {fp} ({fp/max(1,tp+fp)*100:.0f}%)")
    return out
if __name__=='__main__': score(sys.argv[1],sys.argv[2])
