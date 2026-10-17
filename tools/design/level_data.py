# -*- coding: utf-8 -*-
# 캐릭터 레벨 · 경험치 · 능력치 성장 · MP(구 「파란 게이지 / 기력」) · 회피 · 필살기 게이지 설계 데이터.
# gen_docs.py 가 import → 검증(validate) → data/levels.json + data/towns.json(levels, quests[].exp) + LEVELS.md 생성.
# 숫자를 바꾸려면 이 파일의 상수만 고치고 `python3 tools/design/gen_docs.py` 를 실행한다. 표(EXP 표, 몹 EXP, 퀘스트 EXP)는 모두 공식으로 다시 계산된다.
import math, os, re
from craft_data import AREAS as _AREAS, CHAMPS as _CHAMPS, BOSSES as _BOSSES, AREA_NAMES

# ================================================================ 1. 레벨 상한 · 경험치 곡선
LEVEL_CAP=60
# 다음 레벨까지 필요 EXP = round_to(A·L^P + B·L, 5)   (L = 현재 레벨)
EXP_CURVE=dict(A=10.0,P=1.9,B=40.0,round_to=5,
  formula='다음 레벨까지 EXP(L) = 10 × L^1.9 + 40 × L (5 단위 반올림)',
  why='초반은 거의 직선(몇 마리만 잡아도 오름), 후반은 L^1.9로 완만하게 가팔라진다. 지수가 2보다 작아 Lv50 이후에도 「벽」이 생기지 않고, 몹 EXP를 지역별로 같은 공식에서 뽑아 쓰므로 어느 지역이든 적정 레벨에서 비슷한 처치 수로 1레벨이 오른다.')
def exp_to_next(L):
    if L>=LEVEL_CAP: return 0
    c=EXP_CURVE; v=c['A']*L**c['P']+c['B']*L
    return int(round(v/c['round_to'])*c['round_to'])
EXP_TABLE=[]; _tot=0
for _L in range(1,LEVEL_CAP+1):
    EXP_TABLE.append(dict(level=_L,next=exp_to_next(_L),total=_tot)); _tot+=exp_to_next(_L)
def total_exp(L): return EXP_TABLE[L-1]['total']

# ================================================================ 2. 지역별 권장 레벨 · 마을 레벨
# (진입 권장, 보스 권장). 1지역 ≈ Lv1~6 … 10지역 ≈ Lv50~58, 59~60은 원탁의 심연(엔드게임).
AREA_LEVELS={1:(1,6),2:(6,11),3:(11,16),4:(16,21),5:(21,27),6:(27,33),7:(33,39),8:(39,45),9:(45,50),10:(50,58)}
POSTGAME=dict(name='원탁의 심연 · 아스란 · 10지역 강화판 재방문',levels=(58,60),note='Lv60은 엔드게임 콘텐츠(마을 강자 징표 8개 → 원탁의 심연, 아스란)로 닿게 설계. 본편 엔딩은 Lv55~58이면 충분하다.')
# 마을 퀘스트 기준 레벨 (도착 시점의 권장 레벨)과 퀘스트 EXP를 몰아줄 지역
TOWN_LEVELS={'A':dict(level=2,areas=[1]),'B':dict(level=6,areas=[2,3]),'H':dict(level=7,areas=[2,3]),'G':dict(level=12,areas=[3,4]),
             'F':dict(level=22,areas=[5,6]),'E':dict(level=34,areas=[7]),'C':dict(level=40,areas=[8]),'D':dict(level=46,areas=[9,10])}
def area_mid(a): lo,hi=AREA_LEVELS[a]; return (lo+hi)/2

# ================================================================ 3. 몬스터 EXP
KILLS_PER_LEVEL=30        # 적정 레벨에서 일반 몹 몇 마리로 1레벨이 오르는지 (지역 중간 레벨 기준)
CHAMPION_MULT=6           # 챔피언 = 그 지역 일반 몹 기준 EXP × 8 (리스폰 후에도 같은 EXP, 레벨 차 보정은 적용)
BOSS_LEVEL_SHARE=0.6      # 보스 = 보스 권장 레벨의 「다음 레벨까지 EXP」 × 1.0 (= 레벨의 60%)
FINAL_BOSS_SHARE=1.2      # 10지역 마룡
ENHANCED_MULT=1.0         # 10지역 강화판 몹: 10지역 기준 EXP 그대로 (원본 지역 무관)
# 몹별 가중치 (기본 1.0). 약한 무리형은 낮게, 단단한 몹은 높게. 이름은 craft_data.AREAS 와 같아야 한다.
MOB_EXP_WEIGHT={'뿔토끼':0.8,'도토리 다람쥐':0.8,'숲 슬라임':0.8,'멧돼지':1.3,'호박 허수아비':1.1,'나무 정령 새싹':1.2,
 '박쥐':0.7,'반딧불 지렁이':0.8,'곡괭이 바위도깨비':1.3,'수정 슬라임':1.1,
 '대머리 독수리':0.9,'선인장 골렘':1.3,'낙타 거북':1.3,'사막 도적':1.2,
 '스카라베 떼':0.7,'함정 석판 골렘':1.4,'아누비스 경비병':1.3,'저주 항아리':0.8,
 '해파리':0.8,'상어 돌격병':1.3,'아귀':1.2,'소라게':0.9,
 '갈매기':0.7,'따개비 골렘':1.4,'바다 거북 방패병':1.3,'해적 해골':1.1,
 '불꽃 임프':0.9,'용암 바위 골렘':1.4,'저주받은 갑옷':1.3,'잿불 불사조 새끼':1.1,
 '서리 요정':0.8,'설인 새끼':1.2,'얼음 거북':1.3,'폭풍 가고일':1.3,
 '고블린':0.8,'보라 도깨비불':0.8,'가고일 석상':1.4,'그림자 암살자':1.3}
def mob_base_exp(a):
    return max(2,int(round(exp_to_next(int(area_mid(a)))/KILLS_PER_LEVEL)))
def mob_level(a,i,n=8):
    lo,hi=AREA_LEVELS[a]; return lo+round(i*(hi-lo-1)/(n-1))
MONSTER_EXP=[]
for _a in range(1,11):
    lo,hi=AREA_LEVELS[_a]; base=mob_base_exp(_a)
    if _a<10:
        mobs=[dict(name=m[0],level=mob_level(_a,i),exp=max(1,int(round(base*MOB_EXP_WEIGHT.get(m[0],1.0)))),weight=MOB_EXP_WEIGHT.get(m[0],1.0)) for i,m in enumerate(_AREAS[_a]['mobs'])]
        champs=[dict(name=c[1],level=hi,exp=base*CHAMPION_MULT) for c in _CHAMPS if c[0]==_a]
    else:   # 10지역: 1~9지역 몹·챔피언의 강화판 (72종 + 18종). 대표값만 둔다.
        mobs=[dict(name=f'강화 {_AREAS[k]["mobs"][0][0]} 외 {k}지역 8종',level=mob_level(10,k-1,9),exp=int(round(base*ENHANCED_MULT)),weight=1.0,enhanced_of=k) for k in range(1,10)]
        champs=[dict(name='강화 챔피언 18종 (1~9지역 챔피언의 강화판)',level=hi,exp=base*CHAMPION_MULT)]
    b=[x for x in _BOSSES if x[0]==_a][0]
    boss=dict(name=b[1],level=hi,exp=int(round(exp_to_next(hi)*(FINAL_BOSS_SHARE if _a==10 else BOSS_LEVEL_SHARE)/10))*10)
    MONSTER_EXP.append(dict(area=_a,name=AREA_NAMES[_a],levels=[lo,hi],base_exp=base,mobs=mobs,champions=champs,boss=boss))
