"""Idempotent text patch: v2 hero-proportion NPC sprites (assets/npcs/v2/<id>.png + meta.json) in the town page.
Adds NPC_V2 loader, 4-direction facing, optional patrol path, and drawNpcV2 (crisp, logical-grid aligned).
NPCs without a v2 sheet keep the old drawNpc path.  Usage: python3 patch_npc_v2.py town/index.html town/tools/game.template.html"""
import sys
MARK = '[npc_v2]'
A_OLD = "function spawnNpc(id,x,y,o={}){"
A_NEW = """// [npc_v2] hero-proportion women (approved v2: 28 logical px = live hero, head 7 px = 4.0 heads, same baseline).
// Sheet assets/npcs/v2/<id>.png: rows down/left/right/up x [idle 4 (breathing) | walk 8]; meta.json = cell size/anchor/ranges.
// tweak: NPC_V2_CFG.idleTicks / walkTicks (60 fps ticks per frame), patrol speed (world px/s), stopNear (stop + face hero).
const NPC_V2_CFG={idleTicks:15,walkTicks:9,speed:42,stopNear:90,paths:{a_tailor:[[0,0],[130,0]]}};
const NPC_V2={};fetch('assets/npcs/v2/meta.json').then(r=>r.json()).then(j=>{Object.assign(NPC_V2,j);for(const n of npcs)npcV2(n);}).catch(()=>{});
function npcV2(n){const m=NPC_V2[n.id];if(!m||n.v2)return;const im=new Image();im.onload=()=>{n.v2={m,im};n.headH=(m.ch+3)/LSC/CS;
  const p=NPC_V2_CFG.paths[n.id];if(p&&!n.path){n.path=p.map(([dx,dy])=>[n.x+dx,n.y+dy]);n.seg=0;}};im.src='assets/npcs/v2/'+n.id+'.png';}
function patrolNpc(n,dt){if(!n.path||n.alert>0||n.fainted>0||n.dead)return;
 if(Math.hypot(hero.x-n.x,hero.y-n.y)<NPC_V2_CFG.stopNear){const dx=hero.x-n.x,dy=hero.y-n.y;n.dir=Math.abs(dx)>Math.abs(dy)?(dx<0?'left':'right'):(dy>0?'down':'up');return;}
 const q=n.path[(n.seg+1)%n.path.length],dx=q[0]-n.x,dy=q[1]-n.y,d=Math.hypot(dx,dy),s=NPC_V2_CFG.speed*dt;
 if(d<=s+.5){n.seg=(n.seg+1)%n.path.length;return;}moveCol(n,dx/d*s,dy/d*s,14);}
function drawNpcV2(n){const{m,im}=n.v2,L=1/LSC,C=NPC_V2_CFG,tt=Math.floor(n.t*60)+(n.seed||(n.seed=(Math.random()*60)|0));
 const r=Math.max(0,m.rows.indexOf(n.dir||'down')),fi=n.moving&&!m.static?m.walk[0]+Math.floor(tt/C.walkTicks)%m.walk[1]:m.idle[0]+Math.floor(tt/C.idleTicks)%m.idle[1];
 shadow(n.x,n.y+1,14*L*.6/CS,10,.35);const x=(Math.round(n.x*LSC)-m.ax)*L,y=(Math.round(n.y*LSC)-m.ay)*L;
 const sm=ctx.imageSmoothingEnabled;ctx.imageSmoothingEnabled=false;ctx.drawImage(im,fi*m.cw,r*m.ch,m.cw,m.ch,x,y,m.cw*L,m.ch*L);
 if(n.flash>0){ctx.save();ctx.globalAlpha=.6;ctx.globalCompositeOperation='lighter';ctx.drawImage(im,fi*m.cw,r*m.ch,m.cw,m.ch,x,y,m.cw*L,m.ch*L);ctx.restore();}
 ctx.imageSmoothingEnabled=sm;}
function spawnNpc(id,x,y,o={}){"""
B_OLD = "im.src='assets/npcs/'+id+'.png';npcs.push(n);return n;}"
B_NEW = "im.src='assets/npcs/'+id+'.png';npcs.push(n);npcV2(n);return n;}"
C_OLD = "function drawNpc(n){const im=n.img;if(!im)return;"
C_NEW = "function drawNpc(n){if(n.v2)return drawNpcV2(n);const im=n.img;if(!im)return;"
D_OLD = "n._m=()=>{n.moving=Math.hypot(n.x-px,n.y-py)>.01;if(Math.abs(n.x-px)>.01)n.face=n.x>px?1:-1;};if(n.dead)return;"
D_NEW = ("n._m=()=>{n.moving=Math.hypot(n.x-px,n.y-py)>.01;if(Math.abs(n.x-px)>.01)n.face=n.x>px?1:-1;"
         "if(n.moving){const ddx=n.x-px,ddy=n.y-py;n.dir=Math.abs(ddx)>Math.abs(ddy)?(ddx<0?'left':'right'):(ddy>0?'down':'up');}};if(n.dead)return;patrolNpc(n,dt);")
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    if MARK in s: print(p, 'already patched'); continue
    for o, n in ((A_OLD, A_NEW), (B_OLD, B_NEW), (C_OLD, C_NEW), (D_OLD, D_NEW)):
        assert s.count(o) == 1, (p, o[:60], s.count(o)); s = s.replace(o, n)
    open(p, 'w', encoding='utf-8').write(s); print(p, 'patched')
