# 회피대시·맞기 박자 (사장님 10-23 "3번까지 전부 인게임 적용해"). 그림은 그대로, 장마다 틱만 바꿈(합계는 그대로).
# 회피대시: 출발 순간이 가장 빠름(outCubic) -> 서 있는 장은 1틱, 숙인 장이 빠를 때 나오게. 맞기: 맞자마자 젖혀지고 가장 젖혀진 장을 가장 길게.
import json,os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));HTML=ROOT+'/test128/index.html';LJ=ROOT+'/test128/assets/anim/linette8.json'
HERO={'dash_right':[1,1,1,2,2,2,2,2,2,2],'dash_down':[1,1,1,2,2,2,3,3,2],'hurt_right':[1,6,5,4,4],'hurt_down':[1,1,2,6,5,5],'hurt_up':[1,1,2,6,5,5]}
LIN={'dash_right':[1,6,5,5],'dash_left':[1,6,5,5],'dash_south':[1,1,2,6,4,3],'dash_north':[1,1,2,6,4,3],
     'hurt_right':[1,2,7,5,4,3],'hurt_left':[1,2,7,5,4,3],'hurt_south':[1,6,6,5,4],'hurt_north':[1,6,6,5,4]}
def put(anims,T):
    for k,t in T.items():
        L=anims[k];assert len(L)==len(t),(k,len(L));old=sum(e[2] for e in L)
        assert sum(t)==old,(k,old,sum(t))
        for e,x in zip(L,t):e[2]=x
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e]);put(H['anims'],HERO)
H['_dodgehurt_note']='owner 10-23: dash/hurt ticks re-timed (handoff/claude/dodge_hurt_v1): lean when the dodge is fastest, recoil right on impact'
open(HTML,'w').write(s[:j]+json.dumps(H,separators=(',',':'),ensure_ascii=False)+s[e:])
A=json.load(open(LJ));put(A['anims'],LIN);json.dump(A,open(LJ,'w'),ensure_ascii=False,separators=(',',':'));print('ok')