# 인간 강적 (마을 강자 결투 / 아스란)
STRONGMAN_SHARE=0.4       # 강자 = (마을 레벨 + 4)의 다음 레벨 EXP × 0.6. 살려 줘도 죽여도 같은 EXP (선악만 다름)
def strongman_exp(town): L=TOWN_LEVELS[town]['level']+4; return int(round(exp_to_next(L)*STRONGMAN_SHARE/10))*10
def strongman_area(town):   # 결투 권장 레벨(마을 레벨 + 4)이 속한 지역
    L=TOWN_LEVELS[town]['level']+4
    return next(a for a in range(1,11) if AREA_LEVELS[a][0]<=L<AREA_LEVELS[a][1] or a==10)
ASRAN_EXP=int(round(exp_to_next(59)*2.0/10))*10

# ================================================================ 4. 레벨 차이 보정 (파밍 남용 방지)
# diff = 주인공 레벨 - 몹 레벨. 위에서부터 첫 번째로 diff <= max 인 줄의 배율. 최소 1 EXP.
LEVEL_DIFF_SCALE=[(-6,1.25,'6 이상 낮음: 도전 보너스 +25% (상한)'),(-3,1.10,'3~5 낮음: +10%'),(2,1.00,'±2 이내: 그대로'),
                  (3,0.80,'3 높음'),(4,0.60,'4 높음'),(5,0.40,'5 높음'),(6,0.25,'6 높음'),(7,0.12,'7 높음'),(99,0.05,'8 이상 높음: 5% (사실상 0)')]
LEVEL_DIFF_RULES=['보스는 리스폰하지 않으므로 보정 하한 50% (늦게 잡아도 손해가 크지 않음).',
  '챔피언은 같은 보정 + 기존 「10분 안에 3번 넘게 잡으면 재료 절반」 규칙과 별개로, 같은 챔피언 4번째 처치부터 EXP 절반 (10분 창).',
  '퀘스트 EXP는 레벨 차 보정 없음 (늦게 깨도 그대로). 대신 퀘스트 EXP 자체가 마을 기준 레벨로 고정돼 있어 후반엔 비중이 작다.',
  '동료 히로인이 마무리해도 주인공이 전부 받는다 (분배 없음).',
  '마을 사람·경비병 처치 EXP(악의 길·마왕)도 같은 보정을 쓴다. 마을 사람 레벨 = 그 마을 기준 레벨.']
def diff_mult(hero_lv,mob_lv,boss=False):
    d=hero_lv-mob_lv
    for mx,m,_ in LEVEL_DIFF_SCALE:
        if d<=mx: return max(m,0.5) if boss else m

# ================================================================ 5. 능력치 성장 (고정 성장 + 소량 분배 포인트)
GROWTH_CHOICE=('고정 성장 + 소량 분배 포인트(힘·체력·정신 3종). 이유: ① 회피 구르기만으로 막는 액션이라 숫자 빌드보다 조작이 중심이어야 하고, 고정 성장이 지역 난이도 곡선을 예측 가능하게 만든다(적 스케일 계약, 아래 9장). '
  '② 그래도 「내 캐릭터」 감각을 주려고 레벨당 1포인트를 3종에만 나눠 준다. 포인트 효과는 고정 성장의 약 20~25% 규모라 잘못 찍어도 진행이 막히지 않는다. ③ 마왕 강림처럼 장비·스킬이 잠기는 루트에서도 성장 선택지가 남는다.')
# 구간별 레벨당 증가량: [(시작 레벨, 끝 레벨, 증가량)]. Lv1 값 = base.
GROWTH={
 'hp':  dict(name='최대 체력(HP)',base=50,steps=[(2,20,2),(21,40,3),(41,60,4)],unit='HP',note='1하트 = 10HP (반 칸 = 5HP). HUD는 하트 20칸까지 그리고 넘으면 하트 줄 끝에 ×숫자. 하트 조각·거인의 열매·원한의 조각은 +10HP(1하트)씩 따로 더한다.'),
 'atk': dict(name='기본 공격력(ATK)',base=10,steps=[(2,30,1),(31,60,1.5)],unit='',note='최종 공격력 = ATK + 무기 공격 × (1 + 강화 %). 콤보 타마다 배율이 붙는다(1타 1.0 / 2타 1.0 / 3타 1.4).'),
 'def': dict(name='방어(DEF)',base=0,steps=[(2,60,0.5)],unit='',note='받는 피해 = 원래 피해 × 60 / (60 + DEF합). DEF합 = 레벨 DEF + 몸·투구·보조무기 방어.'),
 'mag': dict(name='마력(MAG, 스킬 위력)',base=14,steps=[(2,60,2)],unit='',note='스킬 피해 = 스킬 배율(dmg) × (0.5 × 최종 공격력 + 0.5 × MAG). 구 「기력」의 위력 부분.'),
 'mp':  dict(name='최대 MP',base=80,steps=[(2,60,2)],unit='MP',note='구 「파란 게이지」. 1칸 = 10MP 눈금 (Lv1 = 8칸, 기존 데모와 같음).'),
 'crit':dict(name='치명타 확률',base=5.0,steps=[(2,60,0.1)],unit='%',note='치명타 피해 ×1.5. 상한 40%.'),
}
def stat_at(stat,L,route='hero',descent_level=None):
    g=GROWTH[stat]; v=float(g['base'])
    for lv in range(2,L+1):
        inc=next(i for a,b,i in g['steps'] if a<=lv<=b)
        if route=='demon' and descent_level is not None and lv>descent_level: inc*=DEMON_GROWTH['mult'][stat]
        v+=inc
    v=round(v,1); return int(v) if v==int(v) else v
STAT_POINTS=dict(per_level=1,from_level=2,total=LEVEL_CAP-1,cap_per_stat=30,
 stats=[dict(id='str',name='힘',effect='공격력 +1 · 치명타 +0.1%p',per=dict(atk=1.0,crit=0.1)),
        dict(id='vit',name='체력',effect='최대 HP +4 · DEF +0.3',per=dict(hp=4,defense=0.3)),
        dict(id='spi',name='정신',effect='MAG +1.5 · 최대 MP +2 · MP 자연 회복 +1%',per=dict(mag=1.5,mp=2,mp_regen_pct=1))],
 respec='재분배: C 성녀 설화 또는 D 대주교 루미엘(대성당)에게서 금화 50 × 레벨. 처음 1회 무료. 마왕은 마염 제단에서 원한 서린 혼석 1개.',
 why='레벨당 1포인트(총 59), 한 능력치 최대 30. 고정 성장 대비 약 20~25% 규모라 「잘못 찍은 빌드」가 생기지 않는다.')

