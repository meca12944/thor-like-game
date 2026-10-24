# 8장 지도 데이터 만들기 (모션연구방 10-24) — python3 docs_maps/ch8/make_ch8.py → ch8_map.json
# 결전장이라 400보다 작아도 됨 (팀장 10-24). 정본에 8장 잡몹 없음 → 몹 무리 없음.
import json,os
D=os.path.dirname(os.path.abspath(__file__))
Z=[dict(id='rift_gate',name='핏빛 하늘 입구',kind='sky',x=10,y=150,w=120,h=110,note='7장 제단을 지나 나오는 왕도 상공. 무너지는 왕도 잔해가 떠 있는 발판'),
   dict(id='skybridge',name='잔해 다리',kind='sky',x=140,y=170,w=110,h=70,note='떠 있는 성벽·옥좌 조각을 밟고 건너는 길 (몹 없음, 하늘이 점점 붉어짐)'),
   dict(id='arena1',name='공허의 틈새 결전장 (1페이즈)',kind='boss',x=260,y=120,w=150,h=150,note='사멸의 화신과 1:1. 둥근 바닥, 가장자리는 낭떠러지'),
   dict(id='arena2',name='재앙의 폭풍 (2페이즈 · 같은 자리)',kind='boss',x=260,y=10,w=150,h=100,note='같은 결전장이 붉은 실타래 폭풍에 덮인 모습. 가운데 코어를 직접 침'),
   dict(id='ending',name='결말: 코어 / 제단',kind='sky',x=420,y=120,w=90,h=150,note='보스 뒤: 코어를 부수거나 옥좌의 제단을 영구 봉인 → 왕도 소멸, 모두의 안식')]
A=[dict(kind='void',poly=[[10,150],[130,150],[130,158],[10,158]]),
   dict(kind='ruin',poly=[[40,190],[80,185],[85,220],[45,225]]),dict(kind='ruin',poly=[[160,190],[190,185],[195,210],[165,215]]),dict(kind='ruin',poly=[[210,200],[240,195],[245,225],[215,230]]),
   dict(kind='pit',poly=[[260,120],[410,120],[410,128],[260,128]]),dict(kind='void',poly=[[300,160],[370,160],[385,230],[285,230]]),
   dict(kind='web',poly=[[280,25],[390,25],[400,100],[270,100]]),dict(kind='void',poly=[[320,45],[350,45],[355,75],[315,75]])]
P=[dict(kind='bridge',w=4,pts=[[30,240],[70,205],[120,205]]),dict(kind='bridge',w=3,pts=[[130,205],[175,200],[230,215],[255,205]]),
   dict(kind='corridor',w=3,pts=[[410,195],[425,195]])]
L=[dict(**{'from':'ch7','to':'rift_gate'},kind='oneway',at=[16,245],label='7장 옥좌 뒤 제단 → 하늘'),
   dict(**{'from':'rift_gate','to':'skybridge'},kind='bridge' if False else 'gate',at=[133,205],label='잔해 다리'),
   dict(**{'from':'skybridge','to':'arena1'},kind='gate',at=[255,205],label='결전장'),
   dict(**{'from':'arena1','to':'arena2'},kind='oneway',at=[335,115],label='2페이즈 (체력 절반 → 폭풍)'),
   dict(**{'from':'arena1','to':'ending'},kind='door',at=[415,195],label='결말'),
   dict(**{'from':'rift_gate','to':'ch7'},kind='shortcut',at=[16,165],label='지름길1 제단 귀환 계단 (7장 쉼터로)'),
   dict(**{'from':'skybridge','to':'rift_gate'},kind='shortcut',at=[145,230],label='지름길2 결전장 앞 부유 발판 (다리 끝에서 내림)')]
