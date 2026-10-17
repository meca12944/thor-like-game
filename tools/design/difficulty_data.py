# -*- coding: utf-8 -*-
# 난이도 · 전투 밸런스 목표 (기본 = 「보통」 = Ys VIII 보통~어려움 체감). level_data.py 의 예상 주인공 능력치에서 지역별 적 수치를 계산한다.
# gen_docs.py: validate() → data/levels.json(difficulty) + LEVELS.md(난이도 장) + town/BALANCE_TODO.md(엔진에 넣을 정확한 값).
# 고치는 곳: TARGETS(보통 기준 목표), DIFFICULTIES(난이도 배율), BEHAVIOR(행동 파라미터), RESOURCES(물약·MP).
import os, re
import level_data as LV

# ================================================================ 1. 보통(Normal) 기준 목표 — 「적정 레벨 주인공」 기준
# pct = 한 대 맞았을 때 최대 HP 대비 % (방어 적용 후). hits = 주인공 일반 공격 몇 타에 죽는지.
TARGETS=dict(
 mob_dmg_pct=dict(range=(8,12),center=10,desc='일반 몹 한 대'),
 champ_dmg_pct=dict(range=(15,20),center=17.5,desc='챔피언 한 대'),
 boss_dmg_pct=dict(range=(18,25),center=21.5,desc='보스 일반 패턴 한 대'),
 boss_ult_pct=dict(range=(45,60),center=52,desc='보스 필살기 (가득 찬 HP에서 한 번은 버팀, 구르기 실패를 크게 벌함)'),
 mob_hits=dict(range=(4,6),center=5,desc='일반 몹 처치 타수 (1콤보로 안 죽음)'),
 champ_hits=dict(range=(25,40),center=32,desc='챔피언 처치 타수'),
 boss_seconds=dict(range=(150,240),center=190,desc='숙련자 보스전 시간 (초)'),
)
MOTION_AVG=(1.0+1.0+1.4)/3      # 3타 콤보 평균 배율 (level_data GROWTH['atk'] 메모와 같음)
SKILLED_HITS_PER_SEC=0.9        # 숙련자가 보스전에서 실제로 꽂는 일반 공격 수/초 (패턴 회피·이동 포함 평균, 스킬 피해는 일반 타 환산)
BOSS_PHASE_INVULN=4.0           # 등장·2페이즈 전환 무적 연출 합계(초) — 시간 계산에 더함
# 몹별 편차: HP는 EXP 가중치(단단한 몹 = EXP 많음)를 그대로, 피해는 아래 표 (기본 1.0). 목표 범위 안에 들어와야 한다.
HP_WEIGHT_CLAMP=(0.8,1.2)
DMG_WEIGHT={'멧돼지':1.15,'상어 돌격병':1.15,'용암 바위 골렘':1.15,'그림자 암살자':1.15,'박쥐':0.85,'스카라베 떼':0.85,'해파리':0.9,'갈매기':0.85}
def hit_dmg(a): return LV.expected_hero(a)['attack']*MOTION_AVG
def mitig(a): return 60/(60+LV.expected_hero(a)['defense'])
def raw_for_pct(a,pct): return pct/100*LV.expected_hero(a)['hp']/mitig(a)
def hp_w(name): return min(max(LV.MOB_EXP_WEIGHT.get(name,1.0),HP_WEIGHT_CLAMP[0]),HP_WEIGHT_CLAMP[1])
def area_enemies(a):
    """보통 난이도, 적정 레벨 기준 실제 적 수치 (방어 적용 전 원래 피해)."""
    h=LV.expected_hero(a); hd=hit_dmg(a); T=TARGETS
    boss_hits=(T['boss_seconds']['center']-BOSS_PHASE_INVULN)*SKILLED_HITS_PER_SEC
    r=LV.MONSTER_EXP[a-1]
    mobs=[dict(name=m['name'],hp=round(T['mob_hits']['center']*hd*hp_w(m['name'])),dmg=round(raw_for_pct(a,T['mob_dmg_pct']['center']*DMG_WEIGHT.get(m['name'],1.0)),1)) for m in r['mobs']]
    return dict(area=a,hero=h,hit_dmg=round(hd,1),mitigation=round(mitig(a),3),mobs=mobs,
      mob_hp=round(T['mob_hits']['center']*hd),mob_dmg=round(raw_for_pct(a,T['mob_dmg_pct']['center']),1),
      champ_hp=round(T['champ_hits']['center']*hd),champ_dmg=round(raw_for_pct(a,T['champ_dmg_pct']['center']),1),
      boss_hp=round(boss_hits*hd),boss_dmg=round(raw_for_pct(a,T['boss_dmg_pct']['center']),1),boss_ult_pct=T['boss_ult_pct']['center'],
      boss_ult_dmg=round(raw_for_pct(a,T['boss_ult_pct']['center']),1))
def check_area(e):
    """적정 레벨 주인공이 실제로 받는 %·타수 (검증·문서용)."""
    a=e['area']; h=e['hero']; m=e['mitigation']; hd=e['hit_dmg']
    pct=lambda raw: raw*m/h['hp']*100
    return dict(mob_dmg_pct=[round(pct(x['dmg']),1) for x in e['mobs']],champ_dmg_pct=round(pct(e['champ_dmg']),1),boss_dmg_pct=round(pct(e['boss_dmg']),1),
      boss_ult_pct=round(pct(e['boss_ult_dmg']),1),mob_hits=[round(x['hp']/hd,1) for x in e['mobs']],champ_hits=round(e['champ_hp']/hd,1),
      boss_seconds=round(e['boss_hp']/hd/SKILLED_HITS_PER_SEC+BOSS_PHASE_INVULN))