# ================================================================ 6. 레벨 보상 (5레벨마다 작은 보상, 10레벨마다 큰 보상)
PERKS=[
 dict(level=5, major=False,id='quick_potion',name='빠른 물약',desc='물약 사용 모션 0.6초 → 0.4초'),
 dict(level=10,major=True, id='combo4',name='4타 콤보',desc='3타 돌려베기 직후 공격 → 4타 「내려찍기」(배율 1.6, 작은 충격파). 콤보 시트 내려찍기 4프레임 재사용'),
 dict(level=15,major=False,id='iframe1',name='회피 무적 +',desc='구르기 무적 0.20초 → 0.23초'),
 dict(level=20,major=True, id='ult_rate1',name='필살기 게이지 충전 +15%',desc='필살기 게이지 획득량 ×1.15'),
 dict(level=25,major=False,id='roll_cd1',name='회피 재사용 -',desc='구르기 재사용 0.55초 → 0.50초'),
 dict(level=30,major=True, id='perfect_window',name='퍼펙트 회피 판정 확대',desc='퍼펙트 회피 판정 0.12초 → 0.16초, 퍼펙트 회피 MP 회복 15 → 20'),
 dict(level=35,major=False,id='iframe2',name='회피 무적 ++',desc='구르기 무적 0.23초 → 0.26초'),
 dict(level=40,major=True, id='dash_strike',name='회피 반격',desc='구르기 직후 0.25초 안에 공격 → 돌진 찌르기(배율 1.5, 관통). 퍼펙트 회피 뒤라면 반드시 치명타'),
 dict(level=45,major=False,id='roll_cd2',name='회피 재사용 -- · 치명 +3%',desc='구르기 재사용 0.50초 → 0.45초, 치명타 확률 +3%p'),
 dict(level=50,major=True, id='combo5',name='5타 콤보 · 필살기 충전 ++',desc='4타 뒤 공격 → 5타 「낙인 회전참」(배율 2.0, 원형). 필살기 게이지 획득량 ×1.30 (Lv20과 합산 아님, 대체)'),
 dict(level=55,major=False,id='mp_regen',name='MP 순환',desc='MP 자연 회복 +25%, 일반 공격 적중 MP +1'),
 dict(level=60,major=True, id='brand_bloom',name='낙인 개화',desc='필살기를 쓴 뒤 6초 동안 스킬 MP 소모 0. 칭호별 변형: 영웅=아군(히로인) HP 30% 회복 / 필멸자=그대로 / 타락한 필멸자=처치 시 HP 흡수'),
]
# 마왕 강림 후 바뀌는 보상 (같은 레벨 칸을 대체. 이미 얻은 것도 강림 순간 바뀜)
DEMON_PERK_SWAP={
 'combo4':'종언 3연격 3타 뒤 촉수 추가타가 2회로',
 'combo5':'종언 3연격 회전 베기 범위 +25%, 구조물 피해 ×2.5',
 'dash_strike':'구르기 대신 「그림자 걸음」(짧은 순간이동, 무적 동일) — 직후 공격 시 내려찍기',
 'ult_rate1':'파멸 게이지 획득 +15%',
 'brand_bloom':'멸계강림 뒤 6초 동안 마왕 스킬 MP 소모 0',
}

# ================================================================ 7. 칭호(선악) · 마왕 루트와 레벨
KARMA_EXP=[
 dict(title='영웅',cond='선악 +40 이상',exp='퀘스트 EXP +15%. 동료 히로인 레벨 보너스 +1',growth='기본 성장',npc_kill='마을 사람을 죽이면 EXP ×0.5 (그리고 칭호를 잃는다)'),
 dict(title='필멸자',cond='선악 -39 ~ +39',exp='기준',growth='기본 성장',npc_kill='마을 사람 처치 EXP ×0.5 (악의 길)'),
 dict(title='타락한 필멸자',cond='선악 -40 ~ -59 (강림 전)',exp='몹 처치 EXP +10% (굶주림). 선의 퀘스트 의뢰 대부분 거절 → 퀘스트 EXP 감소분을 처치로 메움',growth='기본 성장',npc_kill='마을 사람 처치 EXP ×0.75, 처치 시 MP +10'),
 dict(title='마왕',cond='마왕 강림 후 (영구)',exp='몹 처치 EXP +15%. 어른 NPC·경비병·마을 강자 처치 EXP ×1.0. 구조물 붕괴 단계마다 소량 EXP. 선의 퀘스트 EXP 없음 (악의 길 퀘스트만)',growth='마왕 성장 (아래 표)',npc_kill='×1.0 (아이는 대상이 아님 — 공격이 통과)'),
]
DEMON_GROWTH=dict(
 mult=dict(hp=1.25,atk=1.3,def_=1.0,mag=0.8,mp=0.6,crit=1.5),
 rule='강림한 레벨 이후 오르는 레벨부터 레벨당 증가량에 배율을 곱한다(소급 없음). HP·공격이 더 크게 오르고, MP 최대치는 덜 오른다 — 마왕은 MP를 「회복」하지 않고 「빼앗는다」(MP 장 참고).',
 points='분배 포인트는 계속 받는다. 강림 순간 정신(SPI)에 찍은 포인트를 힘·체력으로 1회 무료 재분배할 수 있다(남겨도 됨 — 마왕 스킬도 MP를 쓴다).',
 descent_bonus='강림 순간 1회: 최대 HP +10% (괴수 갑옷), 레벨은 그대로.',
 structure_exp='구조물 붕괴 1단계 = 그 마을 기준 일반 몹 EXP × 0.3',
 townsfolk_exp='마을 사람 처치 EXP = 전투 HP ÷ 10 × 그 마을 지역의 일반 몹 기준 EXP (경비병 HP 30 → 몹 3마리 분량). 강림 전 악의 길은 ×0.5 / ×0.75(타락한 필멸자).',
 lock_note='마왕 루트는 스킬·장비가 잠기지만 레벨 성장·분배 포인트·레벨 보상(대체판)은 계속된다. 고정 장비 「종언」 공격력은 강림 순간 무기 공격 ×1.3, 이후 보스당 +2 (기존 규칙).')
DEMON_GROWTH['mult']['def']=DEMON_GROWTH['mult'].pop('def_')

# ================================================================ 8. 동료 히로인 레벨
COMPANION_LEVEL=dict(
 rule='히로인은 따로 EXP를 모으지 않는다. 레벨 = 주인공 레벨 + 호감도 보정 (1 ~ 60). 동행하지 않아도 같이 오른다(파티에서 빠져 있다가 다시 불러도 뒤처지지 않음).',
 affinity_offset=[(0,39,-3),(40,59,-2),(60,79,-1),(80,99,0),(100,100,1)],
 hero_title_bonus='주인공이 「영웅」이면 +1 추가.',
 stats='히로인 HP = (히로인 데이터 hp ÷ 50) × 주인공 기본 HP 곡선(그 레벨) × 0.8. 공격 = 주인공 ATK 곡선 × 0.7 + 지역 기준 무기 공격 × 0.5. 분배 포인트·장비 없음.',
 affinity_stat='호감도 보너스: 모든 능력치 +(호감도 ÷ 10)% (호감도 100 = +10%).',
 down='쓰러짐·부활 규칙은 기존 동료 규칙 그대로 (사망 없음). 쓰러져도 EXP 불이익 없음.',
 demon='마왕 루트: 동행 중인 히로인(유나처럼 끌려오는 경우)은 레벨이 강림 순간에 멈춘다.')
def companion_level(hero_lv,affinity,hero_title='필멸자'):
    off=next(o for a,b,o in COMPANION_LEVEL['affinity_offset'] if a<=affinity<=b)+(1 if hero_title=='영웅' else 0)
    return max(1,min(LEVEL_CAP,hero_lv+off))

