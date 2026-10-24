# 4장 지도 데이터 만들기 (2번방). 고칠 때는 이 파일을 고치고 다시 돌린다: python3 docs_maps/ch4/build_ch4.py
import json,random,math
random.seed(4)
Z=lambda i,n,k,x,y,w,h,note: dict(id=i,name=n,kind=k,x=x,y=y,w=w,h=h,note=note)
zones=[
 Z('front','불타는 정면 거리','field',230,400,200,130,'정면 화염 지대. 3장에서 들어오는 첫 길. 반란군 화염이 멈춘 그대로'),
 Z('alley','귀족가 뒷골목','field',10,220,210,200,'좁은 골목·마차·화로. 실라스. 직행 샛길이 여기로 나옴'),
 Z('avenue','귀족가 대로','field',230,170,200,220,'저택이 늘어선 큰길. 이안이 공을 튕김'),
 Z('roof','지붕 암살자 루트','field',10,10,210,200,'지붕 위를 건너 뛰는 길. 끝에 다락방'),
 Z('hall1','연회장 본관 1층','interior',440,190,210,160,'불타는 만찬. 중앙 긴 식탁·거대 벽난로'),
 Z('hall2','연회장 2층','interior',440,10,210,170,'귀빈석·발코니. 탐욕의 루비 반지'),
 Z('cellar','지하 와인 저장고','dungeon',440,360,210,170,'부서진 오크통·불길 없는 어둠'),
 Z('boss','엘레노어의 대연회장','boss',230,10,200,150,'보스방. 끝없는 다과회'),
 Z('grave','어린아이들의 재 무덤','hidden',10,430,210,100,'이안 샛길 3번 끝. 몹 없음 (아동 보호)'),
]
zid={z['id']:z for z in zones}
areas=[]; paths=[]; links=[]; mk=[]; grok=[]
def A(k,*pts): areas.append({'kind':k,'poly':[list(p) for p in pts]})
def R(k,w,*pts): paths.append({'kind':k,'w':w,'pts':[list(p) for p in pts]})
def L(f,t,k,at,lab): links.append({'from':f,'to':t,'kind':k,'at':list(at),'label':lab})
def M(t,n,z,x,y,ref='',note=''):
    d={'type':t,'name':n,'zone':z,'x':x,'y':y}
    if ref:d['ref']=ref
    if note:d['note']=note
    mk.append(d)
# --- terrain
A('fire',(240,470),(300,455),(310,500),(250,515)); A('fire',(360,440),(420,430),(425,480),(370,490)); A('fire',(300,410),(340,405),(345,425),(305,430))
A('ash',(235,405),(425,405),(425,420),(235,420))
for bx,by in [(240,180),(240,250),(240,320),(380,180),(380,250),(380,320)]: A('building',(bx,by),(bx+40,by),(bx+40,by+50),(bx,by+50))
A('building',(20,230),(70,230),(70,280),(20,280)); A('building',(140,240),(210,240),(210,300),(140,300)); A('building',(20,330),(80,330),(80,410),(20,410)); A('ruin',(120,340),(200,340),(200,410),(120,410))
for rx,ry in [(20,20),(80,30),(140,20),(30,100),(110,90),(160,130),(40,160)]: A('building',(rx,ry),(rx+45,ry),(rx+45,ry+40),(rx,ry+40))
A('pit',(70,60),(80,60),(80,200),(70,200)); A('pit',(125,10),(135,10),(135,150),(125,150))
A('fire',(560,250),(640,250),(640,290),(560,290))  # 1층 거대 벽난로
A('fire',(240,60),(420,60),(420,150),(240,150))  # 보스방 화염 다과회 장판 자리
A('ash',(20,450),(210,450),(210,520),(20,520))
A('wall',(450,370),(640,370),(640,380),(450,380))
# --- roads
R('road',6,(330,530),(330,400),(330,170)); R('road',4,(330,300),(220,300),(110,300),(110,420))
R('road',3,(110,220),(110,200)); R('corridor',4,(440,280),(650,280)); R('corridor',3,(545,190),(545,180),(545,100),(430,100))
R('corridor',3,(545,350),(545,450)); R('bridge',2,(45,190),(45,140),(100,120),(150,110),(190,60))
# --- links
L('ch3','front','gate',(330,529),'3장 대서고에서')
L('ch2','alley','secret',(11,300),'귀족가 직행 샛길 (2장 그레이 금서 → 1장 베르디 해독)')
L('front','avenue','gate',(330,401),'불탄 아치문'); L('front','alley','door',(231,470),'무너진 담 틈')
L('avenue','alley','gate',(231,300),'골목 입구'); L('avenue','hall1','door',(429,280),'연회장 정문')
L('alley','roof','stairs',(110,219),'지붕 사다리'); L('hall1','hall2','stairs',(545,190),'중앙 계단')
L('hall1','cellar','stairs',(545,350),'와인고 계단'); L('hall2','boss','door',(431,100),'대연회장 문')
L('roof','hall2','oneway',(219,60),'다락방 창 → 2층 (한 방향)')
L('cellar','alley','shortcut',(219,400),'지름길1: 와인고 뒷문 (안에서 열기)')
L('hall2','avenue','shortcut',(429,175),'지름길2: 발코니 줄사다리 (위에서 내리기)')
L('front','avenue','shortcut',(429,395),'지름길3: 화염 거리 옆 하수 뚜껑 (대로에서 열기)')
# 이안 샛길 3번
L('avenue','alley','secret',(260,380),'이안 샛길1 (화염 장막 뒤)'); L('alley','alley','secret',(150,330),'이안 샛길2'); L('alley','grave','secret',(60,425),'이안 샛길3 → 재 무덤')
# --- markers: start/saves
M('start','4장 시작 (3장에서 들어옴)','front',330,520)
for z,x,y in [('front',300,515),('alley',100,410),('avenue',330,385),('roof',30,195),('hall1',460,330),('cellar',460,515),('grave',30,515),('hall2',450,160)]:
    M('save','모닥불','%s'%z,x,y,note='팀 제안')