# ================================================================ 2. 레벨 우위 상한 (과도한 레벨업으로 쉬워지지 않게)
LEVEL_ADVANTAGE_RULE=('유효 레벨 우위 상한: 주인공 레벨이 그 지역 보스 권장 레벨 + 상한(난이도별)보다 높으면, 전투 계산에서는 「권장 + 상한」 레벨의 주인공으로 본다. '
  '구현: 적 HP × (실제 공격력 ÷ 상한 레벨 예상 공격력), 적 피해 × (실제 최대 HP ÷ 상한 레벨 예상 최대 HP). 장비·강화·분배 포인트로 얻은 우위는 그대로 남는다(레벨 숫자만 묶음). '
  'EXP는 기존 레벨 차이 보정을 그대로 쓴다. 레벨이 낮은 쪽은 묶지 않는다 (불리함은 그대로).')

# ================================================================ 3. 적 행동 파라미터 (보통 기준, 엔진 world_mobs.js 대비)
BEHAVIOR=dict(
 telegraph=dict(mult=0.85,floor_attack=0.45,floor_aoe=0.60,floor_charge_line=0.45,ult_min=2.2,
   desc='예고 시간 = 현재 엔진 값 × 0.85, 단 하한 아래로는 줄이지 않는다 (근접·사격 0.45초, 바닥 광역 0.60초, 돌진 예고선 0.45초, 필살기 2.2초). 모든 공격은 여전히 구르기로 피할 수 있다.'),
 approach=dict(speed_mult=1.25,aggro_radius_mult=1.3,attack_cd_mult=0.8,
   desc='접근 속도 ×1.25, 인식 거리 ×1.3, 공격 재사용 ×0.8. 주인공이 멀리 도망가도 쉽게 포기하지 않는다(추격 시간 +50%).'),
 tokens=dict(normal=2,token_cd=0.6,
   desc='공격 토큰: 동시에 공격 동작에 들어갈 수 있는 적 수. 토큰이 없는 적은 주인공 주변 70~110px를 돌며 자리를 잡고(측면·후방 우선), 토큰이 반납되면 0.6초 뒤 다음 적이 받는다. 원거리 몹은 토큰 1개를 따로 쓴다 (근접 2 + 원거리 1).'),
 champions=dict(extra_patterns=1,enrage_at=0.4,enrage_speed=1.2,
   desc='챔피언은 패턴 1개 추가 + HP 40% 이하 분노(행동 속도 ×1.2, 예고는 하한 유지). 추가 패턴은 마지막 동작 뒤 1.2초 빈틈을 반드시 둔다.'),
 bosses=dict(pattern_gap=(0.7,1.1),phase2_tele_mult=0.85,ult_cd=24,
   desc='보스 패턴 사이 빈틈 0.7~1.1초(2페이즈 0.55~0.9), 2페이즈 예고 ×0.85(하한 유지), 필살기 재사용 24초.'),
 recovery='모든 적 공격은 끝난 뒤 최소 0.4초 경직(반격 기회). 보스 일반 패턴은 0.8초 이상.',
)
CHAMPION_EXTRA={  # 1지역은 엔진에 이미 있는 챔피언이라 구체적으로. 나머지는 같은 규칙으로 각 챔피언의 대표 공격을 변형해 만든다.
 "거대 왕멧돼지 '돌엄니'":'「땅울림 3연 돌진」: 예고선 0.55초 → 돌진, 벽에 부딪히면 바로 재조준 2회 (각 0.45초 예고), 마지막에 원형 충격파(0.7초 예고)',
 '여왕 말벌':'「독침 부채꼴」: 5갈래 예고선 0.6초 → 독침 5발, 0.5초 뒤 반대 각도로 한 번 더 (2회째는 HP 40% 이하에서만)',
}

# ================================================================ 4. 자원 (물약·MP) — 보통 기준
RESOURCES=dict(
 potion_cap=dict(normal=5,desc='HP 회복 물약은 종류 합쳐서 최대 5개만 들고 다닌다 (초과분은 마을 창고). 만능 영약은 별도 1개.'),
 potion_heal=dict(potion=30,potion_m=50,potion_hi=100,desc='회복량을 최대 HP 비율로 바꾼다: 회복약 30% / 중급 50% / 고급 100% (구 「하트 2·4칸·전부」는 후반에 무의미해지므로).'),
 potion_use=dict(anim=0.6,cooldown=4.0,desc='사용 모션 0.6초(이동 가능, 공격·구르기 불가, 맞으면 취소되지만 소모 안 됨), 재사용 4초.'),
 price_mult=dict(normal=1.5,desc='HP·MP 물약 가격 ×1.5 (towns_data 기준가 대비). 장비·재료 가격은 그대로.'),
 heart_drop=dict(normal=0.04,desc='몹이 떨어뜨리는 회복 하트: 4% 확률, 하트 1개 = 최대 HP 5%.'),
 mp=dict(passive=0.25,idle_mult=6,hit=3,finisher=5,aggro_bonus=[(10,1),(30,2)],perfect=20,kill=1,
   desc='MP 자연 회복 0.25/초(전투 중), 적이 없으면 ×6. 일반 공격 적중 +3(마무리 +5), 콤보 카운터 10히트 이상 +1·30히트 이상 +2(공격성 보상, 맞으면 콤보 초기화). 퍼펙트 회피 +20. 처치 +1.'),
)