# ================================================================ 9. 퀘스트 EXP
# 퀘스트 EXP = 다음 레벨 EXP(마을 기준 레벨 + 보정) × 종류 배율 (10 단위 반올림)
QUEST_TYPE_MULT={'사냥':0.12,'배달':0.10,'숨은 물건 찾기':0.08,'호위':0.14,'연계':0.16,'잠수':0.12,'대장간':0.14,
                 '동료 동행':0.12,'결투':0.0,'암살':0.0,'악의 길':0.14,'악의 길 (변형)':0.12}
QUEST_LEVEL_OFFSET={'연계':2,'대장간':2,'잠수':2,'악의 길':2,'악의 길 (변형)':2}
QUEST_RULES=['결투(⑦)·암살(⑧) 퀘스트는 퀘스트 EXP 0 — 대신 마을 강자 처치 EXP(강자 EXP)를 받는다. 살려 주든 죽이든 같은 EXP라 선택이 EXP로 기울지 않는다.',
  '동료 퀘스트는 단계가 오를수록 기준 레벨 +2씩 (2단계 +2, 3단계 +4).','영웅 칭호는 퀘스트 EXP +15% (6장).','악의 길 퀘스트는 강림 후에도 받을 수 있다.']
def quest_exp(q,town):
    m=QUEST_TYPE_MULT.get(q.get('type'),0.3)
    if m==0: return 0
    L=TOWN_LEVELS[town]['level']+QUEST_LEVEL_OFFSET.get(q.get('type'),0)
    if q.get('companion'): L+=2*(q['companion']['step']-1)
    return int(round(exp_to_next(min(L,LEVEL_CAP-1))*m/10))*10

# ================================================================ 10. 적 스케일 계약 (레벨이 실제로 의미를 갖게 하는 규칙)
def expected_weapon(a):   # 지역 티어 상점 무기 평균 공격 × 그 시점 강화
    from towns_data import EQUIP_ITEMS, ENH_LEVELS
    ws=[e['atk'] for e in EQUIP_ITEMS if e['slot']=='weapon' and e['tier']==a and e['source']['type']=='shop'] or [e['atk'] for e in EQUIP_ITEMS if e['slot']=='weapon' and e['tier']==a]
    enh={1:1,2:2,3:3,4:3,5:4,6:5,7:6,8:7,9:8,10:9}[a]
    pct=[l for l in ENH_LEVELS if l['level']==enh][0]['atk_pct']
    return sum(ws)/len(ws)*(1+pct/100), enh
def expected_def(a):
    from towns_data import EQUIP_ITEMS
    avg=lambda s:(lambda v:sum(v)/len(v) if v else 0)([e.get('defense',0) for e in EQUIP_ITEMS if e['slot']==s and e['tier']<=a and e['tier']>=a-1])
    return avg('armor')+avg('helmet')+avg('offhand')*0.5
def expected_hero(a):
    L=int(area_mid(a)); w,enh=expected_weapon(a)
    ap=stat_at('atk',L)+w; df=stat_at('def',L)+expected_def(a); hp=stat_at('hp',L)
    return dict(level=L,attack=round(ap,1),defense=round(df,1),hp=hp,weapon=round(w,1),enh=enh,mag=stat_at('mag',L),mp=stat_at('mp',L))
def enemy_scale():
    base=expected_hero(1); out=[]
    for a in range(1,11):
        h=expected_hero(a)
        hp_unit=h['attack']/base['attack']
        dmg_unit=(h['hp']/base['hp'])*((60+h['defense'])/(60+base['defense']))
        out.append(dict(area=a,hero=h,hp_mult=round(hp_unit,2),dmg_mult=round(dmg_unit,2)))
    return out
SCALE_RULE=('설계 문서의 적 체력(1지역 보스 = 100 기준 상대값)과 공격(하트 단위)은 「그 지역 권장 레벨의 주인공」 기준이다. 실제 값 = 체력 × hp_mult[지역], 공격 = 하트 × 10HP × dmg_mult[지역]. '
  'hp_mult는 권장 레벨 주인공의 예상 공격력 비율, dmg_mult는 예상 HP × 방어 보정 비율이다. 그래서 적정 레벨이면 「몇 대 때려야 잡고 몇 대 맞으면 죽는지」가 설계값 그대로이고, 레벨이 높으면 빨리 잡고 덜 아프며, 낮으면 반대가 된다. 마을 사람·강자는 그 마을 기준 레벨의 지역 값을 쓴다.')

# ================================================================ 11. 사망 페널티
DEATH=dict(choice='가벼운 페널티',rules=['EXP는 잃지 않는다 (레벨 다운 없음).','「다시 도전」: 보스·강자 방 입구 또는 마지막으로 지나간 화면 입구에서 HP·MP 가득, 필살기 게이지 0. 페널티 없음.',
  '「마을로」: 마지막으로 들른 마을 여관 앞. 들고 있던 금화 10% 잃음 (최대 500).','마왕: 「다시 도전」만 가능, 파멸 게이지 0. 금화 손실 없음 (빼앗을 사람이 없다).'],
 why='회피 구르기만으로 막는 패턴 액션이라 죽음은 「패턴을 배우는 과정」이다. Ys VIII처럼 즉시 재도전을 기본으로 두고, 마을 귀환에만 작은 금화 손실을 둔다.')

