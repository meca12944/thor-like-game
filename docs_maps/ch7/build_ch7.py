# 7장 지도 데이터 만들기 (모션연구방 10-24) — python3 docs_maps/ch7/build_ch7.py → ch7_map.json
import json,os
D=os.path.dirname(os.path.abspath(__file__))
Z=[dict(id='rampart',name='왕도 상층 성벽길',kind='field',x=10,y=290,w=230,h=160,note='6장 시계탑에서 올라오는 길. 잿빛 모래 바람, 무너진 성벽 위'),
   dict(id='forecourt',name='황금 문 전정',kind='dungeon',x=250,y=290,w=170,h=160,note='왕가의 열쇠로 연 황금 문 안쪽. 석회로 굳은 대리석 앞뜰'),
   dict(id='sandfall',name='모래 폭포 대계단',kind='dungeon',x=250,y=120,w=170,h=160,note='잿빛 모래가 폭포처럼 쏟아지는 거대한 계단, 층계참마다 싸움'),
   dict(id='gallery',name='대회랑',kind='dungeon',x=20,y=20,w=320,h=90,note='옥좌로 가는 긴 회랑, 바랜 붉은 카펫, 끝에 근위대장 석상'),
   dict(id='throne',name='옥좌의 방',kind='boss',x=350,y=10,w=150,h=100,note='루드비히가 석회로 굳은 채 앉아 있는 방'),
   dict(id='altar',name='옥좌 뒤 제단',kind='hidden',x=430,y=120,w=80,h=70,note='부서진 옥좌 뒤 숨겨진 제단. 8장 공허의 틈새로 가는 문'),
   dict(id='sidegarden',name='석화된 왕실 정원',kind='field',x=20,y=120,w=220,h=160,note='대계단 테라스에서 대회랑 서쪽 계단까지 가로지르는 정원. 모래에 묻힌 분수·석상')]
A=[dict(kind='ash',poly=[[290,130],[380,130],[370,270],[300,270]]),          # 모래 폭포
   dict(kind='cliff',poly=[[10,290],[240,290],[240,298],[10,298]]),
   dict(kind='ruin',poly=[[40,330],[90,320],[100,360],[50,370]]),dict(kind='ruin',poly=[[150,390],[200,380],[210,420],[160,430]]),
   dict(kind='ash',poly=[[60,160],[140,150],[150,220],[70,240]]),dict(kind='water',poly=[[160,180],[200,175],[205,215],[165,220]]),
   dict(kind='building',poly=[[260,300],[300,300],[300,330],[260,330]]),dict(kind='building',poly=[[370,300],[410,300],[410,330],[370,330]]),
   dict(kind='wall',poly=[[20,20],[340,20],[340,26],[20,26]]),dict(kind='wall',poly=[[20,104],[340,104],[340,110],[20,110]]),
   dict(kind='void',poly=[[455,135],[490,135],[495,175],[450,175]])]
P=[dict(kind='road',w=4,pts=[[20,430],[80,400],[140,410],[200,370],[245,370]]),
   dict(kind='corridor',w=5,pts=[[250,370],[335,370],[335,285]]),
   dict(kind='corridor',w=4,pts=[[335,275],[335,230],[290,200],[250,200]]),   # 대계단을 올라 테라스 문으로
   dict(kind='corridor',w=6,pts=[[40,65],[340,65]]),                          # 대회랑 서쪽 끝 → 동쪽 옥좌의 문
   dict(kind='corridor',w=3,pts=[[335,120],[335,105]]),                       # 지름길1 승강기 통로
   dict(kind='corridor',w=4,pts=[[340,65],[360,60]]),
   dict(kind='corridor',w=3,pts=[[470,110],[470,125]]),
   dict(kind='road',w=4,pts=[[245,200],[200,200],[150,170],[90,150],[40,125]])]   # 정원을 가로질러 대회랑 서쪽 계단으로
L=[dict(**{'from':'ch6','to':'rampart'},kind='stairs',at=[14,440],label='6장 시계탑 → 성벽길'),
   dict(**{'from':'rampart','to':'forecourt'},kind='gate',at=[245,370],label='황금 문 (왕가의 열쇠)'),
   dict(**{'from':'forecourt','to':'sandfall'},kind='stairs',at=[335,285],label='대계단 아래'),
   dict(**{'from':'sidegarden','to':'gallery'},kind='stairs',at=[40,115],label='대회랑 서쪽 계단'),
   dict(**{'from':'sandfall','to':'sidegarden'},kind='door',at=[248,200],label='테라스 문'),
   dict(**{'from':'gallery','to':'throne'},kind='door',at=[345,65],label='옥좌의 문 (보스)'),
   dict(**{'from':'throne','to':'altar'},kind='secret',at=[470,112],label='부서진 옥좌 뒤'),
   dict(**{'from':'altar','to':'ch8'},kind='oneway',at=[472,185],label='8장 공허의 틈새로'),
   dict(**{'from':'gallery','to':'sandfall'},kind='shortcut',at=[335,112],label='지름길1 근위대 승강기 → 대계단·전정 (대회랑에서 열기)'),
   dict(**{'from':'sidegarden','to':'rampart'},kind='shortcut',at=[120,285],label='지름길2 무너진 성벽 사다리 (정원에서 내리기)'),
   dict(**{'from':'gallery','to':'ch5'},kind='gate',at=[180,22],label='북문 → 5장 대성당 (핏방울 3/3을 수장고 석관에)'),
   dict(**{'from':'forecourt','to':'ch3'},kind='gate',at=[418,380],label='서문 → 3장 대서고'),
   dict(**{'from':'rampart','to':'ch4'},kind='gate',at=[12,330],label='동문 → 4장 귀족가')]
