# Region fields for areas 2-9 (owner 10-22 "만들어 놓은 몬스터 전부 배치해서 인게임"): one 52x32 field per world-map area node,
# themed ground + obstacle clumps, west exit back to the world map, and every room-3 mob of that area spawned (respawn 30s).
# Writes maps/field02..field09.json and updates maps/world.json (unlocks area2-9) and maps/index.json. Re-run safe (seeded).
# usage (from test128/): python3 tools/gen_region_fields.py
import json,random
W,H=52,32
TH={2:('수정 동굴','soil',['stones','dirt_pebble'],'cliff_rock',['crystal','crystal','boulder','rocks'],None,'area02_cave'),
    3:('모래 사막','desert',['sand','sand2'],'cliff',['rocks','boulder','rubble'],None,'area03_desert'),
    4:('피라미드','sand',['paving','paving2'],'cliff',['pillar','rubble','tablet'],None,'area04_pyramid'),
    5:('산호 바다','sand',['sand2','water_shallow'],'cliff_rock',['rocks','boulder'],'water_deep','area05_coral_sea'),
    6:('해안 절벽','grass',['soil','stones'],'cliff',['rocks','boulder','bush'],'water','area06_cliff'),
    7:('화산 성채','ash',['soil','mud'],'cliff_rock',['boulder','rubble','rocks'],None,'area07_volcano'),
    8:('설산 뇌전 탑','snow',['stones','snow'],'cliff',['pine','pine','boulder'],None,'area08_thunder_tower'),
    9:('어둠 신전','grass_cursed',['paving','paving2'],'cliff',['pillar','rubble','tablet'],None,'area09_dark_temple')}
MOBS=json.load(open('assets/mobs47/mobs47.json'))
idx=json.load(open('maps/index.json'));wj=json.load(open('maps/world.json'))
for a,(nm,base,var,cliff,decos,pool,bgm) in TH.items():
    R=random.Random(a*7919);fid=f'field0{a}'
    g=[['.']*W for y in range(H)]
    for _ in range(10):                                     # soft variant patches instead of per-tile noise
        cx,cy,c=R.randint(3,W-4),R.randint(3,H-4),R.choice(',,:')
        for y in range(H):
            for x in range(W):
                if ((x-cx)/R.uniform(2.5,4))**2+((y-cy)/R.uniform(1.5,2.5))**2<1:g[y][x]=c
    leg={'.':base,',':var[0],':':var[1],'#':cliff}
    solid=['#']
    for x in range(W):
        for y in range(H):
            if x<2 or y<2 or x>=W-2 or y>=H-2:g[y][x]='#'
    for y in range(13,19):g[y][0]=g[y][1]='.'          # west opening
    if pool:
        leg['~']=pool;solid.append('~')
        cx,cy=R.randint(30,42),R.randint(8,22)
        for y in range(H):
            for x in range(W):
                if ((x-cx)/6)**2+((y-cy)/4)**2<1 and 2<x<W-3 and 2<y<H-3:g[y][x]='~'
    for i,d in enumerate(dict.fromkeys(decos)):
        c='ABCDEFG'[i];leg[c]={'ground':base,'deco':d};solid.append(c)
    keep=lambda x,y:(y in range(14,18) and x<12) or abs(x-W//2)<3 and abs(y-H//2)<3
    for _ in range(14):                                     # obstacle clumps
        cx,cy=R.randint(5,W-6),R.randint(4,H-5);c='ABCDEFG'[decos.index(R.choice(decos))]
        for _ in range(R.randint(2,5)):
            x,y=cx+R.randint(-2,2),cy+R.randint(-1,1)
            if 2<=x<W-2 and 2<=y<H-2 and not keep(x,y) and g[y][x]!='~':g[y][x]=c
    ids=[k for k in MOBS if k.startswith(f'a{a}_')];per=max(2,round(12/len(ids)));objs=[]
    objs.append({'type':'exit','x':0,'y':13,'w':1,'h':6,'to':'world','spawn':f'area{a}','label':'월드맵'})
    objs.append({'type':'sign','x':4,'y':12,'text':f'{a}지역 · {nm}\n← 월드맵'})
    n=0
    for k in ids:
        for j in range(per):
            for _ in range(200):
                x,y=R.randint(10,W-4),R.randint(4,H-5)
                if g[y][x] in '.,:' and all(abs(o['x']-x)+abs(o['y']-y)>5 for o in objs if o['type']=='spawn'):break
            objs.append({'type':'spawn','mob':k,'x':x,'y':y,'respawn':30});n+=1
    m={'id':fid,'type':'field','area':a,'region':f'area{a}','mapPos':[0,0],'name':f'{nm} — 들판','title':{'kicker':f'{a}지역 · AREA {a}','name':nm,'sub':'들판'},
       'bgm':bgm,'battleBgm':'battle_champion','tileset':'field','tile':16,'w':W,'h':H,'legend':leg,'solid':solid,
       'spawns':{'default':[3.5,16,'right'],'world':[3.5,16,'right']},'objects':objs,'ground':[''.join(r) for r in g]}
    json.dump(m,open(f'maps/{fid}.json','w'),ensure_ascii=False,indent=1)
    for nd in wj['nodes']:
        if nd['id']==f'area{a}':nd['scene']=fid;nd['locked']=False
    if fid not in idx['maps']:idx['maps'].append(fid)
    idx['regions'][f'area{a}']={'name':f'{a}지역 · {nm}','worldNode':f'area{a}','maps':[fid]}
    print(fid,len(ids),'types',n,'spawns')
json.dump(wj,open('maps/world.json','w'),ensure_ascii=False,indent=1)
json.dump(idx,open('maps/index.json','w'),ensure_ascii=False,indent=1)