# ================================================================ 12. MP (구 「파란 게이지」·「기력」 통합)
MP=dict(
 rename='기존 「파란 게이지 / 기력 / 정령력」은 모두 MP 하나로 통합한다. 데모의 8칸 게이지 = Lv1 최대 MP 80 (1칸 = 10MP 눈금). 기존 데이터의 「파란 게이지 N칸」은 「MP N×10」으로 읽는다. 스킬 위력은 MAG(마력) 능력치로 분리.',
 legacy_unit=10,
 max='최대 MP = 기본 성장(Lv1 80 → Lv60 198) + 정신 포인트 ×2 + 정령의 물방울(영구 +10, 8개) + 장비(공허의 반지 +10). 마왕은 강림 후 증가량 ×0.6.',
 regen=[
  dict(id='passive',name='자연 회복 (전투 중)',value='0.6 MP/초 (≈ 1칸 / 17초). 정신 포인트당 +1%, Lv55 보상 +25%, 정령 찻잎 60초 ×2, 서리 부적 +10%, 공허의 반지 +15%'),
  dict(id='passive_idle',name='자연 회복 (비전투)',value='화면에 적대 대상이 없고 3초 지나면 자연 회복 ×4 (2.4 MP/초)'),
  dict(id='hit',name='일반 공격 적중',value='타격 1회당 +3 MP (콤보 마지막 타 +5). 한 번 휘두름에 최대 2마리까지만 계산. Lv55 보상 +1. 구조물·소품 타격은 0'),
  dict(id='perfect_dodge',name='퍼펙트 회피',value='적 공격 판정 직전 0.12초(Lv30: 0.16초) 안에 구르기 → +15 MP(Lv30: +20) + 1.2초 슬로 모션 + 필살기 게이지 +5'),
  dict(id='kill',name='처치',value='+1 MP (챔피언 +10)'),
  dict(id='none',name='회복 없음',value='스킬 시전 중과 시전 끝난 뒤 0.5초, 필살기·멸계강림 연출 중, 잠수 중에는 모든 MP 회복이 멈춘다'),
 ],
 items=[('spirit','정령수','MP 30 회복 (구 「3칸」)'),('spirit_tea','정령 찻잎','60초간 MP 자연 회복 ×2'),('spirit_hi','상급 정령수','MP 전부 회복'),
        ('panacea_full','만능 영약','HP·MP 전부 회복 + 상태이상 해제'),('spirit_drop','정령의 물방울','최대 MP +10 (영구, 구 「+1칸」)')],
 gear=[('a_frost_amulet','서리 부적','MP 자연 회복 +10%'),('h_witch_hat','화염 마녀의 모자','스킬 MP 소모 -10%'),('o_void_ring','공허의 반지','최대 MP +10, 자연 회복 +15%')],
 rest=['마을 여관·집 침대(1박): HP·MP 전부 회복. 영웅·필멸자 무료, 타락한 필멸자(악명) 금화 10 × 지역 번호, 현상금 ★2 이상 마을은 이용 불가.','마을 분수·우물 옆에 서 있으면 MP 자연 회복 ×4 (전투 불가 구역).','지역 안 세이브 결정(쉼터 화면): HP 30%, MP 전부 회복 (1회 방문당 1번, 화면을 나갔다 오면 다시).','마왕: 여관 불가. 폐허의 「검은 왕좌」·검은 성채에서만 휴식 (HP·MP 전부).'],
 ult_separate='MP와 필살기 게이지는 별개다. MP = 스킬 3칸(Digit1~3)의 자원. 필살기 게이지(0~100, 화면 아래 금색 막대) = 광역 키(Q)의 전체 화면 필살기 자원. 서로 바꿔 쓸 수 없고, MP 회복 수단은 필살기 게이지를 채우지 않는다 (퍼펙트 회피만 둘 다 조금씩).',
)
# 스킬별 MP 소모. demo_id = 타운 데모 game.template.html SKILLS[].id (cost는 칸 단위 → ×10).
SKILL_MP=[
 # (분류, id, 이름, MP, 재사용 초, 비고)
 ('보스','quake','대지의 수정',20,3.0,''),('보스','thread','수정 실',10,1.5,''),('보스','sand','사중 잠행',20,3.5,''),('보스','pact','망자의 계약',30,6.0,''),
 ('보스','water','해류의 숨결',10,1.2,'잠수 진입은 MP 0 (잠수 중 MP 회복 없음)'),('보스','shield','산호 방패',10,1.0,'들 때 10, 유지 중 초당 4'),('보스','fire','업화의 검',20,2.0,''),
 ('보스','bolt','뇌광 질주',20,2.0,''),('보스','time','시간 정지',40,10,''),('보스','dragon','삼룡의 각성',80,20,'MP 스킬 중 최대 (Lv1 MP 전부). 필살기 게이지와는 별개'),
 ('강자','kalbaram','바람 가르기',20,4,'어둠 변형 +5MP'),('강자','sol','매의 삼연사',25,5,'어둠 변형 +5MP'),('강자','gomsoe','대지 강권',25,5,'어둠 변형 +5MP'),
 ('강자','zahra','모래 장막',20,6,'어둠 변형 +5MP'),('강자','mago','작살 사슬',15,3,'어둠 변형 +5MP'),('강자','garon','철벽 반격',20,6,'어둠 변형 +5MP'),
 ('강자','hanbing','한기 장풍',25,5,'어둠 변형 +5MP'),('강자','grim','단죄의 일격',40,12,'어둠 변형 +5MP'),
 ('인간 보스','asran','팔방검',45,8,'아스란 흡수 스킬'),
 ('전설검','hs_tak','천일섭 (탁검)',35,10,'HIDDEN_SWORDS cost 그대로 (MP)'),('전설검','hs_gyu','월영참 (규검)',30,8,'HIDDEN_SWORDS cost 그대로 (MP)'),
 ('마왕','dk_black_moon','흑월참',20,4,'DEMON_KING cost 그대로 (MP)'),('마왕','dk_abyss_grasp','심연의 촉수',35,9,'붙잡은 적마다 MP +3 흡수'),('마왕','dk_horn_roar','뿔관의 포효',30,12,''),
]
SKILL_COST_RULES=['빛 변형은 기본형과 같은 MP, 어둠 변형은 +5MP(더 강한 대신 비쌈). 스킬 MP는 레벨이 올라도 고정 → 최대 MP·회복이 늘수록 더 자주 쓴다.',
 '시전 중 MP가 모자라면 시전하지 않고 「MP 부족」 토스트 (데모의 「기력 부족」을 바꿔 표기).','화염 마녀의 모자 -10%는 반올림(최소 5).','일월식(찬검)·멸계강림은 MP가 아니라 필살기 게이지 / 파멸 게이지를 쓴다.']
DEMON_MP=dict(rule='마왕은 MP 자연 회복이 없다 (굶주림). 대신 생명을 빼앗아 채운다.',
 drain=[('일반 적 처치','+6 MP'),('챔피언 처치','+25 MP'),('어른 NPC·경비병 처치','+15 MP'),('마을 강자 처치','MP 전부'),('일반 공격(종언 3연격) 적중','+4 MP (마지막 타 +6)'),
        ('구조물 붕괴 1단계','+2 MP'),('퍼펙트 회피(그림자 걸음)','+10 MP'),('심연의 촉수로 붙잡은 적','적마다 +3 MP')],
 items='물약류는 뒷거래(1.5배)로만 구한다. 마염 제단 소모품(혼석 정제)이 MP 회복을 대신한다.',
 max='최대 MP 증가량 ×0.6 → 작은 통을 자주 채우는 구조.')
COMPANION_MP=dict(rule='히로인은 자기 MP 통을 갖는다: 최대 MP = 40 + 레벨 × 1. 자연 회복 1 MP/초, 일반 공격 적중 +2 MP. 고유 스킬 MP = 재사용 초 × 2.5 (5 단위).',
 ai='AI는 MP가 스킬 비용 이상이고 재사용 대기가 끝났으며 화면 안에 대상이 있을 때만 스킬을 쓴다. 회복형(설화 「눈꽃 축복」)은 주인공 HP 50% 이하일 때만.',
 duo='듀오 합동기(호감도 60): 주인공 필살기 게이지 50 + 히로인 MP 50% 소모. 필살기 게이지가 100이면 단독 필살기와 합동기 중 하나를 고른다(Q 짧게 / 길게).',
 potion='주인공이 쓴 정령수·상급 정령수는 동행 히로인 MP도 같은 비율로 채운다. 여관 휴식도 동일.')
ROLL=dict(choice='스태미나 없음 — 구르기는 무료 + 짧은 재사용',
 why='Ys VIII처럼 회피가 유일한 방어이므로 회피를 자원으로 묶으면 패턴 읽기보다 게이지 관리가 앞선다. 데모도 이미 재사용 0.55초 대시라서 그대로 이어 쓴다. 대신 「연속 3회 뒤 피로」로 무한 구르기를 막고, 레벨 보상이 무적·재사용을 조금씩 늘린다.',
 base=dict(duration=0.20,iframes=0.20,cooldown=0.55,perfect_window=0.12,chain=3,fatigue=0.8),
 rules=['구르기 지속 0.20초 전체 무적 (Lv15 0.23 / Lv35 0.26).','재사용 0.55초 (Lv25 0.50 / Lv45 0.45).',
        '1.5초 안에 3번 연속 구르면 다음 구르기까지 0.8초 피로 (짧게 숨 고르는 모션). 퍼펙트 회피 성공은 연속 횟수에서 빠진다.',
        '퍼펙트 회피: 적 공격 판정 직전 0.12초(Lv30 0.16) 안에 구르면 성공 → 1.2초 슬로, MP +15(+20), 필살기 게이지 +5.','스킬·필살기 시전 중에는 구를 수 없다 (시전 취소 없음).'])
