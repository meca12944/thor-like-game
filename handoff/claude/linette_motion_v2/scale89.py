# 리네트 키 = 주인공의 89% (사장님 10-23 "89프로 해주고"). 방향마다 서기 키를 재서 그 방향 동작 전체에 같은 배율(동작 하나에 한 번, pxscale).
# 주인공 서기 키: 옆 122 · 정면 118 · 뒷면 126 (대각선은 게임에서 옆 그림과 나란히 보이므로 옆 기준).
# 새 시트 이름(linette8s_*)으로 써서 폰 캐시에 옛 그림이 남지 않게 함. thrust·casttip(바늘 끝 위치)도 같은 배율.
import json,os,sys,numpy as np
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));sys.path.insert(0,ROOT+'/handoff/claude/hero8_fix_v1')
from pxscale import pxscale
J=ROOT+'/test128/assets/anim/linette8.json';A=json.load(open(J))
if A.get('_scale89'):sys.exit('already scaled')
HERO={'side':122,'south':118,'north':126};R=0.89
def idle_h(d):   # 서기 첫 장: 발(앵커) ~ 머리 꼭대기(목 위 좁은 줄)
    s,c,_=A['anims']['idle_'+d][0][:3];x,y,w,h,ax,ay=A['cells'][s][c];im=np.array(IMS[s].crop((x,y,x+w,y+h)))[...,3]>40
    rows=im.any(1);top=np.nonzero(rows)[0].min();return ay-top
IMS=[Image.open(ROOT+'/test128/assets/'+p).convert('RGBA') for p in A['sheets']]
F={}
for d in A['dirs']:
    ref=HERO['south' if d=='south' else 'north' if d=='north' else 'side'];F[d]=round(ref*R/idle_h(d),4)
print('배율',F)
owner={}
for k,L in A['anims'].items():
    d=k.rsplit('_',1)[1]
    for e in L:owner.setdefault((e[0],e[1]),d)
newcells=[[None]*len(c) for c in A['cells']];tiles=[[] for _ in A['cells']]
for s,cl in enumerate(A['cells']):
    for c,(x,y,w,h,ax,ay) in enumerate(cl):
        f=F.get(owner.get((s,c)),1.0);t=IMS[s].crop((x,y,x+w,y+h))
        if abs(f-1)>1e-3:
            # 앵커가 정확히 같은 자리에 오도록 앵커 둘레를 넉넉히 둔 뒤 줄이고 다시 자름
            t2=pxscale(t,f);b=t2.getbbox() or (0,0,1,1)
            nax,nay=ax*f-b[0],ay*f-b[1];t=t2.crop(b);ax,ay=round(nax),round(nay)
        tiles[s].append((c,t,ax,ay))
newsheets=[]
for s,T in enumerate(tiles):
    W=2048;x=y=rowh=0;pos=[]
    for c,t,ax,ay in T:
        w,h=t.size
        if x+w>W:x=0;y+=rowh+1;rowh=0
        pos.append((c,t,x,y,ax,ay));x+=w+1;rowh=max(rowh,h)
    sh=Image.new('RGBA',(W,y+rowh),(0,0,0,0))
    for c,t,x0,y0,ax,ay in pos:sh.paste(t,(x0,y0));newcells[s][c]=[x0,y0,t.size[0],t.size[1],ax,ay]
    name=A['sheets'][s].replace('anim/linette8_','anim/linette8s_');sh.save(ROOT+'/test128/assets/'+name,lossless=True,method=6);newsheets.append(name)
A['sheets']=newsheets;A['cells']=newcells
for k,v in A['thrust'].items():f=F[k.rsplit('_',1)[1]];v['tip']=[round(v['tip'][0]*f,1),round(v['tip'][1]*f,1)]
for k,v in A['casttip'].items():f=F[k.rsplit('_',1)[1]];A['casttip'][k]=[[round(p[0]*f),round(p[1]*f)] for p in v]
A['figH']=round(117*np.mean(list(F.values())),1);A['_scale89']={'ratio':R,'factors':F,'note':'owner 10-23: Linette height = 89% of the hero in every direction (hero idle: side 122, front 118, back 126)'}
json.dump(A,open(J,'w'),ensure_ascii=False,separators=(',',':'));print('done',newsheets[:2])
