# 점프를 실제처럼 (사장님 10-23 "점프랑 공격 반동도 ... 현실처럼"): 마을 점프(Space)
#  전: 누르자마자 떠오르고(웅크림이 공중에서), 그림 8장을 30틱에 고르게 → 착지 웅크림이 아직 80칸 높이에서 나옴
#  후: 땅에서 웅크림(4틱, 달리기 점프는 0) -> 공중(30틱, 높이 곡선 그대로, 공중 그림만) -> 땅에서 착지 웅크림(8틱, 움직이거나 공격·대시하면 바로 끝)
#  그림이 땅/공중인지는 발 높이로 잰 표(H8.jumpPh: [땅 웅크림 장, 공중 장, 착지 장]).
import json,os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));HTML=ROOT+'/test128/index.html'
s=open(HTML).read()
PH={'jump_right':[[0,1],[2,3,4],[5,6,7]],'jump_left':[[0,1],[2,3,4],[5,6,7]],'jump_down':[[0,1,2],[3,4,5],[6,7,8]],
    'jump_up':[[0,1],[2,3,4,5,6],[7,9,11,14]],'rjump_right':[[],[0,1,2],[3,4,5,6,7,8,9]],'rjump_left':[[],[0,1,2],[3,4,5,6,7,8,9]]}
i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e]);H['jumpPh']=PH
s=s[:j]+json.dumps(H,separators=(',',':'),ensure_ascii=False)+s[e:]
R=[("jumpTicks:30,jumpLogical:84,","jumpTicks:30,jumpLogical:84,jumpPreTicks:4,jumpLandTicks:8,"),
("hero.jump={t:0,T:tk(FEEL.jumpTicks),run,","hero.jump={t:0,T:tk(FEEL.jumpTicks),pre:run?0:tk(FEEL.jumpPreTicks),land:tk(FEEL.jumpLandTicks),run,"),
("""  if(hero.jump){const J=hero.jump;J.t+=dt;atkPressed=false;dashPressed=false;const p=Math.min(1,J.t/J.T);hero.z=4*p*(1-p)*FEEL.jumpLogical/LSC;
   if(J.run){hero.vx=J.vx;hero.vy=J.vy;}
   if(p>=1){hero.jump=null;hero.z=0;burst(hero.x,hero.y-2,8,['#e8dcc0','#cbb894'],110,0,3);}}""",
"""  if(hero.jump){const J=hero.jump;J.t+=dt;const ta=J.t-(J.pre||0),p=Math.max(0,Math.min(1,ta/J.T)); // pre: crouch on the ground, air: parabola, land: absorb on the ground (motion lab 10-23)
   if(ta<J.T){atkPressed=false;dashPressed=false;}hero.z=ta>0&&ta<J.T?4*p*(1-p)*FEEL.jumpLogical/LSC:0;
   if(J.run&&ta<J.T){hero.vx=J.vx;hero.vy=J.vy;}
   if(ta>=J.T&&!J.landed){J.landed=true;burst(hero.x,hero.y-2,8,['#e8dcc0','#cbb894'],110,0,3);}
   if(J.landed&&(ta>=J.T+(J.land||0)||hero.moving||atkPressed||dashPressed)){hero.jump=null;hero.z=0;}}"""),
("""else if(h.jump){const L=(h.jump.run&&!vert&&(d==='right'||d==='left')&&H8.anims['rjump_'+d])?A('rjump'):A('jump');if(L)e=h8seq(L,Math.min(.999,h.jump.t/h.jump.T)*h8tot(L));}""",
"""else if(h.jump){const L=(h.jump.run&&!vert&&(d==='right'||d==='left')&&H8.anims['rjump_'+d])?A('rjump'):A('jump');const J=h.jump,PH=L&&H8.jumpPh&&H8.jumpPh[h8key(L)];
  if(L&&PH){const ta=J.t-(J.pre||0),[l,f]=ta<0?[PH[0],J.t/Math.max(J.pre,1e-3)]:ta<J.T?[PH[1],ta/J.T]:[PH[2],(ta-J.T)/Math.max(J.land||1,1e-3)],q=l.length?l:PH[1];e=L[q[Math.min(q.length-1,Math.floor(f*q.length))]];}
  else if(L)e=h8seq(L,Math.min(.999,h.jump.t/h.jump.T)*h8tot(L));} // ground crouch / air / landing frames from H8.jumpPh (motion lab 10-23)""")]
for a,b in R:
    assert s.count(a)==1,a[:60];s=s.replace(a,b)
# 아틀라스 배열 -> 이름 찾기 도우미
a="function heroCell8(){"
assert s.count(a)==1;s=s.replace(a,"let H8KEY=null;function h8key(L){if(!H8KEY){H8KEY=new Map();for(const k in H8.anims)H8KEY.set(H8.anims[k],k);}return H8KEY.get(L);}\n"+a)
open(HTML,'w').write(s);print('ok')
