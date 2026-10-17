"""Bootstrap generator for the editable map JSON in maps/.
  python3 tools/world_maps.py world     -> maps/world.json   (terrain derived from src/world_map_v4.jpg, nodes from data/towns.json)
  python3 tools/world_maps.py field01   -> maps/field01.json (hand-placed layout below)
  python3 tools/world_maps.py dungeon   -> maps/dungeon01_b1.json, dungeon01_b2.json, boss01.json
  python3 tools/world_maps.py all
After generation the JSON files ARE the source of truth: edit them by hand (see WORLD.md). Re-running overwrites them.
"""
import json, sys, math, random, heapq
import numpy as np
from PIL import Image
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'   # town/ (or the town-demo working copy)
_up=os.path.dirname(os.path.dirname(R))+'/'
REPO=os.environ.get('THOR_REPO') or (_up if os.path.isdir(_up+'art') else '/workspace/thor-like-game/')  # repo root (art/, data/)
M=R+'maps/'
def dump(name,obj):
    # one map row per line so the ASCII grids stay hand-editable
    rows={k:obj.pop(k) for k in ('ground',) if k in obj}
    s=json.dumps(obj,ensure_ascii=False,indent=1)
    if rows:
        g=',\n'.join('  '+json.dumps(r,ensure_ascii=False) for r in rows['ground'])
        s=s[:-2]+',\n "ground": [\n'+g+'\n ]\n}'
    open(M+name+'.json','w').write(s+'\n');print('wrote',name)

# ======================================================================= WORLD MAP
AREAS=[ # id, name, boss, node (x,y in 1024x576 design-map pixels, from src/world_map_v4_numbered.png), bgm
 (1,'시작의 숲','이끼 수정 골렘',(149,349),'area01_forest'),
 (2,'수정 동굴','수정 여왕거미',(107,269),'area02_cave'),
 (3,'모래 사막','모래 대지렁이',(736,229),'area03_desert'),
 (4,'피라미드','황금가면 미라왕',(896,360),'area04_pyramid'),
 (5,'산호 바다','심해 크라켄 뱀',(131,476),'area05_coral_sea'),
 (6,'해안 절벽','산호 거대게',(872,449),'area06_cliff'),
 (7,'화산 성채','화염검 흑기사',(640,59),'area07_volcano'),
 (8,'설산 뇌전 탑','뇌전 와이번',(253,96),'area08_thunder_tower'),
 (9,'어둠 신전','공허의 대사제',(327,200),'area09_dark_temple'),
 (10,'마룡의 둥지','머리 셋 달린 그림자 마룡',(509,40),'area10_dragon_nest')]