M=[]
def mk(t,name,zone,x,y,ref='',note=''):M.append(dict(type=t,name=name,zone=zone,x=x,y=y,ref=ref,note=note))
mk('start','7장 시작 (6장에서 올라옴)','rampart',22,432,'정본 6장: 클로비스 처치 → 왕가의 열쇠')
mk('save','모닥불: 성벽길 입구','rampart',40,425,'팀 제안','구역 쉼터')
mk('save','모닥불: 황금 문 앞','rampart',225,360,'팀 제안','문 열기 전 쉼터')
mk('quest','황금 문 (왕가의 열쇠로 염)','rampart',238,370,'정본 7장 「왕가의 열쇠로 거대한 황금 문을 열고 진입」')
# 성벽길 몹 무리 (230x160 → 15무리)
import itertools
pts=[(30,310),(80,310),(130,310),(180,310),(225,315),(30,360),(80,355),(130,350),(175,345),(60,400),(110,395),(170,400),(220,410),(100,440),(160,440)]
for i,(x,y) in enumerate(pts):mk('mob','몹 무리 보통 3~4' if i%3 else '몹 무리 큰 5~6','rampart',x,y,'팀 제안 (마물은 기획 뒤 정함)')
mk('save','모닥불: 전정 분수','forecourt',300,420,'팀 제안')
for i,(x,y) in enumerate([(270,350),(320,345),(390,350),(270,410),(380,410),(330,320),(400,430)]):mk('mob','몹 무리 보통 3~4','forecourt',x,y,'팀 제안 (마물은 기획 뒤 정함)')
mk('save','모닥불: 대계단 층계참','sandfall',395,200,'팀 제안')
for i,(x,y) in enumerate([(270,260),(390,255),(270,200),(395,150),(270,140),(340,230)]):mk('mob','몹 무리 작은 2~3' if i%2 else '몹 무리 보통 3~4','sandfall',x,y,'팀 제안 (마물은 기획 뒤 정함)')
mk('trap','모래 폭포 (밀려 떨어짐)','sandfall',335,200,'정본 7장 「잿빛 모래가 폭포처럼 흐르는 계단」','쏟아지는 모래에 맞으면 아래 층계참으로 밀림')
# 정원 (220x160 → 14무리)
for i,(x,y) in enumerate([(35,135),(85,135),(140,135),(195,140),(230,150),(35,185),(100,250),(150,240),(205,235),(35,250),(60,210),(200,180),(230,260),(120,270)]):mk('mob','몹 무리 보통 3~4' if i%2 else '몹 무리 작은 2~3','sidegarden',x,y,'팀 제안 (마물은 기획 뒤 정함)')
mk('save','모닥불: 정원 분수','sidegarden',180,200,'팀 제안')
mk('shortcut','사다리 (정원 쪽에서 내림)','sidegarden',120,275,'팀 제안','지름길2: 성벽길 쉼터와 바로 연결')
# 대회랑
for i,(x,y) in enumerate([(60,50),(110,85),(160,45),(210,85),(250,50)]):mk('mob','몹 무리 보통 3~4','gallery',x,y,'팀 제안 (마물은 기획 뒤 정함)')
mk('elite','근위대장 석상','gallery',300,65,'정본 7장 「대회랑의 마지막 근위대장 석상(정예 몹)」','핏방울 3/3·시간이 굳은 모래·붉은 인광석 드랍')
mk('item','시간이 굳은 핏방울 (3/3)','gallery',305,75,'시간이 굳은 핏방울 (3/3)','근위대장 석상 드랍 → 5장 수장고 석관으로')
mk('item','시간이 굳은 모래','gallery',310,58,'시간이 굳은 모래','근위대장 석상 드랍')
mk('item','붉은 인광석','gallery',295,55,'붉은 인광석','근위대장 석상 드랍')
mk('shortcut','근위대 승강기 레버','gallery',330,95,'팀 제안','지름길1: 대회랑 끝 ↔ 대계단 층계참 (전정 쉼터에서 바로 옥좌 앞으로)')
mk('save','모닥불: 옥좌의 문 앞','gallery',332,40,'팀 제안 (보스 문 앞 필수)')
mk('boss','루드비히 「멈춰버린 군주」','throne',425,55,'정본 3장·7-1·7-2','1페이즈 석화된 검왕 / 2페이즈 왕도 권능 개방 (맵 전체 검격·구체 공격)')
mk('item','박제된 군주의 대검','throne',410,85,'박제된 군주의 대검','보스 처치 보상')
mk('item','박제된 군주의 망토','throne',440,85,'박제된 군주의 망토','보스 처치 보상')
mk('landmark','부서진 옥좌','throne',470,100,'정본 7장','쓰러진 뒤 옥좌 뒤로 길이 열림')
mk('item','사멸의 핵철 반지','altar',460,150,'사멸의 핵철 반지','숨겨진 제단. 주인공 정체(살아있는 코어의 그릇) 판명')
mk('npc','루드비히의 왕비 (비밀 인물)','altar',445,170,'정본 0절 「비밀 인물(7~8장) = 루드비히의 왕비」','자리는 팀 제안 — 등장 방식은 스토리 담당이 정할 것')
mk('save','모닥불: 제단 (8장 전 마지막)','altar',495,180,'팀 제안')
mk('landmark','제단의 문 (8장)','altar',472,182,'정본 8장 「옥좌 뒤편의 제단을 통해」')
G=[dict(kind='bg',name='왕성 성벽길 바닥',size='타일 16px 세트',desc='잿빛 모래가 쌓인 성벽 돌길, 무너진 흉벽'),
   dict(kind='bg',name='황금 문',size='12x8 타일',desc='거대한 황금 양문, 왕가 문장 열쇠구멍, 석회가 흘러내림'),
   dict(kind='bg',name='전정 바닥·석화 시종',size='타일 세트 + 소품 2x3',desc='대리석 앞뜰, 석회가 흘러내린 기둥'),
   dict(kind='bg',name='모래 폭포 대계단',size='타일 세트 + 폭포 애니 4장',desc='넓은 계단 위로 잿빛 모래가 폭포처럼 쏟아짐'),
   dict(kind='bg',name='석화된 왕실 정원',size='타일 세트',desc='모래에 묻힌 분수, 굳은 나무, 깨진 석상'),
   dict(kind='bg',name='대회랑',size='타일 세트 + 기둥 소품',desc='붉은 카펫이 바랜 긴 회랑, 높은 기둥'),
   dict(kind='bg',name='옥좌의 방',size='40x30 타일 한 장',desc='황금 예복의 군주가 굳어 앉은 옥좌, 잿빛 안개'),
   dict(kind='bg',name='왕성 탑 (멀리 보이는 배경)',size='화면 배경 한 장',desc='왕도 어디서나 보이는 왕성 탑 — 7장에서는 바로 머리 위로 솟음 (다른 장 배경에도 같은 탑)'),
   dict(kind='bg',name='옥좌 뒤 제단',size='20x15 타일',desc='부서진 옥좌 뒤 숨은 제단, 붉은 틈이 열림'),
   dict(kind='mob',name='일반 마물',size='-',desc='마물은 기획 뒤 부탁 (사장님 10-24)'),
   dict(kind='elite',name='근위대장 석상',size='1.6배',desc='대회랑 끝 거대 석상, 깨어나 대검을 듦'),
   dict(kind='boss',name='루드비히 「멈춰버린 군주」',size='2.5배',desc='황금 예복, 잿빛 석회·모래로 굳은 몸, 부서진 대검의 불길한 광채'),
   dict(kind='npc',name='루드비히의 왕비 (비밀 인물)',size='1배',desc='정본 외형 없음 — 스토리 담당 확정 뒤 부탁')]