M('save','모닥불 (보스 문 앞)','hall2',450,100,note='보스 문 앞 필수')
# canon NPC / items
CAN='정본 6장 4장'
M('npc','실라스 (도굴꾼)','alley',60,300,CAN,'뒷골목 마차 밑. 보석 화상')
M('landmark','부서진 마차','alley',60,305,CAN)
M('landmark','화로 (반지 태우는 곳)','alley',85,300,'팀 제안','실라스 곁 화로')
M('quest','그림자 도둑의 망토 (반지 소각 보상)','alley',75,290,'그림자 도둑의 망토')
M('npc','이안 (수수께끼의 소년)','avenue',290,360,CAN,'무적. 공을 튕기며 콧노래. 몹 없음 반경 30')
M('quest','이안의 붉은 가죽 공','avenue',280,370,'이안의 붉은 가죽 공','공이 샛길1로 굴러감')
M('quest','공이 굴러간 자리 2','alley',150,335,'이안의 붉은 가죽 공'); M('quest','공이 굴러간 자리 3','alley',60,414,'이안의 붉은 가죽 공')
M('item','숨겨진 요람의 목검','grave',110,480,'숨겨진 요람의 목검','무덤 한가운데')
M('item','이안의 붉은 소년 망토','grave',125,480,'이안의 붉은 소년 망토','무덤 한가운데')
M('chest','다락방: 도굴꾼의 그림자 반지 · 재가 되지 못한 편지','roof',195,30,'도굴꾼의 그림자 반지, 재가 되지 못한 편지','암살자 루트 끝')
M('item','칠면조 잿더미: 귀족의 그을린 세검 · 굳어진 연회용 칼','hall1',520,250,'귀족의 그을린 세검, 굳어진 연회용 칼','중앙 긴 식탁')
M('landmark','중앙 긴 식탁 (불타는 만찬)','hall1',505,265,CAN)
M('item','벽난로 안: 불타는 낙인 반지','hall1',600,270,'불타는 낙인 반지','안개 진화 물약 또는 불타는 외투로 화염 뚫기')
M('item','탐욕의 루비 반지 (탐욕의 무게 반지)','hall2',600,60,'탐욕의 루비 반지','줍기=착복 시 실라스 즉사·저주 귀속 / 태우면 망토')
M('chest','부서진 오크통: 재앙의 흑요석 반지 · 안개 진화 물약','cellar',610,480,'재앙의 흑요석 반지, 안개 진화 물약')
M('boss','엘레노어 후작 부인 『불타는 연회의 주인』','boss',330,90,'정본 3장·7-1 4장','처치: 불타는 귀족의 외투 · 불탄 귀족의 외투 조각')
M('item','보상: 불타는 귀족의 외투 · 불탄 귀족의 외투 조각','boss',330,130,'불타는 귀족의 외투, 불탄 귀족의 외투 조각')
M('landmark','반란군 화염이 멈춘 정면 거리','front',330,470,CAN)
# --- mob packs (정본 몹: 불타는 유령 귀족 / 불탄 시체 마네킹)
NOMOB=[(290,360,30),(260,380,18),(150,330,18),(60,420,18)]  # 이안·공·샛길 근처
SAVES=[(k['x'],k['y']) for k in mk if k['type']=='save']
kinds=['불타는 유령 귀족','불탄 시체 마네킹']
def inpoly(x,y,P):
    c=False
    for i in range(len(P)):
        (x1,y1),(x2,y2)=P[i],P[i-1]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