# ================================================================ 5. 난이도
DIFFICULTIES=[
 dict(id='easy',name='쉬움 (이야기)',unlock='처음부터',enemy_hp=0.75,enemy_dmg=0.6,telegraph=1.3,aggression=0.8,tokens=1,champ_extra=0,
      potion_cap=10,price=1.0,mp_regen=1.5,perfect_ticks=10,iframe_bonus=0.06,level_adv_cap=99,exp=1.0,drop=1.0,ult_cap=0.5,
      note='이야기를 보고 싶은 사람용. 패턴은 같지만 예고가 길고 덜 아프다. 레벨 우위 상한 없음.'),
 dict(id='normal',name='보통',unlock='처음부터 (기본값)',enemy_hp=1.0,enemy_dmg=1.0,telegraph=1.0,aggression=1.0,tokens=2,champ_extra=1,
      potion_cap=5,price=1.5,mp_regen=1.0,perfect_ticks=7,iframe_bonus=0.0,level_adv_cap=5,exp=1.0,drop=1.0,ult_cap=0.9,
      note='기준 난이도 = Ys VIII 보통~어려움. 위 목표 범위 그대로.'),
 dict(id='hard',name='어려움',unlock='처음부터',enemy_hp=1.25,enemy_dmg=1.3,telegraph=0.85,aggression=1.2,tokens=3,champ_extra=1,
      potion_cap=3,price=2.0,mp_regen=0.8,perfect_ticks=6,iframe_bonus=-0.02,level_adv_cap=3,exp=1.15,drop=1.15,ult_cap=0.9,
      note='토큰 3, 물약 3개. 필살기는 여전히 가득 찬 HP에서 한 번 버틴다(최대 90%).'),
 dict(id='nightmare',name='악몽',unlock='아무 난이도로 엔딩을 한 번 본 뒤',enemy_hp=1.4,enemy_dmg=1.6,telegraph=0.7,aggression=1.35,tokens=3,champ_extra=2,
      potion_cap=3,price=2.5,mp_regen=0.0,perfect_ticks=4,iframe_bonus=-0.03,level_adv_cap=0,exp=1.3,drop=1.5,ult_cap=0.95,
      note='레벨 완전 동기화(우위 상한 0), 자연 MP 회복 없음(공격·퍼펙트 회피로만), 퍼펙트 회피 판정 4틱(0.067초), 예고 ×0.7(하한은 지킴). 필살기 95% — 가득 찬 HP에서만 버틴다.'),
]
TELEGRAPH_FLOOR_ABS=0.33   # 어떤 난이도에서도 이보다 짧은 예고는 없다 (반응 0.25초 + 구르기 시작 프레임)
TICK=1/60

# ================================================================ 검증
def validate():
    errs=[]
    T=TARGETS
    for a in range(1,11):
        e=area_enemies(a); c=check_area(e)
        for k in ['champ_dmg_pct','boss_dmg_pct','boss_ult_pct','champ_hits','boss_seconds']:
            lo,hi=T[k]['range']
            if not lo<=c[k]<=hi: errs.append((a,k,c[k]))
        for k in ['mob_dmg_pct','mob_hits']:
            lo,hi=T[k]['range']
            for v in c[k]:
                if not lo<=v<=hi: errs.append((a,k,v))
    assert not errs,errs
    ids=[d['id'] for d in DIFFICULTIES]; assert ids==['easy','normal','hard','nightmare']
    nm=[d for d in DIFFICULTIES if d['id']=='normal'][0]
    assert all(nm[k]==1.0 for k in ['enemy_hp','enemy_dmg','telegraph','aggression','mp_regen']) and nm['tokens']==BEHAVIOR['tokens']['normal'] and nm['potion_cap']==RESOURCES['potion_cap']['normal']
    for x,y in zip(DIFFICULTIES,DIFFICULTIES[1:]):   # 어려워질수록 단조
        assert y['enemy_hp']>=x['enemy_hp'] and y['enemy_dmg']>=x['enemy_dmg'] and y['telegraph']<=x['telegraph'] and y['potion_cap']<=x['potion_cap'] and y['perfect_ticks']<=x['perfect_ticks'] and y['level_adv_cap']<=x['level_adv_cap']
    B=BEHAVIOR['telegraph']
    for d in DIFFICULTIES:
        # 실제 예고 하한 = max(절대 하한, 보통 하한 × 난이도 배율). 모든 종류가 절대 하한 이상이고, 필살기는 1.6초 이상
        fl=difficulty_floor(d); assert min(fl['attack'],fl['aoe'],fl['charge_line'])>=TELEGRAPH_FLOOR_ABS and fl['ult']>=1.6,(d['id'],fl)
        assert d['telegraph']>=0.6,(d['id'],'예고 배율이 너무 짧음')
        assert d['perfect_ticks']*TICK>=0.06 and d['perfect_ticks']<=12
        assert LV.ROLL['base']['iframes']+d['iframe_bonus']>=0.15,d['id']
        ult=T['boss_ult_pct']['center']*d['enemy_dmg']/100; assert min(ult,d['ult_cap'])<1.0,(d['id'],ult)   # 가득 찬 HP면 필살기 한 번은 버틴다
        mob=T['mob_dmg_pct']['center']*d['enemy_dmg']; assert mob<=20,(d['id'],mob)
    for n in CHAMPION_EXTRA: assert any(n==c[1] for c in LV._CHAMPS),n
    return True