ULT_GAUGE=dict(name='필살기 게이지',range=[0,100],
 gain=[('일반 공격 적중','+0.5 (스킬 적중은 0)'),('받은 피해','반 칸(5HP)당 +2'),('퍼펙트 회피','+5'),('일반 적 처치','+1'),('챔피언 처치','+10'),('보스 페이즈 전환','+15')],
 use='광역 키(Q): 게이지 100 전부 → 전체 화면 필살기. 기본은 「낙인 해방」(제안: 화면 전체 피해 15, 보스는 최대 체력 8% 상한, 0.8초 시간 정지 연출), 찬검을 들면 「일월식」(기존 데이터). 마왕은 같은 칸이 파멸 게이지(멸계강림)로 바뀐다.',
 keep='게이지는 지역·마을을 옮겨도 유지, 사망·「다시 도전」 시 0. Lv20·Lv50 보상이 획득량을 올린다.')

# ================================================================ 검증
def validate(towns=None,template=None):
    nx=[r['next'] for r in EXP_TABLE[:-1]]; assert all(b>a for a,b in zip(nx,nx[1:])) and EXP_TABLE[-1]['next']==0
    ks=sorted(AREA_LEVELS); assert ks==list(range(1,11))
    for a in range(1,10): assert AREA_LEVELS[a][1]==AREA_LEVELS[a+1][0],a
    assert AREA_LEVELS[1][0]==1 and AREA_LEVELS[10][1]<=LEVEL_CAP and POSTGAME['levels'][1]==LEVEL_CAP
    for m in MOB_EXP_WEIGHT: assert any(m==x[0] for a in _AREAS for x in _AREAS[a]['mobs']),m
    for g in GROWTH.values():
        lv=sorted((a,b) for a,b,_ in g['steps']); assert lv[0][0]==2 and lv[-1][1]==LEVEL_CAP and all(p[1]+1==q[0] for p,q in zip(lv,lv[1:]))
    assert all(p['level']%5==0 and (p['major']==(p['level']%10==0)) for p in PERKS) and [p['level'] for p in PERKS]==list(range(5,LEVEL_CAP+1,5))
    assert set(DEMON_PERK_SWAP)<={p['id'] for p in PERKS}
    assert {k['title'] for k in KARMA_EXP}=={'영웅','필멸자','타락한 필멸자','마왕'}
    assert set(DEMON_GROWTH['mult'])==set(GROWTH)
    for a,b,o in COMPANION_LEVEL['affinity_offset']: assert a<=b
    assert stat_at('mp',1)==80 and MP['legacy_unit']==10
    ids=[s[1] for s in SKILL_MP]; assert len(set(ids))==len(ids) and all(s[3]>0 and s[3]%5==0 for s in SKILL_MP)
    from towns_data import HIDDEN_SWORDS, DEMON_KING   # 기존 데이터의 MP 비용과 일치해야 한다
    _mp={s[1]:s[3] for s in SKILL_MP}
    for h in HIDDEN_SWORDS:
        if isinstance(h['skill']['cost'],int): assert _mp[h['id']]==h['skill']['cost'],h['id']
    for k in DEMON_KING['skills']: assert _mp[k['id']]==k['cost'],k['id']
    sc=enemy_scale(); assert all(b['hp_mult']>=a['hp_mult'] for a,b in zip(sc,sc[1:])),[s['hp_mult'] for s in sc]
    p=pacing(towns) if towns else []
    for r in p: assert 40<=r['mob_kills']<=260,r
    warn=[]
    if template and os.path.exists(template):   # 데모 스킬 표와 MP 표 교차 확인 (데모는 다른 작업자가 고치므로 경고만)
        src=open(template,encoding='utf-8').read()
        for m in re.finditer(r"\{id:'(\w+)',\s*name:'([^']+)'[^}]*?cost:(\d+)",src):
            row=[s for s in SKILL_MP if s[1]==m.group(1)]
            if not row: warn.append(f"데모 스킬 {m.group(1)} 이(가) SKILL_MP에 없음")
            elif row[0][3]!=int(m.group(3))*MP['legacy_unit']: warn.append(f"{m.group(1)}: 데모 cost {m.group(3)}칸 ≠ MP {row[0][3]}")
    return warn
def town_quest_exp_total(towns,town):
    t=[x for x in towns if x['id']==town][0]; return sum(quest_exp(q,town) for q in t['quests'] if q['path']!='evil')
def pacing(towns):
    """지역별로 진입→보스 레벨까지 필요한 EXP 중 보스·챔피언 첫 격파·선의 퀘스트를 빼고 남는 양을 일반 몹 몇 마리로 채우는지."""
    share={a:0 for a in range(1,11)}
    for t,v in TOWN_LEVELS.items():
        e=town_quest_exp_total(towns,t)
        for a in v['areas']: share[a]+=e/len(v['areas'])
    out=[]
    for r in MONSTER_EXP:
        a=r['area']; lo,hi=r['levels']; need=total_exp(hi)-total_exp(lo)
        champs=sum(c['exp'] for c in r['champions'])*(2 if a<10 else 6)   # 각 챔피언 2회(보스 문 여는 첫 격파 + 재료 파밍 1회), 10지역은 강화 챔피언 6회
        strong=sum(strongman_exp(t) for t in TOWN_LEVELS if strongman_area(t)==a)
        rest=need-r['boss']['exp']-champs-share[a]-strong
        avg=sum(m['exp'] for m in r['mobs'])/len(r['mobs'])
        out.append(dict(area=a,need=need,boss=r['boss']['exp'],champions=champs,quests=int(share[a]),strongmen=strong,mob_kills=max(0,int(math.ceil(rest/avg)))))
    return out

# ================================================================ 내보내기
def export(towns):
    return dict(version=1,note='레벨·EXP·능력치·MP 설계 데이터 (게임 미연결). 원본: tools/design/level_data.py → gen_docs.py.',
     level_cap=LEVEL_CAP,exp_curve=EXP_CURVE,exp_table=EXP_TABLE,area_levels={str(k):list(v) for k,v in AREA_LEVELS.items()},postgame=dict(POSTGAME,levels=list(POSTGAME['levels'])),
     town_levels=TOWN_LEVELS,monster_exp=MONSTER_EXP,strongman_exp={t:strongman_exp(t) for t in TOWN_LEVELS},asran_exp=ASRAN_EXP,
     level_diff=dict(table=[dict(max_diff=a,mult=b,desc=c) for a,b,c in LEVEL_DIFF_SCALE],rules=LEVEL_DIFF_RULES,boss_floor=0.5),
     growth=dict(choice=GROWTH_CHOICE,stats=GROWTH,table=[dict(level=L,**{k:stat_at(k,L) for k in GROWTH}) for L in range(1,LEVEL_CAP+1)]),
     stat_points=STAT_POINTS,perks=PERKS,demon_perk_swap=DEMON_PERK_SWAP,karma=KARMA_EXP,demon_growth=DEMON_GROWTH,
     companion_level=COMPANION_LEVEL,quest_exp=dict(type_mult=QUEST_TYPE_MULT,level_offset=QUEST_LEVEL_OFFSET,rules=QUEST_RULES,
        by_quest={q['id']:quest_exp(q,t['id']) for t in towns for q in t['quests']}),
     enemy_scale=dict(rule=SCALE_RULE,areas=enemy_scale()),death=DEATH,
     mp=dict(MP,skills=[dict(group=g,id=i,name=n,mp=c,cooldown=cd,note=no) for g,i,n,c,cd,no in SKILL_MP],cost_rules=SKILL_COST_RULES,demon=DEMON_MP,companion=COMPANION_MP),
     roll=ROLL,ult_gauge=ULT_GAUGE,pacing=pacing(towns))