BLOCK=[a['poly'] for a in areas if a['kind'] in('building','pit','fire','wall')]
def packs(z,step,inset=12):
    Zz=zid[z]; need=max(1,Zz['w']*Zz['h']//2500) if Zz['kind']=='field' else 0
    while True:
        pts=[]
        for gy in range(Zz['y']+inset,Zz['y']+Zz['h']-inset+1,step):
            for gx in range(Zz['x']+inset,Zz['x']+Zz['w']-inset+1,step):
                for t in range(8):
                    x=gx+random.randint(-8,8); y=gy+random.randint(-8,8)
                    if not any(inpoly(x,y,P) for P in BLOCK): break
                else: continue
                if any(math.hypot(x-a,y-b)<r for a,b,r in NOMOB): continue
                if any(math.hypot(x-a,y-b)<12 for a,b in SAVES): continue
                pts.append((x,y))
        if len(pts)>=need: break
        step-=3
    n=0
    for x,y in pts:
        k=kinds[(n+len(mk))%2]; c=random.choice([3,4,5])
        M('mob',f'{k} {c}',z,x,y,'정본 6장 4장 / 3장 엘레노어',f'{k} {c}'); n+=1
for z in ['front','alley','avenue','roof']: packs(z,50)
for z in ['hall1','hall2','cellar']: packs(z,60,25)
grok=[
 {'kind':'bg','name':'불탄 귀족가 돌바닥','size':'타일 16px 세트','desc':'검게 그을린 대리석 포석, 재가 눈처럼 쌓임, 붉은 잔불 틈'},
 {'kind':'bg','name':'멈춘 화염 장막','size':'2x4 타일 반복','desc':'타오르는 순간 그대로 굳은 불꽃 벽 (흔들림은 코드로)'},
 {'kind':'bg','name':'저택 외벽·지붕 기와','size':'타일 16px 세트','desc':'금박이 녹아내린 귀족 저택 벽, 무너진 기와 지붕 (지붕 루트)'},
 {'kind':'bg','name':'연회장 바닥·벽','size':'타일 16px 세트','desc':'붉은 융단 잿더미, 깨진 샹들리에 빛'},
 {'kind':'bg','name':'지하 와인 저장고','size':'타일 16px 세트','desc':'돌 아치 천장, 깨진 오크통, 와인 웅덩이'},
 {'kind':'bg','name':'어린아이들의 재 무덤','size':'타일 16px 세트','desc':'작은 재 무덤들, 장난감 조각, 고요하고 맑은 빛 (몹·피 없음)'},
 {'kind':'prop','name':'부서진 마차','size':'6x4 타일','desc':'뒤집힌 귀족 마차, 바퀴가 그을림 (실라스가 밑에 있음)'},
 {'kind':'prop','name':'화로','size':'2x2 타일','desc':'쇠 화로, 숯불'},
 {'kind':'prop','name':'중앙 긴 식탁','size':'12x3 타일','desc':'불타는 만찬, 칠면조 잿더미에 세검이 꽂힘'},
 {'kind':'prop','name':'거대 벽난로','size':'8x5 타일','desc':'사람 키 두 배, 꺼지지 않는 불'},
 {'kind':'prop','name':'부서진 오크통','size':'2x2 타일','desc':'금 간 와인통'},
 {'kind':'mob','name':'불타는 유령 귀족','size':'주인공 키 1배','desc':'반투명 잿빛 귀족 유령, 몸이 계속 타오름, 술잔·부채'},
 {'kind':'mob','name':'불탄 시체 마네킹','size':'주인공 키 1배','desc':'불탄 시체 잔해를 실로 매단 꼭두각시 (엘레노어가 조종)'},
 {'kind':'npc','name':'실라스','size':'주인공 비율','desc':'바싹 마른 몸, 검게 그을림, 목·손목 보석이 피부에 박힌 화상'},
 {'kind':'npc','name':'이안','size':'아이 (주인공 키 0.6)','desc':'새하얀 옛 귀족 소년복, 먼지 하나 없음, 붉은 가죽 공 (아동 보호: 다침·위협 묘사 없음)'},
 {'kind':'boss','name':'엘레노어 후작 부인 (1페이즈)','size':'주인공 키 1.6배','desc':'반쯤 불탄 화려한 드레스, 실로 유령·마네킹 조종'},
 {'kind':'boss','name':'엘레노어 후작 부인 (2페이즈)','size':'주인공 키 1.6배','desc':'드레스가 완전히 타 재가 됨, 온몸 화염'},
]
m={'chapter':'ch4','title':'잿더미 연회장 & 귀족가','w':660,'h':540,'zones':zones,'areas':areas,'paths':paths,'links':links,'markers':mk,'grok':grok}
json.dump(m,open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'ch4_map.json'),'w'),ensure_ascii=False,indent=1)
from collections import Counter
print(Counter((k['zone'],k['type']) for k in mk if k['type'] in('mob','save')))