def difficulty_floor(d):
    B=BEHAVIOR['telegraph']; f=lambda x: round(max(TELEGRAPH_FLOOR_ABS,x*min(1.0,d['telegraph'])),2)
    return dict(attack=f(B['floor_attack']),aoe=f(B['floor_aoe']),charge_line=f(B['floor_charge_line']),ult=round(max(1.6,B['ult_min']*min(1.0,d['telegraph'])),2))

def export():
    areas=[]
    for a in range(1,11):
        e=area_enemies(a); c=check_area(e)
        areas.append(dict(area=a,normal=dict((k,v) for k,v in e.items() if k!='hero'),check=c,
          by_difficulty={d['id']:dict(mob_hp_mult=d['enemy_hp'],dmg_mult=d['enemy_dmg'],
              mob_dmg_pct=round(TARGETS['mob_dmg_pct']['center']*d['enemy_dmg'],1),champ_dmg_pct=round(TARGETS['champ_dmg_pct']['center']*d['enemy_dmg'],1),
              boss_dmg_pct=round(TARGETS['boss_dmg_pct']['center']*d['enemy_dmg'],1),boss_ult_pct=round(min(TARGETS['boss_ult_pct']['center']*d['enemy_dmg'],d['ult_cap']*100),1),
              mob_hits=round(TARGETS['mob_hits']['center']*d['enemy_hp'],1)) for d in DIFFICULTIES}))
    return dict(default='normal',targets={k:dict(v,range=list(v['range'])) for k,v in TARGETS.items()},motion_avg=round(MOTION_AVG,3),skilled_hits_per_sec=SKILLED_HITS_PER_SEC,
      level_advantage_rule=LEVEL_ADVANTAGE_RULE,behavior=BEHAVIOR,champion_extra=CHAMPION_EXTRA,resources=RESOURCES,
      levels=[dict(d,telegraph_floor=difficulty_floor(d)) for d in DIFFICULTIES],telegraph_floor_abs=TELEGRAPH_FLOOR_ABS,areas=areas)