# 세계 지도(사장님 10-24 「거대한 성, 그 안 왕도」): 왕성은 한가운데, 6장은 동남 → 처음 그린 지도를 좌우로 뒤집어 6장 입구를 동남에 둠. 둘레는 내성벽.
W7=520
def fx(x):return W7-x
for z in Z:z['x']=W7-z['x']-z['w']
for a in A:a['poly']=[[fx(x),y] for x,y in a['poly']]
for q in P:q['pts']=[[fx(x),y] for x,y in q['pts']]
for l in L:l['at']=[fx(l['at'][0]),l['at'][1]]
for k in M:k['x']=fx(k['x'])-1
SW=lambda t:t.replace('서쪽','@').replace('동쪽','서쪽').replace('@','동쪽')
for o in Z+L+M:
    for f in ('name','label','note'):
        if f in o:o[f]=SW(o[f])
A+=[dict(kind='wall',poly=[[0,0],[520,0],[520,6],[0,6]]),dict(kind='wall',poly=[[0,454],[520,454],[520,460],[0,460]]),
    dict(kind='wall',poly=[[0,0],[6,0],[6,460],[0,460]]),dict(kind='wall',poly=[[514,0],[520,0],[520,460],[514,460]])]   # 내성벽 (지도 가장자리)
json.dump(dict(chapter='ch7',title='왕성 옥좌의 방',w=520,h=460,zones=Z,areas=A,paths=P,links=L,markers=M,grok=G),open(f'{D}/ch7_map.json','w'),ensure_ascii=False,indent=1)
print('markers',len(M))