TOWNBGM={'A':'town_a_fountain','B':'town_b_watermill','H':'town_h_mine','G':'town_g_bazaar','F':'town_f_harbor','E':'town_e_forge','C':'town_c_snow_lodge','D':'town_d_capital'}
def world():
    T=8; W,H=128,72
    im=Image.open(R+'assets_src/world/world_map_v4.jpg').convert('RGB').resize((1024,576),Image.BOX)
    a=np.array(im).astype(int)
    grid=[['.']*W for _ in range(H)]
    # land/water from the design map (water is clearly blue); biomes from seeds near the design-map landmarks + noise
    SEEDS=[((149,349),'F'),((95,330),'F'),((210,330),'F'),((107,269),'h'),((736,229),'_'),((896,360),'_'),((760,195),'_'),((820,280),'_'),
           ((872,449),'h'),((800,420),'h'),((640,59),'a'),((675,120),'a'),((509,40),'a'),((253,96),'S'),((200,175),'S'),((120,150),'S'),
           ((327,200),'x'),((505,315),'.'),((270,285),'.'),((610,430),'.'),((455,125),'.'),((450,250),'.'),((350,300),'.'),((560,300),'.'),
           ((600,380),'.'),((400,380),'F'),((540,230),'F'),((380,440),'h'),((470,470),'.')]
    rng=np.random.RandomState(5)
    nz=np.array(Image.fromarray((rng.rand(9,16)*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)).astype(float)/255
    nz2=np.array(Image.fromarray((rng.rand(18,32)*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)).astype(float)/255
    nz3=np.array(Image.fromarray((rng.rand(24,42)*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)).astype(float)/255
    for ty in range(H):
        for tx in range(W):
            blk=a[ty*T:(ty+1)*T,tx*T:(tx+1)*T].reshape(-1,3)
            r,g,b=blk.mean(0);mx,mn=max(r,g,b),min(r,g,b);s=(mx-mn)/(mx+1)
            water=(b>r+25 and b>g+5)
            if water: c='~'
            else:
                px,py=tx*T+4+(nz[ty,tx]-.5)*70,ty*T+4+(nz2[ty,tx]-.5)*70
                c=min(SEEDS,key=lambda sd:(sd[0][0]-px)**2+(sd[0][1]-py)**2)[1]
                if s<0.13 and mx>120: c='^' if c=='S' or mx>165 else 'M'      # grey / snowy peaks on the design map
                elif c in 'Sha' and nz3[ty,tx]>.66: c='^' if c=='S' else 'M'   # ridges
                elif c=='.' and nz2[ty,tx]>.72: c='F'
                elif c=='F' and nz2[ty,tx]<.3: c='.'
            grid[ty][tx]=c
    # majority smoothing (keeps roads)
    g2=[row[:] for row in grid]
    for y in range(1,H-1):
        for x in range(1,W-1):
            if grid[y][x] in '=~':continue
            nb=[grid[y+j][x+i] for j in (-1,0,1) for i in (-1,0,1)]
            best=max(set(nb),key=nb.count)
            if nb.count(best)>=6:g2[y][x]=best
    grid=g2
    towns=json.load(open(REPO+'data/towns.json'))['towns']
    nodes=[]
    for t in towns:
        x,y=json.loads(t['map_xy_1024']) if isinstance(t['map_xy_1024'],str) else t['map_xy_1024']
        nodes.append({'id':'town'+t['id'],'kind':'town','town':t['id'],'name':t['name'],'sub':t.get('subtitle',''),'x':round(x/T,1),'y':round(y/T,1),
            'scene':'town' if t['id']=='A' else None,'locked':t['id']!='A','bgm':TOWNBGM[t['id']],
            'connects':t['connects'] if isinstance(t['connects'],dict) else None})
    for n,name,boss,(x,y),bgm in AREAS:
        nodes.append({'id':'area%d'%n,'kind':'area','area':n,'name':name,'boss':boss,'x':round(x/T,1),'y':round(y/T,1),
            'scene':'field%02d'%n if n==1 else None,'locked':n!=1,'bgm':bgm})
    # carve roads between connected nodes (A* through cheap terrain) so every node is reachable on foot
    cost={'.':1,'=':.6,'F':2,'h':2,'_':1.5,'x':2,'S':1.5,'a':2,'^':9,'M':9,'~':14}
    def astar(a_,b_):
        sx,sy=a_;gx,gy=b_;openl=[(0,sx,sy)];came={(sx,sy):None};gs={(sx,sy):0}
        while openl:
            _,x,y=heapq.heappop(openl)
            if (x,y)==(gx,gy):break
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if not(0<nx<W-1 and 0<ny<H-1):continue
                ng=gs[(x,y)]+cost.get(grid[ny][nx],2)
                if ng<gs.get((nx,ny),1e9):gs[(nx,ny)]=ng;came[(nx,ny)]=(x,y);heapq.heappush(openl,(ng+abs(nx-gx)+abs(ny-gy),nx,ny))
        p=(gx,gy);path=[]
        while p:path.append(p);p=came.get(p)
        return path
    byid={n['id']:n for n in nodes}
    links=set()
    for t in towns:
        c=t['connects'] if isinstance(t['connects'],dict) else eval(t['connects'])
        for o in c.get('towns',[]):links.add(tuple(sorted(('town'+t['id'],'town'+o))))
        for ar in c.get('areas',[]):links.add(tuple(sorted(('town'+t['id'],'area%d'%ar))))
    links.add(('area10','townD'))
    roads=[]
    for a_,b_ in sorted(links):
        A_,B_=byid[a_],byid[b_]
        path=astar((int(A_['x']),int(A_['y'])),(int(B_['x']),int(B_['y'])))
        for (x,y) in path:
            if grid[y][x]=='~':grid[y][x]='b'   # bridge / ford
            elif grid[y][x] in 'M^':grid[y][x]='p'  # mountain pass
            else:grid[y][x]='='
        roads.append([a_,b_])
    for n in nodes:  # clear a little plaza around each node
        for j in (-1,0,1):
            for i in (-1,0,1):
                x,y=int(n['x'])+i,int(n['y'])+j
                if grid[y][x] in 'M^~':grid[y][x]='.'
    dump('world',{'id':'world','type':'world','name':'월드맵','title':{'kicker':'WORLD MAP','name':'왕국 전도','sub':'열 개의 땅과 여덟 마을'},
        'bgm':'worldmap','tile':8,'w':W,'h':H,
        'legend':{'.':'grass','=':'dirt','~':'water_deep','b':'bridge_h','F':'forest','M':'mountain','^':'snowpeak','p':'dirt','h':'hill','_':'desert','x':'grass_cursed','S':'snow','a':'ash'},
        'solid':['~','M','^'],
        'note':'terrain derived from src/world_map_v4.jpg (8px tiles); roads carved between towns.json connections. Edit freely.',
        'spawns':{'default':[byid['townA']['x'],byid['townA']['y']+1.5]},
        'townGate':{'town':'A','x0':560,'x1':800,'y':690,'hintY':640,'note':'town-A coordinates of the south exit; update if the town is rescaled'},
        'nodes':nodes,'roads':roads,'ground':[''.join(r) for r in grid]})


# ======================================================================= FIELD 00  (town outskirts, Ys-style seamless road)
FLEG={'.':'grass',',':'grass_tuft',"'":'grass_flowers','=':'dirt','~':'water','b':'bridge_h',':':'stones','#':'cliff','"':'tallgrass','_':'sand',
      'T':{'ground':'grass','deco':'tree'},'P':{'ground':'grass','deco':'pine'},'Y':{'ground':'grass','deco':'tree','solid':False},
      'R':{'ground':'grass','deco':'boulder'},'r':{'ground':'grass','deco':'rocks'},'u':{'ground':'grass','deco':'bush'},'s':{'ground':'grass','deco':'stump'},
      'm':{'ground':'grass','deco':'mushrooms','solid':False},'f':{'ground':'grass','deco':'fence'},
      'O':{'ground':'grass','deco':'pillar'},'c':{'ground':'grass','deco':'crystal'}}
FSOLID=['~','#','T','P','R','r','u','s','f','O','c']
def road(G,pts,W,H,width=1,keep='#'):
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        n=max(abs(x1-x0),abs(y1-y0))*2 or 1
        for i in range(n+1):
            x=x0+(x1-x0)*i/n;y=y0+(y1-y0)*i/n
            for dy in range(-width,width+1):
                for dx in range(-width,width+1):
                    xx,yy=int(round(x+dx)),int(round(y+dy))
                    if 0<=xx<W and 0<=yy<H:
                        c=G[yy][xx];G[yy][xx]='b' if c in '~b' else ('=' if c!=keep else c)
def field00():
    W,H=56,36;G=[['.']*W for _ in range(H)];rnd=random.Random(5)
    def put(x,y,c):
        if 0<=x<W and 0<=y<H:G[y][x]=c
    def rect(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):put(x,y,c)
    for y in range(H):
        for x in range(W):
            r=rnd.random();G[y][x]=',' if r<.12 else ("'" if r<.17 else '.')
    # creek from a pond (NE) down to the south edge; the main road crosses it on a bridge
    rect(41,4,48,8,'~');rect(42,3,47,9,'~')
    for y in range(9,H):
        cx=45+round(1.5*math.sin(y/4.0))
        for x in range(cx-1,cx+1):put(x,y,'~')
    # roads: town gate (N) -> junction -> east exit to the forest; west branch to the wind hill; south branch to the rockfall
    road(G,[(27,0),(27,9),(31,14),(38,18),(55,19)],W,H)
    road(G,[(27,9),(16,9),(9,7)],W,H,width=0)
    road(G,[(34,16),(34,24),(32,33),(32,35)],W,H,width=0)
    rect(5,4,11,9,'=')                                   # hill top plaza
    for (x,y) in [(5,4),(11,4),(5,9),(11,9)]:put(x,y,'O')  # ruined pillars around the waystone
    # rockfall blocks the south road (area 2 not open yet)
    for (x,y) in [(30,30),(31,30),(32,30),(33,30),(34,30),(31,31),(33,31),(32,29)]:put(x,y,'R' if (x+y)%2 else 'r')
    # tall grass + flowers
    for (x0,y0,x1,y1) in [(36,24,41,28),(14,20,19,23),(48,12,52,15)]:rect(x0,y0,x1,y1,'"')
    def tree(x,y,kind=None):
        if 0<=x<W and 0<=y<H and G[y][x] in ".,'":G[y][x]=kind or rnd.choice('TTTP')
    for x in range(W):
        for y in (0,1,H-2,H-1):
            if not(24<=x<=30 and y<2):tree(x,y)
    for y in range(H):
        for x in (0,1,W-2,W-1):
            if not(17<=y<=21 and x>=W-2):tree(x,y)
    for cx,cy,r in [(18,3,3),(36,4,3),(6,16,4),(10,28,5),(22,30,4),(50,27,4),(40,32,2),(20,15,2),(52,6,2)]:
        for y in range(cy-r,cy+r+1):
            for x in range(cx-r,cx+r+1):
                if (x-cx)**2+(y-cy)**2<=r*r and rnd.random()<.75:tree(x,y)
    for (x,y,c) in [(23,12,'R'),(30,6,'r'),(38,13,'u'),(14,12,'u'),(25,20,'s'),(40,21,'m'),(17,25,'m'),(50,22,'R'),(28,25,'r'),(12,11,'u')]:
        if G[y][x] in ".,'\"":G[y][x]=c
    for x in range(20,26):G[2][x]='f'
    for x in range(29,35):G[2][x]='f'
    obj=[
     {'type':'exit','x':24,'y':0,'w':7,'h':1,'to':'town','spawn':'gate','label':'시작 마을'},
     {'type':'exit','x':55,'y':17,'w':1,'h':5,'to':'field01','spawn':'west','label':'시작의 숲'},
     {'type':'sign','x':25,'y':10,'text':'↑ 시작 마을    ← 바람의 언덕\n→ 시작의 숲 · 고대 숲 신전    ↓ 수정 동굴 (낙석으로 막힘)'},
     {'type':'sign','x':35,'y':28,'text':'낙석으로 길이 막혀 있다. 수정 동굴(2지역)은 아직 갈 수 없다.'},
     {'type':'waystone','id':'ws_windhill','x':8,'y':6,'name':'바람의 언덕 비석'},
     {'type':'chest','id':'f00_chest_hill','x':6,'y':8,'loot':[['potion',1],['m_hardwood',1]]},
     {'type':'npc','id':'npc_bori','x':30,'y':8,'sprite':'npc_bard','name':'나그네 보리','quests':['q_forest_chiefs','q_temple_golem'],
      'idle':'바람이 좋은 날이군. 숲 쪽 길은 이 길을 따라 동쪽이야.'},
     {'type':'landmark','id':'lm_bridge00','x':45,'y':19,'name':'개울 다리'},
    ]
    for k,x,y in [('rabbit',20,6),('rabbit',38,22),('mushroom',15,18),('slime',42,15),('slime',22,26),('squirrel',49,24),('mushroom',8,22),('rabbit',51,11)]:
        obj.append({'type':'spawn','mob':k,'x':x,'y':y,'respawn':30})
    dump('field00',{'id':'field00','type':'field','area':1,'region':'area1','mapPos':[0,0],'name':'마을 외곽 — 바람길',
      'title':{'kicker':'1지역 · AREA 1','name':'바람길','sub':'시작 마을 외곽'},
      'bgm':'area01_forest','battleBgm':'battle_champion','tileset':'field','tile':16,'w':W,'h':H,'legend':FLEG,'solid':FSOLID,
      'spawns':{'default':[27.5,2.5,'down'],'town':[27.5,2.5,'down'],'east':[53.5,19.5,'left']},
      'objects':obj,'ground':[''.join(r) for r in G]})

# ======================================================================= FIELD 01
def field01():
    W,H=64,40;G=[['.']*W for _ in range(H)]
    rnd=random.Random(11)
    def put(x,y,c):
        if 0<=x<W and 0<=y<H:G[y][x]=c
    def rect(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):put(x,y,c)
    # grass variety
    for y in range(H):
        for x in range(W):
            r=rnd.random();G[y][x]=',' if r<.12 else ("'" if r<.16 else '.')
    # stream (meanders N->S), widens into a pool with an island
    for y in range(H):
        cx=31+round(2*math.sin(y/5.0));wd=3
        if 27<=y<=34:wd=8;cx=32
        for x in range(cx-wd//2,cx-wd//2+wd):put(x,y,'~')
    rect(31,30,33,32,'_')                      # island (secret chest)
    for x in (28,29,30):put(x,31,':')          # stepping stones from the west bank
    put(27,31,'.');put(26,31,'.')
    # north cliff band with the dungeon gate cut
    rect(36,2,61,5,'#');rect(45,2,47,4,'#')
    # path: west gate -> bend -> bridge -> east -> north to the gate
    pts=[(0,19),(10,19),(14,17),(20,14),(28,14),(36,14),(44,14),(46,11),(46,6)]
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        n=max(abs(x1-x0),abs(y1-y0))*2
        for i in range(n+1):
            x=x0+(x1-x0)*i/n;y=y0+(y1-y0)*i/n
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    if G[int(round(y+dy))][int(round(x+dx))] if 0<=int(round(y+dy))<H and 0<=int(round(x+dx))<W else False:
                        c=G[int(round(y+dy))][int(round(x+dx))]
                        put(int(round(x+dx)),int(round(y+dy)),'b' if c=='~' or c=='b' else ('#' if c=='#' and int(round(y+dy))<5 else '='))
    rect(45,4,47,5,'=')   # threshold + the gate cell itself (exit zone at y=4)
    # south branch to the boar clearing
    for y in range(15,27):put(40,y,'=');put(41,y,'=')
    rect(44,23,54,30,'=');
    # tall grass patches (one hides an item)
    for (x0,y0,x1,y1) in [(4,24,9,26),(16,30,21,33),(54,12,58,16),(22,4,26,7)]:rect(x0,y0,x1,y1,'"')
    # rest spot (no mobs) with a bench sign by the bridge
    # trees: border + clumps
    def tree(x,y,kind=None):
        if 0<=x<W and 0<=y<H and G[y][x] in ".,'":G[y][x]=kind or rnd.choice('TTTP')
    for x in range(W):
        for y in (0,1,H-2,H-1):tree(x,y)
    for y in range(H):
        for x in (0,1,W-2,W-1):
            if not(17<=y<=21 and x<2):tree(x,y)
    for cx,cy,r in [(8,8,4),(18,24,3),(24,34,4),(52,34,5),(58,22,3),(26,9,3),(12,35,3),(38,24,2),(55,8,2)]:
        for y in range(cy-r,cy+r+1):
            for x in range(cx-r,cx+r+1):
                if (x-cx)**2+(y-cy)**2<=r*r and rnd.random()<.75:tree(x,y)
    # secret glade (SW): ring of trees, one passable tree 'Y' (looks like a tree, walk through it)
    for y in range(28,36):
        for x in range(4,14):
            G[y][x]=('T' if (x in(4,13) or y in(28,35)) else '.')
    G[28][9]='Y'
    # deco
    for (x,y,c) in [(12,13,'R'),(23,18,'r'),(35,18,'R'),(38,10,'r'),(50,18,'R'),(57,28,'r'),(6,15,'u'),(16,12,'u'),(44,30,'s'),(20,20,'m'),(34,22,'m'),(52,20,'u'),(9,22,'s'),(27,20,'R'),(48,27,'R'),(51,25,'r')]:
        if G[y][x] in ".,'\"":G[y][x]=c
    for x in range(3,9):G[16][x]='f'   # fence near the start
    G[16][2]='f'
    obj=[
     {'type':'exit','x':0,'y':17,'w':1,'h':5,'to':'field00','spawn':'east','label':'바람길 (시작 마을)'},
     {'type':'waystone','id':'ws_temple','x':42,'y':9,'name':'신전 앞 비석'},
     {'type':'landmark','id':'lm_bridge01','x':32,'y':14,'name':'쉼터 다리'},
     {'type':'exit','x':45,'y':4,'w':3,'h':1,'to':'dungeon01_b1','spawn':'default','label':'고대 숲 신전'},
     {'type':'door_deco','x':46,'y':4.6,'sprite':'doorway_big'},
     {'type':'sign','x':4,'y':18,'text':'← 바람길 · 시작 마을   /   시작의 숲 · 고대 숲 신전 →\n(Shift: 구르기 — 구르는 동안은 무적)'},
     {'type':'sign','x':27,'y':12,'text':'쉼터 다리. 개울 아래쪽 웅덩이 가운데 작은 섬이 보인다…'},
     {'type':'sign','x':43,'y':8,'text':'고대 숲 신전.\n「숲의 두 우두머리가 쓰러질 때, 골렘의 방이 열리리라.」'},
     {'type':'sign','x':42,'y':22,'text':'경고: 이 앞 공터에 거대 왕멧돼지 「돌엄니」 출몰!'},
     {'type':'chest','id':'f01_chest_glade','x':9,'y':31,'loot':[['potion',2],['m_hardwood',2]],'note':'secret: walk through the odd tree (Y) at the top of the glade'},
     {'type':'chest','id':'f01_chest_island','x':32,'y':31,'loot':[['heart_piece',1]],'note':'secret: stepping stones (:) from the west bank'},
     {'type':'chest','id':'f01_chest_cliff','x':59,'y':7,'loot':[['potion',1],['m_a1_shared',3]]},
     {'type':'hidden','id':'f01_grass_item','x':56,'y':14,'loot':[['spirit_drop',1]],'note':'interact in the tall grass where it glints'},
     {'type':'heal','x':29,'y':16,'note':'bench/rest spot: interact to restore HP'},
     {'type':'champion','id':'champ_boar','mob':'champ_boar','x':49,'y':26},
     {'type':'champion','id':'champ_wasp','mob':'champ_wasp','x':15,'y':7},
    ]
    sp=[('rabbit',8,21),('mushroom',12,23),('rabbit',17,18),('mushroom',6,12),('wasp',22,11),('squirrel',24,16),('slime',20,27),('slime',35,9),('wasp',37,17),
        ('squirrel',38,12),('boar',52,16),('scarecrow',56,18),('sprout',44,19),('boar',57,31),('sprout',36,27),('scarecrow',30,37)]
    for k,x,y in sp:obj.append({'type':'spawn','mob':k,'x':x,'y':y,'respawn':25})
    dump('field01',{'id':'field01','type':'field','area':1,'region':'area1','mapPos':[56,0],'name':'시작의 숲 — 던전 가는 길','title':{'kicker':'1지역 · AREA 1','name':'시작의 숲','sub':'던전 가는 길'},
      'bgm':'area01_forest','battleBgm':'battle_champion','tileset':'field','tile':16,'w':W,'h':H,
      'legend':{'.':'grass',',':'grass_tuft',"'":'grass_flowers','=':'dirt','~':'water','b':'bridge_h',':':'stones','#':'cliff','"':'tallgrass','_':'sand',
                'T':{'ground':'grass','deco':'tree'},'P':{'ground':'grass','deco':'pine'},'Y':{'ground':'grass','deco':'tree','solid':False},
                'R':{'ground':'grass','deco':'boulder'},'r':{'ground':'grass','deco':'rocks'},'u':{'ground':'grass','deco':'bush'},'s':{'ground':'grass','deco':'stump'},
                'm':{'ground':'grass','deco':'mushrooms','solid':False},'f':{'ground':'grass','deco':'fence'}},
      'solid':['~','#','T','P','R','r','u','s','f'],
      'spawns':{'default':[2.5,19.5,'right'],'west':[2.5,19.5,'right'],'world':[2.5,19.5,'right'],'dungeon':[46.5,7,'down']},
      'objects':obj,'ground':[''.join(r) for r in G]})

# ======================================================================= DUNGEON
B1="""
##########################################
####t##t######################t###t######
###.......####################.......####
###...U...####################...V...####
###.......####################.......####
###.C.....####################..c.c..####
###.......#######################D#######
#####.###########################.#######
#####.###########t###t###########.#######
#####.########..........#########..######
#####.........,,....,,...........%.######
#####.###.....^^^^^^^^...###.....,.######
#####.###.....,.......,..###.....p.######
#####.###.....^^^^^^^^...###.......######
#####.###.....,,....,,...###.......######
#####.###########..##########......######
#####.###########..###############.######
###t..t##########..###########t###.######
###.....#########.............o.o..######
###..C..###########.........o.....o######
###.....###########...p..........K.######
###...c.#########################..######
##########################################
"""
B2="""
##############################################
#####t###t####################################
####.......#####t#######t#####t###t###########
####...U...####.................c....#########
####.......####.....p......p.......S.#########
####.......####......................#########
######.########.....p......p.........#########
######.##########.############################
######.##########.############################
######...........,......^...^...^....#########
######.##########.###################.########
######.##########.#################t#.#t######
####tt.###t######.#################.......####
###...S...#######.#################...B...####
###.......#######G#################.......####
###..C....#######.#################.......####
##########.......,.......o.o.......######.####
##########.......,.................######.####
##########t######.####t############t###...####
##########...............................#####
##############################################
"""
BOSS="""
##########################
####t####t######t####t####
###....................###
###..p......c.......p..###
###....................###
###....................###
###.......p....p.......###
###....................###
###....................###
###..p..............p..###
###....................###
###.........U..........###
##########################
"""
DLEG={'#':'wall','.':'floor',',':'floor_moss','%':'floor_crack','^':{'ground':'floor','obj':'spikes'},'o':{'ground':'floor','obj':'pit'},
      'U':{'ground':'floor','obj':'stairs_up'},'V':{'ground':'floor','obj':'stairs_down'},'D':{'ground':'floor','obj':'door_locked'},'G':{'ground':'floor','obj':'gate'},
      'B':{'ground':'floor','obj':'boss_door'},'K':{'ground':'floor','obj':'key'},'C':{'ground':'floor','obj':'chest'},'S':{'ground':'floor','obj':'lever'},
      't':{'ground':'wall','obj':'torch'},'c':{'ground':'floor_moss','deco':'crystal','solid':True},'p':{'ground':'floor','deco':'pillar','solid':True}}
def grid(s):
    rows=[r for r in s.strip('\n').split('\n')];W=max(map(len,rows));return [r.ljust(W,'#') for r in rows]
def dungeon():
    g=grid(B1)
    dump('dungeon01_b1',{'id':'dungeon01_b1','region':'temple01','mapPos':[0, 0],'type':'dungeon','area':1,'floor':1,'name':'고대 숲 신전 B1','title':{'kicker':'1지역 · 던전','name':'고대 숲 신전','sub':'지하 1층'},
      'bgm':'area01_forest','dark':0.55,'tileset':'dungeon','tile':16,'w':len(g[0]),'h':len(g),'legend':DLEG,'solid':['#','t'],
      'spawns':{'default':[6.5,4.5,'down'],'up':[33.5,4.5,'down']},
      'links':{'stairs_up':{'to':'field01','spawn':'dungeon'},'stairs_down':{'to':'dungeon01_b2','spawn':'default'}},
      'chests':{'3,5':{'id':'d1_c1','loot':[['potion',1]]},'5,19':{'id':'d1_c2','loot':[['m_spore',2],['bomb',1]]}},
      'keys':{'33,20':'d1_key'},
      'objects':[{'type':'spawn','mob':'slime','x':12,'y':10,'respawn':0},{'type':'spawn','mob':'mushroom','x':20,'y':12,'respawn':0},
                 {'type':'spawn','mob':'sprout','x':31,'y':12,'respawn':0},{'type':'spawn','mob':'wasp','x':30,'y':19,'respawn':0},
                 {'type':'spawn','mob':'scarecrow','x':22,'y':19,'respawn':0},{'type':'spawn','mob':'squirrel','x':5,'y':10,'respawn':0},
                 {'type':'sign','x':9,'y':3,'text':'B1 — 잠긴 문 너머로 내려가는 계단이 있다.\n열쇠는 남동쪽 방 어딘가에… (구멍과 가시 함정 주의)'}],
      'ground':g})
    g=grid(B2)
    dump('dungeon01_b2',{'id':'dungeon01_b2','region':'temple01','mapPos':[46, 0],'type':'dungeon','area':1,'floor':2,'name':'고대 숲 신전 B2','title':{'kicker':'1지역 · 던전','name':'고대 숲 신전','sub':'지하 2층'},
      'bgm':'area01_forest','dark':0.62,'tileset':'dungeon','tile':16,'w':len(g[0]),'h':len(g),'legend':DLEG,'solid':['#','t'],
      'spawns':{'default':[7.5,4.5,'down'],'boss':[38.5,15.5,'down']},
      'links':{'stairs_up':{'to':'dungeon01_b1','spawn':'up'},'boss_door':{'to':'boss01','spawn':'default','needFlags':['champ_boar','champ_wasp'],
               'lockedText':'봉인된 문. 「숲의 두 우두머리(돌엄니 · 여왕 말벌)를 쓰러뜨려라.」'}},
      'gateNeeds':'levers',
      'chests':{'5,15':{'id':'d2_c1','loot':[['potion',2]]}},
      'objects':[{'type':'spawn','mob':'boar','x':25,'y':4,'respawn':0},{'type':'spawn','mob':'slime','x':18,'y':5,'respawn':0},{'type':'spawn','mob':'scarecrow','x':30,'y':5,'respawn':0},
                 {'type':'spawn','mob':'sprout','x':22,'y':17,'respawn':0},{'type':'spawn','mob':'rabbit','x':12,'y':16,'respawn':0},{'type':'spawn','mob':'wasp','x':38,'y':14,'respawn':0},
                 {'type':'spawn','mob':'mushroom','x':30,'y':19,'respawn':0},
                 {'type':'sign','x':9,'y':4,'text':'B2 — 철창(G)은 레버 두 개(S)를 모두 당기면 열린다.\n동쪽 끝에 골렘의 방.'}],
      'ground':g})
    g=grid(BOSS)
    dump('boss01',{'id':'boss01','region':'temple01','mapPos':[96, 4],'type':'boss','area':1,'name':'이끼 수정 골렘의 방','title':{'kicker':'BOSS','name':'이끼 수정 골렘','sub':'숲의 심장을 지키는 자'},
      'bgm':'battle_boss','bgm2':'battle_boss_phase2','dark':0.35,'tileset':'dungeon','tile':16,'w':len(g[0]),'h':len(g),'legend':DLEG,'solid':['#','t'],
      'spawns':{'default':[12.5,10.2,'up']},
      'links':{'stairs_up':{'to':'dungeon01_b2','spawn':'boss'}},
      'boss':{'id':'golem01','kind':'golem','name':'이끼 수정 골렘','x':12.5,'y':4.5,'flag':'boss01',
              'absorb':'대지의 수정 (quake)','reward':[['m_a1_shared',5],['heart_piece',1]],'exit':{'to':'field01','spawn':'dungeon'}},
      'objects':[],'ground':g})

if __name__=='__main__':
    w=sys.argv[1] if len(sys.argv)>1 else 'all'
    if w in('world','all'):world()
    if w in('field00','all'):field00()
    if w in('field01','all'):field01()
    if w in('dungeon','all'):dungeon()