def doc_lines():
    T=TARGETS
    L=['','## 14. 난이도와 전투 밸런스 (기본 = 보통 = Ys VIII 보통~어려움)','',
       '> 사용자 방향: 「난이도는 중간 이상, 너무 쉬우면 안 된다」. 아래 목표는 생성기가 10개 지역 모두에서 검사한다 (`difficulty_data.py`).','',
       '### 보통 난이도 목표 (적정 레벨 주인공 기준)','','| 항목 | 목표 범위 | 기준값 |','|---|---|---|']
    L+=[f"| {v['desc']} | {v['range'][0]}~{v['range'][1]}{'' if 'hits' in k or 'seconds' in k else '%'} | {v['center']} |" for k,v in T.items()]
    L+=['',f"- 일반 공격 1타 평균 = 최종 공격력 × {MOTION_AVG:.3f} (3타 콤보 1.0/1.0/1.4). 일반 몹 5타 = 콤보 2번이 조금 안 되는 양.",
        f"- 보스 시간 = 보스 HP ÷ 1타 ÷ {SKILLED_HITS_PER_SEC}타/초 + 무적 연출 {BOSS_PHASE_INVULN}초. 숙련자가 패턴을 피하면서 평균 0.9타/초를 넣는다고 본다.",
        '- 피해는 방어 적용 전 원래 값이다. 받는 피해 = 원래 × 60/(60+DEF).','',
        '### 지역별 실제 적 수치 (보통)','','| 지역 | 1타 피해 | 일반 몹 HP / 피해 | 챔피언 HP / 피해 | 보스 HP / 패턴 / 필살기 | 검사: 몹 % · 타수 | 챔피언 % · 타수 | 보스 % · 필살 % · 시간 |','|---|---|---|---|---|---|---|---|']
    for a in range(1,11):
        e=area_enemies(a); c=check_area(e)
        L.append(f"| {a} | {e['hit_dmg']} | {e['mob_hp']} / {e['mob_dmg']} | {e['champ_hp']} / {e['champ_dmg']} | {e['boss_hp']:,} / {e['boss_dmg']} / {e['boss_ult_dmg']} | "
                 f"{min(c['mob_dmg_pct'])}~{max(c['mob_dmg_pct'])}% · {min(c['mob_hits'])}~{max(c['mob_hits'])}타 | {c['champ_dmg_pct']}% · {c['champ_hits']}타 | {c['boss_dmg_pct']}% · {c['boss_ult_pct']}% · {c['boss_seconds']}초 |")
    L+=['',f"몹별 HP는 EXP 가중치({HP_WEIGHT_CLAMP[0]}~{HP_WEIGHT_CLAMP[1]}로 제한)를, 피해는 일부 몹만 0.85~1.15 편차를 둔다 — 그래도 목표 범위 안. 몹별 값은 `data/levels.json` → `difficulty.areas[].normal.mobs`.",
        '','### 레벨 우위 상한','',LEVEL_ADVANTAGE_RULE,'','### 적 행동 (보통)','']
    L+=[f"- **{n}**: {BEHAVIOR[k]['desc']}" for k,n in [('telegraph','예고'),('approach','공격성'),('tokens','무리 압박'),('champions','챔피언'),('bosses','보스')]]+[f"- **경직**: {BEHAVIOR['recovery']}"]
    L+=['','챔피언 추가 패턴 (1지역):','']+[f"- {k}: {v}" for k,v in CHAMPION_EXTRA.items()]
    L+=['','### 자원 (보통)','']+[f"- {v['desc']}" for v in RESOURCES.values()]
    L+=['','### 난이도 4단계','','| 난이도 | 해금 | 적 HP | 적 피해 | 예고 | 공격성 | 토큰 | 챔피언 추가 패턴 | 물약 휴대 | 물약 가격 | MP 회복 | 퍼펙트 판정 | 무적 보정 | 레벨 우위 상한 | 필살기 상한 | EXP·드롭 |','|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for d in DIFFICULTIES:
        L.append(f"| **{d['name']}** | {d['unlock']} | ×{d['enemy_hp']} | ×{d['enemy_dmg']} | ×{d['telegraph']} | ×{d['aggression']} | {d['tokens']} | +{d['champ_extra']} | {d['potion_cap']} | ×{d['price']} | ×{d['mp_regen']} | {d['perfect_ticks']}틱 ({d['perfect_ticks']*TICK:.3f}초) | {d['iframe_bonus']:+.2f}초 | {('+'+str(d['level_adv_cap'])) if d['level_adv_cap']<99 else '없음'} | {int(d['ult_cap']*100)}% | ×{d['exp']} · ×{d['drop']} |")
    L+=['']+[f"- **{d['name']}**: {d['note']} 예고 하한 {difficulty_floor(d)}" for d in DIFFICULTIES]
    L+=['',f"- 어떤 난이도에서도 예고는 {TELEGRAPH_FLOOR_ABS}초보다 짧지 않다 (반응 0.25초 + 구르기 시작). 모든 공격은 구르기로 피할 수 있다.",
        '- 난이도는 언제든 바꿀 수 있다 (악몽 제외: 악몽은 새 게임 또는 회차에서만, 중간에 내리면 악몽 보상 기록이 사라짐).',
        '- 엔진에 넣을 정확한 값과 현재 엔진 값 비교는 [town/BALANCE_TODO.md](town/BALANCE_TODO.md).']
    return L

# ================================================================ 엔진 대조표 (town/BALANCE_TODO.md)
ENGINE_HIT_UNIT=10   # 엔진 권장: 주인공 1타 = 10 (1지역 기준). 레벨 시스템이 붙으면 이 10을 최종 공격력으로 바꾼다.
ENGINE_HERO_HP=50    # 엔진 권장: 하트 5칸 = HP 50 (1하트 = 10, 반 칸 = 5)
# 엔진 원래 값 (커밋 25dbf5f의 town/world_mobs.js, 하트 단위). 목표 예고·속도는 이 원래 값에서 계산하고, 「현재」 열은 생성 시점 파일에서 읽어 적용 여부(✅/⚠)를 표시한다.
ENGINE_BASE={'mushroom': {'hp': 3, 'warn': ['0.7'], 'line': [], 'speed': []}, 'rabbit': {'hp': 2, 'warn': [], 'line': ['0.55'], 'speed': []}, 'wasp': {'hp': 2, 'warn': [], 'line': ['0.6'], 'speed': ['40']}, 'boar': {'hp': 4, 'warn': [], 'line': ['0.45', '0.65'], 'speed': []}, 'scarecrow': {'hp': 3, 'warn': ['0.55', '0.55'], 'line': [], 'speed': ['18']}, 'slime': {'hp': 2, 'warn': ['0.8'], 'line': [], 'speed': []}, 'squirrel': {'hp': 2, 'warn': ['0.85'], 'line': [], 'speed': ['25']}, 'sprout': {'hp': 3, 'warn': ['0.9'], 'line': [], 'speed': ['14']}, 'champ_boar': {'hp': 16, 'warn': ['0.85'], 'line': ['0.55', '0.7'], 'speed': ['22']}, 'champ_wasp': {'hp': 14, 'warn': ['0.95', '0.6'], 'line': ['0.7'], 'speed': ['40']}, 'golem': {'hp': 44, 'warn': ['0.75', '2.0', '1.0'], 'line': ['0.8', '0.65', '0.45'], 'speed': ['16']}}
def _call_args(src,name):
    out=[]
    for m in re.finditer(re.escape(name)+r'\(',src):
        i=m.end(); depth=1; cur=''; args=[]
        while i<len(src) and depth:
            c=src[i]
            if c in '([{': depth+=1
            elif c in ')]}': depth-=1
            if depth==1 and c==',': args.append(cur.strip()); cur=''
            elif depth: cur+=c
            i+=1
        args.append(cur.strip()); out.append(args)
    return out
def _tele_args(b):   # lineTele(W, m, a, len, warn, width) 의 warn 숫자들 (삼항식이면 숫자 모두)
    vals=[]
    for args in _call_args(b,'lineTele'):
        if len(args)>4 and not args[4].startswith('w'): vals+=re.findall(r'\d*\.\d+|\d+',args[4])
    return vals
def _parse_mobs(src):
    out=[]
    for m in re.finditer(r"^    (\w+): \{ name: '([^']+)'(.*?)(?=^    \w+: \{ name:|^  \};)",src,re.S|re.M):
        k,n,b=m.groups(); g=lambda p: re.findall(p,b)
        out.append(dict(key=k,name=n,champion='champion: true' in b,boss='boss: true' in b,hp=int(re.search(r"hp: (\d+)",b).group(1)),
            warn=g(r"warn: ([\d.]+)"),dmg=sorted(set(g(r"dmg: (\d+)"))-{'0'}),touch=g(r"touch\(m, \d+, (\d+)"),speed=g(r"toward\(m, W, dt, (\d+)"),line=_tele_args(b)))
    return out
def balance_todo(repo):
    town=os.path.join(repo,'town'); L=[]
    def rd(p):
        p=os.path.join(town,p); return open(p,encoding='utf-8').read() if os.path.exists(p) else ''
    wm,wj,tp=rd('world_mobs.js'),rd('world.js'),rd('tools/game.template.html')
    a1=area_enemies(1); h=a1['hero']; unit=ENGINE_HIT_UNIT/a1['hit_dmg']   # 설계값 → 엔진 단위 환산 (1지역 기준 1타 = 10)
    hpu=ENGINE_HERO_HP/h['hp']
    E=lambda raw: max(1,round(raw*a1['mitigation']*hpu))   # 엔진은 방어 계산이 없으므로 방어 적용 후 값을 바로 넣는다
    L+=['# 밸런스 적용 TODO (엔진 담당자용)','','> 자동 생성: `tools/design/gen_docs.py` ← `tools/design/difficulty_data.py`. 설계 목표·근거는 [LEVELS.md](../LEVELS.md) 14장. 이 파일은 엔진 코드를 고치지 않고 「넣어야 할 값」만 적는다 (템플릿·엔진 담당 작업자가 반영).',
        '> 현재 값은 생성 시점의 `town/world_mobs.js`, `town/world.js`, `town/tools/game.template.html`에서 읽었다.','',
        '## 0. 단위 바꾸기 (먼저)','',
        f"- 주인공 HP: 원래 하트 정수 (`hero.hp: 5, maxHp: 5`, 피해 1 = 하트 1칸 = 20%) → **HP {ENGINE_HERO_HP} (1하트 = 10, 반 칸 = 5)**. 하트 20% 단위로는 「일반 몹 8~12%」를 표현할 수 없어서다."+(' ✅ 적용됨 (world.js·템플릿 모두 HP 50, HUD는 연속 HP 바 + 숫자).' if ('hp: 50, maxHp: 50' in wj and 'hp:50,maxHp:50' in tp) else ''),
        f"- 주인공 공격: 원래 `hitMob(mm, a.i === 2 ? 2 : 1)` (1·1·2) → **10 · 10 · 14** (`ATK_DMG=[10,10,14]`). 나중에 레벨 시스템이 붙으면 10 = 최종 공격력."+(' ✅ 적용됨.' if ('ATK_DMG = [10, 10, 14]' in wj and 'ATK_DMG=[10,10,14]' in tp) else ''),
        '- `hurt(dmg)`, `W.touch(m, r, dmg)`, `hazard({dmg})`, `shot({dmg})`의 dmg는 모두 HP 단위로 바꾼다 (아래 표의 값). 필살기 `Math.ceil(hero.maxHp / 2)`는 그대로 50% 비율 유지(목표 45~60%).',
        '- 난이도 배율은 `data/levels.json` → `difficulty.levels[]`의 `enemy_hp`, `enemy_dmg`, `telegraph`, `aggression`, `tokens`를 스폰·hazard 생성 시 곱한다 (예고는 `telegraph_floor` 아래로 내리지 않음).'+(' ✅ 적용됨 (Esc 메뉴 「난이도」, world.js `teleScale()` / `DIFF()`).' if 'teleScale' in wj else ''),'',
        f"## 1. 1지역 몹 (보통, 1지역 적정 레벨 = Lv{h['level']} 기준을 엔진 단위로 환산)",'',
        '| 엔진 키 | 이름 | 원래 HP (하트 단위) | 현재 HP | **목표 HP** | 현재 피해 | **목표 피해 (HP)** | 원래 예고(초) | 현재 예고 | **목표 예고** | 현재 속도 | **목표 속도** | 적용 |','|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    mobs=_parse_mobs(wm); B=BEHAVIOR['telegraph']; sp=BEHAVIOR['approach']['speed_mult']
    a1names={m['name']:m for m in a1['mobs']}
    def tele(ws,floor): return ', '.join(f"{max(floor,round(float(w)*B['mult'],2))}" for w in ws) or '—'
    def tl(ws,floor): return [max(floor,round(float(w)*B['mult'],2)) for w in ws]
    for m in mobs:
        b=ENGINE_BASE.get(m['key'],dict(hp=m['hp'],warn=m['warn'],line=m['line'],speed=m['speed']))
        if m['boss']: tgt_hp=round(a1['boss_hp']*unit); tgt_d=[E(a1['boss_dmg'])]; tgt_dmg=f"패턴 {E(a1['boss_dmg'])} · 접촉 {E(a1['boss_dmg'])} · 필살 maxHp×0.52"
        elif m['champion']: tgt_hp=round(a1['champ_hp']*unit); tgt_d=[E(a1['champ_dmg'])]; tgt_dmg=f"{E(a1['champ_dmg'])} (돌진·장판 공통)"
        else:
            d=a1names.get(m['name']); tgt_hp=round((d['hp'] if d else a1['mob_hp'])*unit); tgt_d=[E(d['dmg'] if d else a1['mob_dmg'])]; tgt_dmg=str(tgt_d[0])
        cur_d=sorted(set(int(x) for x in m['dmg']+m['touch'])); cur_dmg='/'.join(map(str,cur_d)) or '—'
        tw,tln=tl(b['warn'],B['floor_aoe']),tl(b['line'],B['floor_charge_line']); tsp=[round(int(x)*sp) for x in b['speed']]
        cw=[float(x) for x in m['warn']]; cl=[float(x) for x in m['line']]; csp=[int(x) for x in m['speed']]
        okv=m['hp']==tgt_hp and cur_d==tgt_d and sorted(cw)==sorted(tw) and sorted(cl)==sorted(tln) and csp==tsp
        tgt_tele=' / '.join(x for x in [', '.join(map(str,tw)) if tw else '',('선 '+', '.join(map(str,tln))) if tln else ''] if x) or '—'
        cur_tele=' / '.join(x for x in [', '.join(m['warn']) if m['warn'] else '',('선 '+', '.join(m['line'])) if m['line'] else ''] if x) or '—'
        L.append(f"| `{m['key']}` | {m['name']} | {b['hp']} | {m['hp']} | **{tgt_hp}** | {cur_dmg} | **{tgt_dmg}** | {', '.join(b['warn']+b['line']) or '—'} | {cur_tele} | **{tgt_tele}** | {', '.join(m['speed']) or '—'} | **{', '.join(map(str,tsp)) or '—'}** | {'✅' if okv else '⚠'} |")
    L+=['',f"- 슬라임 분열체(`k.hp = k.maxHp = 1`) → **{max(1,round(a1['mob_hp']*unit*0.4))}** (본체의 40%)."+(' ✅ 적용됨.' if 'Math.round(20 *' in wm else ''),
        f"- 골렘 「이끼 재생」은 0.5초마다 +1 → **+{round(a1['boss_hp']*unit*0.01)} (최대 HP 1%)**, 재생 상한 85%/50% 그대로. 경직 중 피해 ×2 그대로."+(' ✅ 적용됨.' if 'm.maxHp * 0.01' in wm else ''),
        f"- 골렘 필살기 예고 `W.ult(m, 2.6)` → **{max(B['ult_min'],round(2.6*B['mult'],2))}초** (하한 {B['ult_min']}초). 패턴 A 링 0.9/1.2/1.5 → **{', '.join(str(max(B['floor_aoe'],round(x*B['mult'],2))) for x in (0.9,1.2,1.5))}**. 2페이즈 k=0.8은 그대로 곱하되 하한 유지."+(' ✅ 적용됨 (하한은 world.js `teleScale()`).' if 'W.ult(m, 2.21)' in wm else ''),
        '- 챔피언 추가 패턴 (보통 +1): '+' / '.join(f"{k}: {v}" for k,v in CHAMPION_EXTRA.items())+(' ✅ 적용됨.' if 'champExtra' in wm else ' ⏳ 아직 미구현 (새 공격 동작 · 아트 필요 — 수치 밸런스와 별도 작업).'),
        f"- 챔피언 분노: HP {int(BEHAVIOR['champions']['enrage_at']*100)}% 이하 행동 속도 ×{BEHAVIOR['champions']['enrage_speed']}"+(' ✅ 적용됨 (돌엄니 40%).' if 'm.maxHp * 0.4' in wm else ' (현재 돌엄니는 50%에서 분노 → 40%로).'),
        f"- 공격 토큰: 동시에 공격하는 몹 최대 {BEHAVIOR['tokens']['normal']} (+원거리 1), 반납 후 {BEHAVIOR['tokens']['token_cd']}초. "+(' ✅ 적용됨 (world.js `token()` / `S.tokens`).' if 'S.tokens' in wj else ' 현재 엔진은 제한 없음 → `S.tokens` 카운터 추가 필요.'),
        f"- 공격 재사용(`m.cd`) ×{BEHAVIOR['approach']['attack_cd_mult']}, 인식 거리 ×{BEHAVIOR['approach']['aggro_radius_mult']}. 모든 공격 뒤 최소 0.4초 경직(보스 0.8초)."+(' ✅ 재사용 · 인식 거리 · 접근 속도 적용 (난이도 `aggression` 도 곱함).' if 'agg(W)' in wm else ''),'',
        '## 2. 주인공 · 구르기 · 회복','','| 위치 | 현재 | **목표 (보통)** | 이유 |','|---|---|---|---|']
    roll=re.search(r"const ROLL = \{([^}]*)\}",wj); feel=re.search(r"dashTicks:(\d+),dashIframes:(\d+),dashCdTicks:(\d+)",tp); pt=re.search(r"perfectTicks:(\d+)",tp)
    pot=re.search(r"hero\.hp \+ (\d+)\); syncTownHp\(\); addFx\('heal'",wj); ult=re.search(r"const ULT_CFG=\{([^}]*)\}",tp); regen=re.search(r"gaugeRegen:([\d.]+)",tp)
    R=LV.ROLL['base']; RS=RESOURCES
    ap=lambda c: ' ✅' if c else ''
    mpr=re.search(r"MPR=\{passive:([\d.]+)",tp)
    L+=[f"| world.js `ROLL` | {roll.group(1).strip() if roll else '?'} | **dur: {R['duration']}, iframe: {R['iframes']}, cd: {R['cooldown']}**{ap(roll and f"iframe: {R['iframes']}" in roll.group(1) and f"cd: {R['cooldown']}" in roll.group(1))} | 무적 0.32초 + 재사용 0.12초는 사실상 무한 무적. Lv15·35 보상으로 +0.03씩 |",
        f"| 템플릿 FEEL dash | dashTicks {feel.group(1) if feel else '?'}, dashIframes {feel.group(2) if feel else '?'}, dashCdTicks {feel.group(3) if feel else '?'} | **dashIframes {round(R['iframes']*60)}, dashCdTicks {round(R['cooldown']*60)}**{ap(feel and int(feel.group(2))==round(R['iframes']*60)-0 or (feel and int(feel.group(2))==11 and int(feel.group(3))==24))} | 같은 규칙 (60Hz 틱) |",
        f"| 템플릿 FEEL perfectTicks | {pt.group(1) if pt else '?'} | **7 (보통) / 10 쉬움 / 6 어려움 / 4 악몽**{ap('perfect_ticks' in tp)} | 난이도표 |",
        f"| world.js 물약 회복 | {('최대 HP '+re.search(r'heal: (\d+)',wj).group(1)+'%') if 'POT.heal' in wj else '+'+(pot.group(1) if pot else '?')+' 하트'} | **최대 HP 30%** (중급 50%, 고급 100%), 사용 모션 {RS['potion_use']['anim']}초, 재사용 {RS['potion_use']['cooldown']}초{ap('POT.heal' in wj and 'cd: 4.0' in wj)}{'' if 'potionAnim' in wj else ' (회복량 · 재사용 적용, 0.6초 사용 모션은 아직 없음)'} | 후반에도 의미 있는 비율 회복 |",
        f"| 물약 휴대 | {'난이도별 상한 (`potion_cap`)' if 'potion_cap' in tp else '제한 없음 (`g.potions`)'} | **최대 {RS['potion_cap']['normal']}개** (쉬움 10 / 어려움·악몽 3){ap('potion_cap' in tp)} | 덜 관대한 자원 |",
        f"| world.js 회복 하트 줍기 | {'최대 HP 5%, 드롭 4%' if 'heartPct: 5' in wj else '+1 하트'} | **최대 HP 5%**, 드롭 {int(RS['heart_drop']['normal']*100)}%{ap('heartPct: 5' in wj)} | |",
        f"| 템플릿 MP 자연 회복 | {('MPR.passive '+mpr.group(1)+' MP/초') if mpr else (regen.group(1) if regen else '?')+' (8칸 기준)'} | **MP 0.25/초** (비전투 ×6) = 80MP 기준 0.0031/틱{ap(mpr and float(mpr.group(1))==RS['mp']['passive'])} | 자연 회복 느리게, 공격·퍼펙트 회피로 채움 |",
        f"| 템플릿 ULT_CFG | {ult.group(1) if ult else '?'} | **적에게 맞으면 차오르고, 저스트 회피에 성공하면 크게 차오름: gainHurt 0.5 (받은 피해 1HP당), gainPerfect 8 (보통 피격 8HP분의 2배). 공격 적중 · 처치 · 보스 페이즈 = 0**{ap(ult and 'gainHurt:.5' in ult.group(1) and 'gainPerfect:8' in ult.group(1) and 'gainDeal' not in ult.group(1))} | LEVELS.md 13장. 조건을 두 가지로 단순화, 어려운 전투 1.5~2번에 1회 |",
        f"| MP 적중 회복 | {'MPR (hit/finisher/combo10/combo30/perfect)' if 'combo30' in tp else '(없음/게이지)'} | **+{RS['mp']['hit']} (마무리 +{RS['mp']['finisher']}), 콤보 10히트↑ +1, 30히트↑ +2, 퍼펙트 회피 +{RS['mp']['perfect']}**{ap('combo30:2' in tp and 'perfect:20' in tp)} | 공격성 보상 |",
        '',f"## 3. 2지역 이후 (엔진 단위, 1타 = 그 지역 최종 공격력)",'','| 지역 | 1타 | 몹 HP | 몹 피해 | 챔피언 HP | 챔피언 피해 | 보스 HP | 보스 패턴 | 필살기 |','|---|---|---|---|---|---|---|---|---|']
    for a in range(1,11):
        e=area_enemies(a); L.append(f"| {a} | {e['hit_dmg']} | {e['mob_hp']} | {e['mob_dmg']} | {e['champ_hp']} | {e['champ_dmg']} | {e['boss_hp']:,} | {e['boss_dmg']} | {e['boss_ult_dmg']} |")
    L+=['','이 표는 레벨 시스템 단위(방어 적용 전 원래 피해)다. 레벨 시스템을 붙이기 전 데모에서는 1장 환산값을 쓰면 된다.']
    return L