def doc_lines(towns,heroines,town_names):
    L=['# 레벨 · 경험치 · 능력치 · MP 설계','','> 데이터: `tools/design/level_data.py` → `data/levels.json` (단독 파일) + `data/towns.json` → `levels`, `towns[].quests[].exp`. 생성·검증: `tools/design/gen_docs.py`. (설계 문서 — 아직 게임 미구현)',
       '> 숫자는 모두 공식에서 계산된다. 곡선·배율 상수만 고치고 생성기를 다시 돌리면 아래 표가 함께 바뀐다.','',
       '## 한눈에 보기','',f"- **레벨 상한**: {LEVEL_CAP}. 본편 엔딩 ≈ Lv55~58, Lv60은 엔드게임({POSTGAME['name']}).",f"- **곡선**: {EXP_CURVE['formula']}. 총 EXP {total_exp(LEVEL_CAP):,}.",
       f"- **성장**: {GROWTH_CHOICE.split('.')[0]}.",'- **보상**: 5레벨마다 작은 보상, 10레벨마다 큰 보상(4타·5타 콤보, 회피 반격, 필살기 충전, 퍼펙트 회피 판정).',
       '- **MP**: 기존 「파란 게이지·기력」을 MP로 통합 (Lv1 80 = 8칸). 자연 회복은 느리고, 일반 공격 적중·퍼펙트 회피로 채운다. 필살기 게이지와는 별개.',
       f"- **회피**: {ROLL['choice']}.",'- **선악**: 영웅 = 퀘스트 EXP↑, 타락한 필멸자 = 처치 EXP↑, 마왕 = 사람을 죽여 EXP·MP를 얻고 HP·공격 위주로 다르게 성장.','',
       '## 1. 경험치 곡선','',EXP_CURVE['why'],'','| Lv | 다음까지 | 누적 | Lv | 다음까지 | 누적 | Lv | 다음까지 | 누적 |','|---|---|---|---|---|---|---|---|---|']
    for i in range(20):
        row=[EXP_TABLE[i+k*20] for k in range(3)]
        L.append('| '+' | '.join(f"{r['level']} | {r['next'] or '—'} | {r['total']:,}" for r in row)+' |')
    L+=['','## 2. 지역별 권장 레벨과 몬스터 EXP','',f"일반 몹 기준 EXP = (지역 중간 레벨의 다음 레벨 EXP) ÷ {KILLS_PER_LEVEL}, 몹별 가중치 곱. 챔피언 = 기준 × {CHAMPION_MULT}. 보스 = 보스 권장 레벨의 다음 레벨 EXP × {BOSS_LEVEL_SHARE} (10지역 마룡 × {FINAL_BOSS_SHARE}). 몹 레벨은 지역 범위 안에서 출현 순서대로 오른다.",'',
        '| 지역 | 권장 Lv | 일반 몹 기준 | 챔피언 | 보스 |','|---|---|---|---|---|']
    for r in MONSTER_EXP:
        L.append(f"| {r['area']} {r['name']} | {r['levels'][0]}~{r['levels'][1]} | {r['base_exp']} | "+', '.join(f"{c['name']} {c['exp']}" for c in r['champions'])+f" | {r['boss']['name']} (Lv{r['boss']['level']}) {r['boss']['exp']:,} |")
    L+=['',f"엔드게임: {POSTGAME['note']} 아스란 EXP {ASRAN_EXP:,}.",'','### 몹별 EXP','']
    for r in MONSTER_EXP:
        L.append(f"- **{r['area']}지역**: "+', '.join(f"{m['name']} Lv{m['level']} {m['exp']}" for m in r['mobs']))
    L+=['','### 마을 강자 (결투) EXP','','살려 줘도 죽여도 같은 EXP. 기준 = (마을 레벨 + 4)의 다음 레벨 EXP × '+str(STRONGMAN_SHARE)+'.','','| 마을 | 기준 Lv | 강자 EXP |','|---|---|---|']
    L+=[f"| {t} {town_names[t]} | {v['level']} | {strongman_exp(t):,} |" for t,v in TOWN_LEVELS.items()]
    L+=['','### 진행 속도 점검 (생성기가 검사)','','진입 레벨 → 보스 레벨까지 필요한 EXP에서 보스·챔피언(2회씩)·선의 퀘스트·마을 강자 몫을 빼고 남은 양을 일반 몹 처치 수로 환산. 40~260 사이여야 통과.','',
        '| 지역 | 필요 EXP | 보스 | 챔피언 | 퀘스트 | 강자 | 일반 몹 처치 수 |','|---|---|---|---|---|---|---|']
    L+=[f"| {p['area']} | {p['need']:,} | {p['boss']:,} | {p['champions']:,} | {p['quests']:,} | {p['strongmen']:,} | 약 {p['mob_kills']} |" for p in pacing(towns)]
    L+=['','## 3. 레벨 차이 보정 (파밍 방지)','','diff = 주인공 레벨 − 몹 레벨.','','| diff | 배율 | 설명 |','|---|---|---|']
    prev=None
    for mx,m,d in LEVEL_DIFF_SCALE:
        rng=f"≤ {mx}" if prev is None else (f"{prev+1} ~ {mx}" if mx<99 else f"≥ {prev+1}"); prev=mx
        L.append(f"| {rng} | ×{m} | {d} |")
    L+=['']+[f"- {x}" for x in LEVEL_DIFF_RULES]
    L+=['','## 4. 능력치 성장','',GROWTH_CHOICE,'','| 능력치 | Lv1 | 레벨당 증가 | Lv10 | Lv30 | Lv60 | 메모 |','|---|---|---|---|---|---|---|']
    for k,g in GROWTH.items():
        L.append(f"| {g['name']} | {g['base']}{g['unit']} | "+' / '.join(f"Lv{a}~{b} +{i}" for a,b,i in g['steps'])+f" | {stat_at(k,10)} | {stat_at(k,30)} | {stat_at(k,60)} | {g['note']} |")
    sp=STAT_POINTS
    L+=['',f"### 분배 포인트 (레벨당 {sp['per_level']}, 총 {sp['total']}, 한 능력치 최대 {sp['cap_per_stat']})",'','| 능력치 | 1포인트 효과 |','|---|---|']+[f"| {s['name']} | {s['effect']} |" for s in sp['stats']]+['',f"- {sp['why']}",f"- {sp['respec']}",
        '','### 레벨별 고정 능력치 (분배 포인트·장비 제외)','','| Lv | HP | ATK | DEF | MAG | MP | 치명 % |','|---|---|---|---|---|---|---|']
    for Lv in [1,5,10,15,20,25,30,35,40,45,50,55,60]:
        L.append(f"| {Lv} | {stat_at('hp',Lv)} | {stat_at('atk',Lv)} | {stat_at('def',Lv)} | {stat_at('mag',Lv)} | {stat_at('mp',Lv)} | {stat_at('crit',Lv)} |")
    L+=['','## 5. 레벨 보상 (5레벨마다 · 10레벨마다 큰 보상)','','| Lv | 구분 | 보상 | 내용 | 마왕 강림 후 |','|---|---|---|---|---|']
    L+=[f"| {p['level']} | {'**큰 보상**' if p['major'] else '작은 보상'} | {p['name']} | {p['desc']} | {DEMON_PERK_SWAP.get(p['id'],'그대로')} |" for p in PERKS]
    dg=DEMON_GROWTH
    L+=['','## 6. 선악 칭호 · 마왕 루트','','| 칭호 | 조건 | EXP | 성장 | 마을 사람 처치 |','|---|---|---|---|---|']+[f"| {k['title']} | {k['cond']} | {k['exp']} | {k['growth']} | {k['npc_kill']} |" for k in KARMA_EXP]
    L+=['','### 마왕 성장',f"- {dg['rule']}",'- 레벨당 증가량 배율: '+', '.join(f"{GROWTH[k]['name']} ×{v}" for k,v in dg['mult'].items()),f"- {dg['descent_bonus']}",f"- {dg['points']}",f"- 마을 사람 EXP: {dg['townsfolk_exp']}",f"- 구조물: {dg['structure_exp']}",f"- {dg['lock_note']}",
        '','예: Lv30에 강림해 Lv50이 되면 — 일반 성장 HP '+str(stat_at('hp',50))+' / ATK '+str(stat_at('atk',50))+' / MP '+str(stat_at('mp',50))+', 마왕 성장 HP '+str(stat_at('hp',50,'demon',30))+' / ATK '+str(stat_at('atk',50,'demon',30))+' / MP '+str(stat_at('mp',50,'demon',30))+'.']
    cl=COMPANION_LEVEL
    L+=['','## 7. 동료 히로인 레벨','',f"- {cl['rule']}",'- 호감도 보정: '+', '.join(f"{a}~{b} → {o:+d}" if a!=b else f"{a} → {o:+d}" for a,b,o in cl['affinity_offset']),f"- {cl['hero_title_bonus']}",f"- {cl['stats']}",f"- {cl['affinity_stat']}",f"- {cl['down']}",f"- {cl['demon']}",'',
        '| 히로인 | 데이터 HP | 주인공 Lv30 · 호감도 40일 때 | Lv30 · 호감도 100 | 고유 스킬 MP |','|---|---|---|---|---|']
    for h in heroines:
        cd=re.search(r'쿨\s*(\d+)',h['skill']['desc']); cdv=int(cd.group(1)) if cd else 12; mpc=int(round(cdv*2.5/5)*5)
        hp=lambda lv,aff: round(h['hp']/50*stat_at('hp',companion_level(30,aff))*0.8*(1+aff/1000))
        L.append(f"| {h['name']} | {h['hp']} | Lv{companion_level(30,40)} · HP {hp(30,40)} | Lv{companion_level(30,100)} · HP {hp(30,100)} | 「{h['skill']['name']}」 {mpc} (쿨 {cdv}초) |")
    L+=['','## 8. 퀘스트 EXP','','퀘스트 EXP = 다음 레벨 EXP(마을 기준 레벨 + 보정) × 종류 배율 (10 단위).','','| 종류 | 배율 | 기준 Lv 보정 |','|---|---|---|']+[f"| {k} | ×{v} | +{QUEST_LEVEL_OFFSET.get(k,0)} |" for k,v in QUEST_TYPE_MULT.items()]
    L+=['']+[f"- {x}" for x in QUEST_RULES]+['','| 마을 | 기준 Lv | 퀘스트별 EXP |','|---|---|---|']
    for t in towns:
        L.append(f"| {t['id']} {t['name']} | {TOWN_LEVELS[t['id']]['level']} | "+', '.join(f"{q['id']} {quest_exp(q,t['id'])}" for q in t['quests'])+' |')
    L+=['','## 9. 적 스케일 계약','',SCALE_RULE,'','| 지역 | 권장 주인공 (Lv · 공격 · 방어 · HP) | 예상 무기 (강화) | 적 체력 배율 | 적 피해 배율 |','|---|---|---|---|---|']
    for s in enemy_scale():
        h=s['hero']; L.append(f"| {s['area']} | Lv{h['level']} · {h['attack']} · {h['defense']} · {h['hp']} | {h['weapon']} (+{h['enh']}) | ×{s['hp_mult']} | ×{s['dmg_mult']} |")
    L+=['','## 10. 사망 페널티','',f"**{DEATH['choice']}** — {DEATH['why']}",'']+[f"- {x}" for x in DEATH['rules']]
    L+=['','## 11. MP (구 「파란 게이지 · 기력」)','',f"- **통합**: {MP['rename']}",f"- **최대 MP**: {MP['max']}",f"- **필살기 게이지와의 관계**: {MP['ult_separate']}",'','### 회복 (Ys VIII 방식)','','| 방법 | 수치 |','|---|---|']+[f"| {r['name']} | {r['value']} |" for r in MP['regen']]
    L+=['','### MP 아이템 · 장비','','| ID | 이름 | 효과 (MP 기준) |','|---|---|---|']+[f"| `{i}` | {n} | {e} |" for i,n,e in MP['items']+MP['gear']]
    L+=['','### 휴식','']+[f"- {x}" for x in MP['rest']]
    L+=['','### 스킬별 MP 소모','','| 분류 | ID | 스킬 | MP | 재사용 | 비고 |','|---|---|---|---|---|---|']+[f"| {g} | `{i}` | {n} | {c} | {cd}초 | {no} |" for g,i,n,c,cd,no in SKILL_MP]
    L+=['']+[f"- {x}" for x in SKILL_COST_RULES]
    L+=['','### 마왕의 MP',f"- {DEMON_MP['rule']} {DEMON_MP['max']}",'','| 행동 | MP |','|---|---|']+[f"| {a} | {b} |" for a,b in DEMON_MP['drain']]+['',f"- {DEMON_MP['items']}"]
    L+=['','### 히로인의 MP',f"- {COMPANION_MP['rule']}",f"- {COMPANION_MP['ai']}",f"- {COMPANION_MP['duo']}",f"- {COMPANION_MP['potion']}"]
    L+=['','## 12. 회피 구르기 (스태미나 여부)','',f"**{ROLL['choice']}** — {ROLL['why']}",'']+[f"- {x}" for x in ROLL['rules']]
    u=ULT_GAUGE
    L+=['','## 13. 필살기 게이지 (MP와 별개)','',f"범위 {u['range'][0]}~{u['range'][1]}.",'','| 행동 | 게이지 |','|---|---|']+[f"| {a} | {b} |" for a,b in u['gain']]+['',f"- {u['use']}",f"- {u['keep']}"]
    L+=['','## 게임 연결 메모','','- `data/levels.json`을 읽어 `exp_table[L-1].next`, `growth.table[L-1]`, `monster_exp`, `quest_exp.by_quest[퀘스트id]`, `mp`, `roll`, `ult_gauge`를 그대로 쓴다.',
        '- 데모(`town/tools/game.template.html`)의 `SKILLS[].cost`(칸)는 MP ÷ 10으로 맞춰 두었다. 데모의 `gauge`(0~1) = MP ÷ 최대 MP, 「기력 부족」 = 「MP 부족」. 데모 코드는 이번 작업에서 고치지 않았다.',
        '- 저장 필드 제안: `level`, `exp`, `stat_points{str,vit,spi}`, `mp`, `ult_gauge`, `perks_seen[]`, `demon_descent_level`.']
    return L