M=[]
def mk(t,name,zone,x,y,ref='',note=''):M.append(dict(type=t,name=name,zone=zone,x=x,y=y,ref=ref,note=note))
mk('start','8장 시작 (제단을 지나옴)','rift_gate',25,240,'정본 8장 「옥좌 뒤편의 제단을 통해 왕도 상공의 찢어진 핏빛 하늘로 진입」')
mk('item','사멸의 진검 (코어 공명 각성)','rift_gate',45,230,'사멸의 진검','8장에 발을 들이는 순간 기본 검이 자동 변환 — 줍는 물건 아님, 각성 연출 자리')
mk('save','모닥불: 하늘 입구','rift_gate',100,240,'팀 제안')
mk('shortcut','제단 귀환 계단','rift_gate',20,170,'팀 제안','지름길1')
mk('landmark','떠 있는 옥좌 조각','skybridge',180,195,'팀 제안 (분위기)')
mk('save','모닥불: 결전장 앞 (보스 문 앞)','skybridge',240,230,'팀 제안 (보스 문 앞 필수)')
mk('shortcut','부유 발판 레버','skybridge',150,232,'팀 제안','지름길2: 죽은 뒤 다리를 건너뛰고 결전장 앞으로')
mk('boss','사멸의 화신 (1페이즈)','arena1',335,195,'정본 0절·3장·7-1','사멸의 진검으로 1:1 맞다이, 붉은 궤적·도트 (맵 전체 스킬·구체 공격)')
mk('boss','사멸의 화신 (2페이즈 · 코어)','arena2',335,60,'정본 0절·7-1','붉은 실타래 폭풍·화면 전체 탄막, 가운데 코어를 직접 타격')
mk('quest','사멸의 코어 부수기','ending',465,170,'정본 0절 결말','주인공이 스스로 가슴의 코어를 부숨')
mk('quest','옥좌의 제단 영구 봉인','ending',465,220,'정본 0절 결말','또는 제단을 봉인 → 왕도가 시간을 되찾고 소멸')
mk('npc','루드비히의 왕비 (비밀 인물)','ending',445,140,'정본 0절 「비밀 인물(7~8장) = 루드비히의 왕비」','자리는 팀 제안 — 등장 방식은 스토리 담당이 정할 것')
mk('landmark','해방되는 사람들 (토비·펠릭스·이안 포함)','ending',480,250,'정본 0절 결말','아이들은 죽음이 아니라 해방으로만 그림 (아동 절대 보호)')
G=[dict(kind='bg',name='핏빛 하늘',size='화면 배경 여러 겹',desc='찢어진 붉은 하늘, 잿가루가 위로 날림, 아래로 무너지는 왕도'),
   dict(kind='bg',name='떠 있는 잔해 발판',size='타일 세트 + 큰 조각 6종',desc='성벽·옥좌·계단 조각이 하늘에 떠 있음'),
   dict(kind='bg',name='공허의 틈새 결전장',size='60x60 타일 한 장',desc='둥근 돌바닥, 가장자리 낭떠러지, 가운데 붉은 틈'),
   dict(kind='bg',name='재앙의 폭풍 (2페이즈 결전장)',size='60x40 타일 + 회오리 애니',desc='같은 바닥이 붉은 실타래 회오리에 덮임, 가운데 코어'),
   dict(kind='boss',name='사멸의 화신',size='화면 1/2 이상',desc='사람 몸 없음, 붉은 실·잿가루가 뭉친 거대한 재앙 형상'),
   dict(kind='boss',name='사멸의 코어 (2페이즈 약점)',size='3x3 타일',desc='맥박치는 핏빛 결정, 실타래가 감김'),
   dict(kind='bg',name='결말 장면',size='화면 한 장',desc='무너지는 왕도와 걷히는 잿빛 안개, 빛 속으로 풀려나는 사람들'),
   dict(kind='npc',name='루드비히의 왕비 (비밀 인물)',size='1배',desc='정본 외형 없음 — 스토리 담당 확정 뒤 부탁')]
json.dump(dict(chapter='ch8',title='공허의 틈새',w=520,h=280,zones=Z,areas=A,paths=P,links=L,markers=M,grok=G),open(f'{D}/ch8_map.json','w'),ensure_ascii=False,indent=1)
print('markers',len(M))
