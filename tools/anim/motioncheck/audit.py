# Number-based motion audit for the check board: per clip, measure frame-to-frame jumps in body height / width / foot position,
# brightness drift and frame count, and flag clips that look off. Same numbering as board.py.
# usage: audit.py <test128 dir>
import sys,json,numpy as np
from PIL import Image
G=sys.argv[1]
def hero_atlas():
    s=open(f'{G}/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);return json.JSONDecoder().raw_decode(s[j:])[0]
def audit(A,sheets,motions,dirs,start,label):
    IM=[Image.open(f'{G}/assets/{p}').convert('RGBA') for p in sheets];n=start;out=[]
    for mo in motions:
        for d in dirs:
            L=A['anims'].get(f'{mo}_{d}')
            if not L:continue
            hs=[];ws=[];feet=[];lum=[]
            for f in L:
                cx,cy,w,h,ax,ay=A['cells'][f[0]][f[1]];a=np.array(IM[f[0]].crop((cx,cy,cx+w,cy+h)));al=a[...,3]>0
                ys,xs=np.nonzero(al);hs.append(ay-ys.min());ws.append(xs.max()-xs.min());feet.append(ys.max()-ay);lum.append(a[...,:3][al].mean())
            hs,ws,lum=np.array(hs),np.array(ws),np.array(lum);why=[]
            if len(L)<=4 and mo not in('hold','rec1','rec2','hurt'):why.append(f'장수 적음({len(L)}장)')
            jh=np.abs(np.diff(hs)).max() if len(hs)>1 else 0
            if jh>14 and mo in('idle','walk','run'):why.append(f'키가 한 번에 {int(jh)}px 튐')
            if lum.max()-lum.min()>18:why.append(f'밝기 들쭉날쭉({int(lum.max()-lum.min())})')
            if mo in('idle','walk','run') and max(feet)-min(feet)>6:why.append(f'발 위치 흔들림({max(feet)-min(feet)}px)')
            if why:out.append((n,mo,d,why))
            n+=1
    print(f'== {label}');[print(f'  {k}번 {mo} {d}: '+', '.join(w)) for k,mo,d,w in out] or print('  이상 없음')
    return n
H=hero_atlas();HD=['down','up','right','left']
n=audit(H,H['sheets'],['idle','walk','run','dash','jump','rjump','hold','rec1','rec2'],HD,1,'주인공 1 (움직이기)')
audit(H,H['sheets'],['hit1','hit2','hit3','hurt','hurtys','death','cast_s1','cast_s2','cast_s3'],HD,n,'주인공 2 (싸우기)')
L=json.load(open(f'{G}/assets/anim/linette8.json'))
audit(L,L['sheets'],['idle','walk','run','dash','jump','rjump','atk1','atk2','atk3','cast','hurt','death'],['down','downl','up','upl','right','left'],1,'리네트')
