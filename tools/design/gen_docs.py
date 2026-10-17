# -*- coding: utf-8 -*-
# towns_data.py (+ story_data.py) → data/towns.json + TOWNS.md / ITEMS.md / EQUIPMENT.md / SYSTEMS.md / STORY.md / TOWNSFOLK_COMBAT.md
import json, sys, os, shutil
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from towns_data import *
REPO=os.path.abspath(os.path.join(HERE,'..','..'))
COPY_DIRS=['/workspace/town-demo/src/monsters']
EQ={e['id']:e for e in EQUIP_ITEMS}
SLOTN={'weapon':'무기','armor':'방어구(몸)','helmet':'방어구(투구)','offhand':'보조무기'}
KINDN={'shield':'방패','bracer':'팔보호대','amulet':'부적','boots':'장화','throw':'투척무기','orb':'오브','ring':'반지'}
TN={t['id']:t['name'] for t in TOWNS}
EFK=dict(kb='넉백',atk_speed='공격 속도',move='이동 속도',spin='돌려베기 범위',coin='금화',swim='수영 속도',evade='회피',carry='소지',gauge='게이지',intimidate='위압',heat='열사병',stealth='은신')
def cat(e): return 'armor' if e['slot'] in('armor','helmet') else e['slot']
# ---------------- 검증
cnt=Counter(cat(e) for e in EQUIP_ITEMS); cnt['consumable']=len(TOOLS)
assert dict(cnt)==CATALOG_COUNTS,(dict(cnt),CATALOG_COUNTS)
assert len(EQ)==len(EQUIP_ITEMS)
assert not (set(EQ)&set(TOOLS))
for e in EQUIP_ITEMS:
    assert e['visual']['palette'] in PALETTES,e['id']; assert 1<=e['tier']<=10
    if e['source']['type']=='shop': assert e['price'] and e['source']['where'] in TN,e['id']
    else: assert e['price'] is None,e['id']
looks=[e['visual']['look'] for e in EQUIP_ITEMS]; assert len(set(looks))==len(looks)
names=[e['name'] for e in EQUIP_ITEMS]+[d['name'] for d in TOOLS.values()]; assert len(set(names))==len(names),[n for n in names if names.count(n)>1]
for c in ['체력','게이지','치료','버프','영구','이동','잠수','강화']: assert any(d['category']==c for d in TOOLS.values()),c
assert 'charm_guard' in TOOLS and 'charm_luck' in TOOLS
for t in TOWNS:
    ids={n['id'] for n in t['npcs']}; assert len(t['npcs'])==10,t['id']
    assert sorted(n.get('shop') for n in t['npcs'] if n.get('shop'))==['cosmetic','tool','weapon']
    good=[q for q in t['quests'] if q['path']=='good']; evil=[q for q in t['quests'] if q['path']=='evil']
    assert len(good)>=5 and len(evil)>=2
    for qq in t['quests']: assert qq['giver'] in ids|{'strongman'},(t['id'],qq['id'])
    for i,_ in t['shops']['tool']+t['shops']['black']: assert i in TOOLS,i
    for i,_ in t['shops']['weapon']: assert i in EQ,i
    for i,_ in t['shops']['cosmetic']: assert i in COSMETICS,i
    for n in t['npcs']: assert 1<=len(n['combat']['attacks'])<=3,n['id']
    tiers=[EQ[i]['tier'] for i,_ in t['shops']['weapon']]; assert tiers
for s in STRONGMEN: assert len(s['patterns'])==6 and s['ultimate']
assert len(TOWNSFOLK)==80 and len(STRONGMEN)==8
# 마을 순서대로 상점 최고 티어가 줄지 않음
order=['A','B','H','G','F','E','C','D']; mx=[max(EQ[i]['tier'] for i,_ in [t for t in TOWNS if t['id']==o][0]['shops']['weapon']) for o in order]
assert mx==sorted(mx),mx
COUNTS=dict(weapon=cnt['weapon'],armor=cnt['armor'],armor_body=sum(e['slot']=='armor' for e in EQUIP_ITEMS),armor_helmet=sum(e['slot']=='helmet' for e in EQUIP_ITEMS),
            offhand=cnt['offhand'],consumable=cnt['consumable'],shop_equipment=sum(e['source']['type']=='shop' for e in EQUIP_ITEMS),
            rare_equipment=sum(e['source']['type']!='shop' for e in EQUIP_ITEMS),quests=sum(len(t['quests']) for t in TOWNS),
            evil_quests=sum(q['path']=='evil' for t in TOWNS for q in t['quests']),npcs=sum(len(t['npcs']) for t in TOWNS),strongmen=len(STRONGMEN))
# ---------------- JSON
def shopj(t): return {k:[{'item':i,'price':p} for i,p in v] for k,v in t['shops'].items()}
def item_json(e): return {k:v for k,v in e.items()}
data=dict(version=2,note='게임에 아직 연결하지 않은 편집용 데이터. tools/design/towns_data.py(+story_data.py)를 고치고 tools/design/gen_docs.py를 실행하면 이 파일과 모든 설계 문서가 함께 갱신된다.',
 counts=COUNTS,
 towns=[dict({k:v for k,v in t.items() if k!='shops'},shops=shopj(t)) for t in TOWNS],
 catalog=dict(weapons=[item_json(e) for e in EQUIP_ITEMS if cat(e)=='weapon'],armor=[item_json(e) for e in EQUIP_ITEMS if cat(e)=='armor'],
   offhand=[item_json(e) for e in EQUIP_ITEMS if cat(e)=='offhand'],consumables=[dict(id=i,**d) for i,d in TOOLS.items()],cosmetics=COSMETICS),
 equipment=dict(slots=EQUIP_SLOTS,layer_order=['body','eyes_corrupt','veins','boots','armor','helmet','halo/horns','cape','aura','weapon','offhand'],
   cosmetic_rule=COSMETIC_RULE,palettes=PALETTES,corruption_visuals=CORRUPTION_VISUALS),
 travel=dict(rule=TRAVEL_RULE,roads=ROADS),
 enhancement=dict(rules=ENH_RULES,tiers=ENH_TIERS,levels=ENH_LEVELS,champion_drops=CHAMPION_DROPS),
 respawn=RESPAWN,
 story=STORY,karma=KARMA,bounty=BOUNTY,skill_evolution=[dict(skill=a,base=b,light=c,dark=d) for a,b,c,d in SKILL_EVOLUTION],
 strongman_rule=STRONGMAN_RULE,townsfolk_rule=TOWNSFOLK_RULE)
os.makedirs(os.path.join(REPO,'data'),exist_ok=True)
json.dump(data,open(os.path.join(REPO,'data','towns.json'),'w'),ensure_ascii=False,indent=1)
DOCS={}
def stat(e):
    if e['slot']=='weapon': s=f"공격 {e['atk']}"
    elif e['slot']=='offhand':
        s=' · '.join(x for x in [f"방어 {e['defense']}" if e.get('defense') else '',f"공격 {e['atk']}" if e.get('atk') else ''] if x) or '—'
    else: s=f"방어 {e.get('defense',0)}"
    ef=[(EFK.get(k,'')+' '+str(v)).strip() if str(v)[:1] in '+-' else str(v) for k,v in e.get('effect',{}).items() if k!='kind']
    if s=='—' and ef: return ', '.join(ef)
    return s+((' · '+', '.join(ef)) if ef else '')
def src(e):
    s=e['source']; 
    if s['type']=='shop': return f"{s['where']} {TN[s['where']]} 상점 ({e['price']})"
    return f"{SRC_KO[s['type']]}: {s['where']}"+(f" ({s['rate']})" if s.get('rate') else '')
def tsrc(d):
    a=[f"{x['town']} {x['price']}" for x in d['shops']]
    s=('뒷거래 ' if d['black_market'] else '')+(', '.join(a) if a else '비매품')
    return s+(f" / {d['other_source']}" if d.get('other_source') else '')
# ---------------- ITEMS.md
I=['# 아이템 카탈로그','',f"> 데이터: `data/towns.json` → `catalog`. 생성기가 개수를 검사한다 (무기 {COUNTS['weapon']} / 방어구 {COUNTS['armor']} (몸 {COUNTS['armor_body']} + 투구 {COUNTS['armor_helmet']}) / 보조무기 {COUNTS['offhand']} / 소모품 {COUNTS['consumable']}).",
 f"> 장비 {len(EQUIP_ITEMS)}종 중 상점 판매 {COUNTS['shop_equipment']}종, 희귀 드롭(보스·챔피언·퀘스트·잠수) {COUNTS['rare_equipment']}종. 티어 1~10 ≈ 지역 번호. 외형 레이어는 [EQUIPMENT.md](EQUIPMENT.md), 강화는 [SYSTEMS.md](SYSTEMS.md).",'']
for c,title in [('weapon','무기 (30)'),('armor','방어구 (30)'),('offhand','보조무기 (30)')]:
    I+=[f"## {title}",'','| ID | 이름 | 종류 | 티어 | 능력치 | 출처 | 스프라이트 · 팔레트 | 외형 |','|---|---|---|---|---|---|---|---|']
    for e in sorted([e for e in EQUIP_ITEMS if cat(e)==c],key=lambda e:(e['tier'],e['source']['type']!='shop',e['id'])):
        kind=KINDN.get(e.get('effect',{}).get('kind'),'') if c=='offhand' else SLOTN[e['slot']]
        I.append(f"| `{e['id']}` | {e['name']} | {kind} | {e['tier']} | {stat(e)} | {src(e)} | `{e['visual']['sprite']}` · {e['visual']['palette']} | {e['visual']['look']} |")
    I.append('')
I+=['## 소모품 (60)','','가격은 기준가, 출처 칸은 「마을 가격」. 비매품은 드롭·잠수·퀘스트로만 얻는다. 「뒷거래」는 도구상점 주인이 악명·마왕 등급에게만 파는 암시장 물건.','',
    '| ID | 이름 | 분류 | 효과 | 기준가 | 출처 |','|---|---|---|---|---|---|']
for i,d in TOOLS.items(): I.append(f"| `{i}` | {d['name']} | {d['category']} | {d['effect']} | {d['price'] or '—'} | {tsrc(d)} |")
I+=['','> 수호의 부적·행운의 숫돌은 강화용으로 이번에 새로 정의한 소모품이다. 선악 분류의 면죄 증서·참회의 촛불·검은 피의 비약·맹독 병은 선악/현상금 시스템(SYSTEMS.md 3·4장)과 연결된다.']
DOCS['ITEMS.md']=I
# ---------------- TOWNS.md
L=['# 마을 설계서 (8개 마을)','',
 '> 원본 데이터: `data/towns.json` (생성기: `tools/design/towns_data.py` + `story_data.py` → `tools/design/gen_docs.py`). 아이템은 [ITEMS.md](ITEMS.md), 장비 외형은 [EQUIPMENT.md](EQUIPMENT.md), 강화·리스폰·선악·현상금은 [SYSTEMS.md](SYSTEMS.md), 본편 이야기는 [STORY.md](STORY.md), 마을 강자와 마을 사람 전투는 [TOWNSFOLK_COMBAT.md](TOWNSFOLK_COMBAT.md).',
 '> 지도: `world_map_v4.jpg` / 번호판 `maps/world_map_v4_numbered.png` (빨강 1~10 = 지역, 파랑 A~H = 마을; 좌표는 1024 폭 기준).','',
 '## 진행 순서와 마을 도착 시점','','| 순서 | 지역 | 직전 거점 마을 |','|---|---|---|',
 '| 프롤로그 | — | A 시작 마을 |','| 1 | 시작의 숲 | A |','| 2 | 수정 동굴 | B → H (1지역 후) |','| 3 | 모래 사막 | G (2지역 후) |','| 4 | 피라미드 | G |',
 '| 5 | 산호 바다 | F (4지역 후, 배로 출항) |','| 6 | 해안 절벽 | F |','| 7 | 화산 성채 | E (6지역 후) |','| 8 | 설산 뇌전 탑 | C (7지역 후) |','| 9 | 어둠 신전 | D (8지역 후) |','| 10 | 마룡의 둥지 | D |','',
 '공통 규칙',
 '- 마을마다 NPC 10명(그중 3명은 도구상점·무기상점·외형상점 주인)과 별도의 마을 강자 1명이 있다. 모든 NPC에게 전투 능력이 있다 (TOWNSFOLK_COMBAT.md).',
 '- 퀘스트: ①~⑥은 선의 퀘스트, ⑦은 강자와의 결투(선/악 분기), ⑧은 강자 암살(악), ⑨는 악의 길 신규, ⑩은 기존 퀘스트의 악의 길 변형. 악의 길 퀘스트는 선악 「악명」 이하에서 열린다.',
 '- 무기상점 = 장비상점(무기·방어구·보조무기)이며 주인이 대장장이로서 강화를 맡는다. 외형상점 물건은 능력치 없는 순수 외형이다. 상점 가격은 선악 등급에 따라 바뀐다 (SYSTEMS.md 3장).','']
for t in TOWNS:
    s=t['strongman']
    L+=[f"## {t['id']}. {t['name']}"+(f" {t['subtitle']}" if t['subtitle'] else ''),'',
        f"- **테마**: {t['theme']}",
        f"- **연결**: 지역 {', '.join(str(a)+'지역' for a in t['connects']['areas'])} / 마을 {', '.join(x+' '+TN[x] for x in t['connects']['towns'])}",
        f"- **도착 시점**: {t['arrival']}",f"- **지도 위치(1024 기준)**: {t['map_xy_1024']}",f"- **강화 가능 단계**: +{t['enhance_max']}까지",
        f"- **마을 강자**: {s['name']} ({s['title']}) — 흡수 스킬 「{s['skill']['name']}」. 패턴은 TOWNSFOLK_COMBAT.md",'',
        '### NPC (10명)','','| 이름 | 역할 | 성격 | 인사말 | 악명 이하일 때 반응 | 전투 |','|---|---|---|---|---|---|']
    for n in t['npcs']:
        c=n['combat']; L.append(f"| {n['name']} | {n['role']} | {n['personality']} | “{n['greeting']}” | “{n['greeting_dark']}” | {c['behavior']} · {', '.join(a['name'] for a in c['attacks'])} |")
    nmap={n['id']:n['name'] for n in t['npcs']}; nmap['strongman']=s['name']
    L+=['','### 퀘스트','']
    for qq in t['quests']:
        tag={'good':'선','evil':'악','both':'선/악 분기'}[qq['path']]
        L+=[f"**{qq['id']}. {qq['title']}** · {qq['type']} · [{tag}] · 의뢰: {nmap[qq['giver']]}"+(f" · 조건: {qq['requires']}" if qq.get('requires') else '')+(f" · 변형 원본: {qq['variant_of']}" if qq.get('variant_of') else ''),
            f"- 이야기: {qq['story']}",f"- 목표: {qq['objective']}",f"- 보상: {qq['reward']}",f"- 선악 조건: {qq['karma_gate']}",'']
    for kind,title in [('tool','도구상점'),('weapon','장비상점 (무기상점)'),('cosmetic','외형상점')]:
        owner=[n['name'] for n in t['npcs'] if n.get('shop')==kind][0]
        L+=[f"### {title} ({owner})",'','| ID | 품목 | 가격(금화) | 설명 |','|---|---|---|---|']
        for i,p in t['shops'][kind]:
            if kind=='tool': a,b=TOOLS[i]['name'],TOOLS[i]['effect']
            elif kind=='cosmetic': a,b=COSMETICS[i]['name'],COSMETICS[i]['look']
            else: e=EQ[i]; a=e['name']; b=f"[{SLOTN[e['slot']]} · 티어 {e['tier']}] {stat(e)} — {e['visual']['look']}"
            L.append(f"| `{i}` | {a} | {p} | {b} |")
        L.append('')
    if t['shops']['black']:
        L+=['**뒷거래 (도구상점 주인, 악명 이하 전용)**: '+', '.join(f"`{i}` {TOOLS[i]['name']} {p}" for i,p in t['shops']['black']),'']
L+=['## 이동 거리와 길의 몹 배치','',TRAVEL_RULE,'','| 길 | 화면 수 | 몹 배치 (화면 구간: 몹) | 비고 |','|---|---|---|---|']
def lbl(x): return f"{x} {TN[x]}" if x in TN else x
for r in ROADS: L.append(f"| {lbl(r['frm'])} ↔ {lbl(r['to'])} | {r['screens']} | "+' / '.join(f"{a}: {b}" for a,b in r['mobs'])+f" | {r['note']} |")
L+=['','현상금 ★3이면 길 어디서든 현상금 사냥꾼 자흐라가 습격할 수 있다 (자흐라를 G7에서 살려 동료로 삼았으면 대신 다른 사냥꾼 무리).']
DOCS['TOWNS.md']=L
# ---------------- EQUIPMENT.md
E=['# 장비와 외형 시스템','','> 전체 아이템 목록과 출처는 [ITEMS.md](ITEMS.md). 데이터: `data/towns.json` → `catalog`, `equipment`. (아직 게임에 구현하지 않음 — 설계만)','',
 '## 장비 칸 (4칸)','','| 칸 | 레이어 | 외형 변화 |','|---|---|---|']
for s_ in EQUIP_SLOTS: E.append(f"| {s_['name']} | `{s_['layer']}` | {s_['desc']} |")
E+=['','방어구 30종은 몸 16 + 투구 14로 나뉜다(같은 「방어구」 분류, 칸은 2개).','','**외형상점(코스메틱)**: '+COSMETIC_RULE,'',
 '## 그리기 방식: 레이어 페이퍼돌','',
 '주인공을 한 장의 그림이 아니라 여러 레이어를 겹쳐 그린다. 모든 레이어 시트는 **같은 프레임 배치·같은 앵커(발 중심)** 를 쓴다. 그래서 몸 프레임 번호 하나로 모든 레이어의 같은 칸을 겹치면 된다.','',
 '기본 순서 (아래 → 위): **몸 → (타락 눈·핏줄) → 장화 → 방어구 → 투구 → (후광·뿔) → 망토 → (오라) → 무기·보조무기**','',
 '| 방향 | 실제 그리는 순서 (아래→위) | 이유 |','|---|---|---|',
 '| 아래(정면) | 오라(뒤) → 망토 → 몸 → 타락 눈 → 장화 → 방어구 → 투구 → 방패·오브(왼쪽) → 무기 → 오라(앞) | 망토가 등 뒤에 있음 |',
 '| 위(뒷면) | 무기 → 방패 → 몸 → 장화 → 방어구 → 투구 → 망토 → 오라 | 망토가 몸을 덮고, 무기·방패는 몸 앞쪽(화면 안쪽)에 가려짐 |',
 '| 오른쪽 | 방패(왼팔, 뒤쪽 팔) → 망토 → 몸 → 타락 눈 → 장화 → 방어구 → 투구 → 무기 | 왼팔은 몸 뒤, 오른손 검은 앞 |',
 '| 왼쪽 | 오른쪽을 좌우 반전 (방패·무기 손 위치도 반전되는 것은 허용 — 기존 데모와 같은 방식) | 시트 절약 |','',
 '- 프레임 단위: 걷기 4방향×4, 3단 콤보(횡베기 2·찌르기 2·돌려베기 5, 위/아래 각 3), 스킬 포즈 약 40프레임, 피격 1, 잠수/수영 2. 프레임마다 각 레이어 그림이 따로 있다.',
 '- 돌려베기 회전 프레임에서는 프레임마다 방향 순서를 따로 적용한다 (데이터에 프레임별 layerOrder 오버라이드 칸).',
 '- **팔레트 스왑**: 방어구·투구·무기·방패 시트는 회색 4단계 원본으로 한 번만 그리고, 실행할 때 아이템의 `palette`(4색 램프)로 치환한다. 외곽선(검정)과 피부·눈 색은 치환하지 않는다.',
 '- 치환 사본은 장착을 바꿀 때 1회 오프스크린 캔버스에 캐시한다. 매 프레임 비용 없음.',
 '- 강화 외형(+4 발광, +7 오라, +9 최대 오라)은 무기 레이어 위에 코드로 덧그린다 (SYSTEMS.md).',
 '- 투척무기: 평소엔 허리·허벅지·등의 작은 오버레이로 보이고, 보조 키(Shift)로 던질 때만 왼손 던지기 포즈 1프레임 + 투사체 스프라이트. 오브: 몸 레이어와 별개로 어깨 옆을 천천히 도는 FX(정면에선 앞, 뒷면에선 뒤). 반지: 손 위치에 2px 반짝임만.',
 '- 쌍검(`wpn_twin`)을 들면 보조무기 칸이 잠기고 왼손에 같은 날을 하나 더 그린다.',
 '- 코스메틱: 망토 색은 망토 레이어 팔레트 교체, 의상 스킨은 방어구 레이어 그림 교체(능력치는 그대로), 머리 장식은 투구 칸이 비었을 때(또는 「투구 숨기기」) 투구 자리에, 궤적 스킨은 무기 `trail` 색 교체.','',
 '## 선악에 따른 타락 외형','','선악 수치(SYSTEMS.md 3장)가 내려가면 페이퍼돌에 타락 레이어가 추가된다. 코스메틱으로 가릴 수 없다(마왕 등급부터는 망토·의상 코스메틱도 덮어씀).','',
 '| 등급 | 추가·변경 레이어 |','|---|---|']
for c in CORRUPTION_VISUALS: E.append(f"| {c['tier']} | "+'<br>'.join(c['layers'])+' |')
E+=['','## 앞으로 필요한 스프라이트 시트','',
 '1. `body_base` — 기본 신체(얼굴·갈색 머리·맨손), 위 프레임 전부. 기존 걷기/콤보/스킬 시트를 다시 그려 분리.',
 '2. `body_*` 회색 원본: tunic, quilted, leather, light, mail, plate, fur, coat, shell, scale (10종 형태) × 전 프레임.',
 '3. `head_*` 회색 원본: hood, circlet, cap_lamp, turban, shell, helm_horn, helm_fur, helm_visor, mask, witch, plume, crown (12종) × 4방향 + 콤보/스킬 오프셋 표.',
 '4. `cape` 회색 원본 1종(펄럭임 포함) + `cape_tattered`(타락) + 코스메틱 장식 레이어.',
 '5. `wpn_*` 회색 원본: straight, straight_long, leaf, crystal, broad, curved, wavy, ornate, dagger, machete, harpoon, scepter, whip, flame, spear, twin (16종 날 모양) × 손 위치 프레임.',
 '6. 보조무기: `off_shield_round`, `off_shield_kite`, `off_shield_tower`, `acc_bracer`, `acc_amulet`, `acc_boots`, `acc_ring`(반짝임 FX), `off_orb`(떠다니는 구슬 4프레임), `off_throw_*`(sling, knife, pick, ring, javelin, star — 몸 오버레이 + 투사체 1~2프레임) + 던지기 포즈 4방향.',
 '7. `head_deco`, `neck_deco` 코스메틱 오버레이.',
 '8. 타락: `eyes_corrupt_1/2`, `veins_1/2`, `horns`, `halo_fx`, `aura_dark`(입자), 3두 용 그림자.','',
 '제작 팁: 기존 파이프라인(마젠타 배경 시트 → 크로마키 → 연결 요소 분리)을 그대로 쓰되, 레이어 시트는 「몸 실루엣 위에 해당 부분만」 그린 시트로 주문하고 몸과 같은 칸 배치·같은 크기로 맞춘다.','',
 '## 장비 외형 설명 (팔레트 색 포함)','','| ID | 아이템 | 칸 | 스프라이트 키 | 팔레트 | 궤적 | 외형 |','|---|---|---|---|---|---|---|']
for e in EQUIP_ITEMS:
    pal=' '.join(f"`{c}`" for c in PALETTES[e['visual']['palette']]); tr=' '.join(f"`{c}`" for c in e['visual'].get('trail',[])) or '—'
    E.append(f"| `{e['id']}` | {e['name']} | {SLOTN[e['slot']]} | `{e['visual']['sprite']}` | {e['visual']['palette']} {pal} | {tr} | {e['visual']['look']} |")
E+=['','## 외형상점 아이템 (능력치 없음)','','| 아이템 | 종류 | 레이어 | 팔레트 | 외형 | 비고 |','|---|---|---|---|---|---|']
for i,c in COSMETICS.items():
    E.append(f"| {c['name']} | {c['kind']} | `{c['layer']}` | "+' '.join(f"`{x}`" for x in c['palette'])+f" | {c['look']} | {'퀘스트 보상 전용' if c.get('quest_only') else ''} |")
DOCS['EQUIPMENT.md']=E
# ---------------- SYSTEMS.md
TT={x['tier']:x for x in ENH_TIERS}
S=['# 시스템 설계: 무기 강화 · 몬스터 리스폰 · 선악 · 현상금','','> 데이터: `data/towns.json` → `enhancement`, `respawn`, `karma`, `bounty`, `skill_evolution`. (설계 문서 — 아직 게임 미구현)','',
 '## 1. 무기 강화 (+0 ~ +9)','','- 대상: **무기만**. 방어구·보조무기는 강화 없음.',f"- 강화 담당: {ENH_RULES['npc']}",
 '- 파괴 없음. +1~+6 실패는 단계 유지(재료·금화만 소모), **+7 이상 시도 실패 시 1단계 하락**.',
 f"- 실패 보정: {ENH_RULES['pity']}",'- 성공률 보정: '+' / '.join(ENH_RULES['boosts']),f"- 보호 아이템: {ENH_RULES['protection']}",
 '- 장인 불칼(E)이 죽으면 E의 +5%p 보너스와 +9 강화가 사라지고 쇠메가 +6까지만 맡는다 (TOWNSFOLK_COMBAT.md).','',
 '### 단계별 표','','| 단계 | 성공률 | 재료 | 금화 | 공격력 보너스(누적) | 실패 시 |','|---|---|---|---|---|---|']
for l in ENH_LEVELS: S.append(f"| +{l['level']} | {l['success']}% | {TT[l['tier']]['name']} ×{l['count']} | {l['coins']} | +{l['atk_pct']}% | {l['fail']} |")
S+=['',ENH_RULES['stat_note'],'','### 강화 재료 티어 (챔피언 전용 드롭)','','| 티어 | 재료 | 나오는 지역 | 쓰는 강화 단계 |','|---|---|---|---|']
use={}
for l in ENH_LEVELS: use.setdefault(l['tier'],[]).append(f"+{l['level']}")
for x in ENH_TIERS: S.append(f"| {x['tier']} | {x['name']} | {', '.join(str(a)+'지역' for a in x['areas'])} | {', '.join(use[x['tier']])} |")
S+=['','재료는 **챔피언 몬스터만** 떨어뜨린다. 각 챔피언 **첫 격파는 해당 재료 2개 확정**, 리스폰 후 격파는 아래 확률로 1개(그중 5%는 2개). 챔피언의 희귀 장비 드롭은 ITEMS.md 참고.','',
 '| 지역 | 챔피언 | 재료 | 드롭률 | 수호의 부적 | 비고 |','|---|---|---|---|---|---|']
for d in CHAMPION_DROPS: S.append(f"| {d['area']} | {d['champion']} | {TT[d['tier']]['name']} | {d['drop']}% | {str(d['guard'])+'%' if d.get('guard') else '—'} | {d.get('note','')} |")
S+=['','### 강화 외형','','| 단계 | 효과 | 설명 |','|---|---|---|']
for v in ENH_RULES['visuals']: S.append(f"| +{v['level']} 이상 | `{v['fx']}` | {v['desc']} |")
S+=['','## 2. 몬스터 리스폰','',f"- **규칙**: {RESPAWN['rule']}",f"- **단위**: {RESPAWN['unit']}",f"- **챔피언**: {RESPAWN['champions']}",f"- **보스**: {RESPAWN['boss']}",
 '- **마을 사람·마을 강자는 리스폰하지 않는다** (죽으면 영구). 일반 경비병만 재방문 시 보충.',
 '- **저장 플래그**: '+', '.join(f"`{x}`" for x in RESPAWN['save_flags'])+', `npc_dead[]`, `strongman_state` (ally/dead), `karma`, `bounty{town}`',f"- **스폰 구역**: {RESPAWN['spawn_zones']}",f"- **수량**: {RESPAWN['counts']}",'','### 배치 규칙','']
S+=[f"{i+1}. {p}" for i,p in enumerate(RESPAWN['placement'])]
S+=['',f"- **선택 규칙**: {RESPAWN['anti_abuse']}",'','```js','function pickSpot(map, entry, water){','  for (let k=0;k<30;k++){','    const p = randomPointIn(map.spawnZones);','    if (dist(p, entry) < 260) continue;',
 '    if (water ? !map.isWater(p) : (map.blocked(p, R) || map.isWater(p))) continue;','    if (nearAny(p, mobs, 72) || nearAny(p, map.props, 48)) continue;','    return p;','  }','  return farthest(map.fallbackPoints, entry);','}','```','',
 '## 3. 선악 수치 (카르마)','',f"- 범위 {KARMA['range'][0]} ~ +{KARMA['range'][1]}, 시작 {KARMA['start']}.",*[f"- {n}" for n in KARMA['notes']],'',
 '### 등급과 효과','','| 등급 | 범위 | 상점 가격 | 상점 | NPC 반응 | 선의 퀘스트 | 악의 길 퀘스트 |','|---|---|---|---|---|---|---|']
for t in KARMA['tiers']:
    S.append(f"| {t['name']} | {t['min']} ~ {t['max']} | {('×'+str(t['price'])) if t['price'] else '거래 거절'} | {t['shops']} | {t['npc']} | {t['quests']} | {t['evil_quests']} |")
S+=['','### 선악이 바뀌는 행동','','| 행동 | 변화 |','|---|---|']+[f"| {a} | {b} |" for a,b in KARMA['actions']]
S+=['','### 선악이 영향을 주는 것 (요약)','',
 '1. **상점**: 가격 배율, 외형상점 거절(악명), 정상 거래 거절 + 뒷거래·협박(마왕). 강자를 결투에서 죽인 마을은 가격 +25% 영구.',
 '2. **NPC 반응**: 등급별 대사. 악명 이하에서는 각 NPC의 「악명 반응」 대사(TOWNS.md)로 바뀌고, 아이들은 숨고, 마왕 등급에서는 도망치거나 무릎 꿇는다.',
 '3. **퀘스트**: 마을마다 선의 퀘스트 ①~⑥, 결투 ⑦(선/악 분기), 악의 길 ⑧~⑩. 악명 이하에서는 ③~⑥ 의뢰인이 거절한다.',
 '4. **외형**: 타락 레이어 (EQUIPMENT.md 「선악에 따른 타락 외형」) — 붉은 눈, 핏줄, 망토 어두워짐 → 찢어진 검은 망토, 검보라 오라, 뿔.',
 '5. **흡수 스킬 진화**: 아래 표. 선악 +20 이상이면 빛 변형, -20 이하이면 어둠 변형, 그 사이는 기본형. 강자에게 전수받은 기술은 빛 쪽이, 강탈한 기술은 어둠 쪽이 한 단계 강하다.',
 '6. **엔딩**: STORY.md 엔딩 조건.','',
 '### 흡수 스킬의 빛 / 어둠 변형 (보스 스킬)','','| 스킬 | 기본형 | 빛 (+20 이상) | 어둠 (-20 이하) |','|---|---|---|---|']
S+=[f"| {a} | {b} | {c} | {d} |" for a,b,c,d in SKILL_EVOLUTION]
S+=['','마을 강자 8명의 스킬 변형은 TOWNSFOLK_COMBAT.md에 있다.','','## 4. 경비병과 현상금','',f"- {BOUNTY['rule']}",'','| 범죄 | 현상금 |','|---|---|']+[f"| {a} | {b} |" for a,b in BOUNTY['crimes']]
S+=['','| 단계 | 현상금 | 효과 |','|---|---|---|']+[f"| ★{l['stars']} | {l['range']} | {l['effect']} |" for l in BOUNTY['levels']]
S+=['','**해결 방법**','']+[f"- {r}" for r in BOUNTY['resolve']]
g=BOUNTY['guards']
S+=['','**경비 담당**: '+', '.join(f"{k} {v}" for k,v in g['npc_guards'].items()),'',f"**{g['generic']['name']}**: 체력 {g['generic']['hp']}, 공격 {g['generic']['atk']}칸. "+' / '.join(g['generic']['attacks'])+f". {g['generic']['note']}"]
DOCS['SYSTEMS.md']=S
# ---------------- STORY.md
st=STORY
R=[f"# 본편 이야기 — {st['title']}",'','> 어두운 톤의 본편 줄거리. 데이터: `data/towns.json` → `story`. 선악 시스템은 SYSTEMS.md 3장, 마을 강자는 TOWNSFOLK_COMBAT.md.','',
 f"**주인공**: {st['hero']}",'',f"## 저주받은 재능: {st['gift']['name']}",'',st['gift']['rule'],'']+[f"- {x}" for x in st['gift']['law']]
R+=['','## 전제','',st['premise'],'',f"## 최종 적: {st['antagonist']['name']}",'',st['antagonist']['desc'],'',f"**{st['antagonist']['cult']}**",'',
 '## 보스가 존재하는 이유','','| 지역 | 보스 | 정체와 이유 |','|---|---|---|']+[f"| {a} | {b} | {c} |" for a,b,c in st['bosses']]
R+=['','## 줄거리 (진행 순서)','']
for a,b,c in st['chapters']: R+=[f"### {a} — {b}",'',c,'']
R+=['## 마을 강자와 이야기','','각 마을의 강자는 낙인을 지닌 하루를 「심판」하려 한다. 결투에서 살려 주면 피의 맹세로 기술을 받는다. 이것이 「받은 힘」이고, 진엔딩의 열쇠가 된다. 죽이면 기술을 빼앗는다. 이것이 「빼앗은 힘」이고, 굶주림을 키운다.','']
R+=[f"- **{s['town']} {s['name']}** ({s['title']}): {s['background']}" for s in STRONGMEN]
R+=['','## 엔딩','','엔딩 직전, 인간 카이렌의 질문(「삼키겠느냐, 받아 가겠느냐」)과 그 시점의 선악 수치로 정해진다. 위에서부터 조건을 확인한다.','','| 엔딩 | 조건 | 내용 |','|---|---|---|']
R+=[f"| {e['name']} | {e['cond']} | {e['desc']} |" for e in st['endings']]
R+=['','## 기존 퀘스트·대사 수정','','어두운 톤에 맞게 아래 퀘스트 설명과 NPC 인사말을 고쳤다 (ID는 그대로). 전체는 TOWNS.md.','','| 퀘스트 | 수정된 이야기 |','|---|---|']
R+=[f"| {k} | {v['story']} |" for k,v in QUEST_REWRITES.items()]
allnpc={n['id']:n['name'] for t in TOWNS for n in t['npcs']}
R+=['','| NPC | 수정된 인사말 |','|---|---|']+[f"| {allnpc[k]} | “{v}” |" for k,v in GREETING_REWRITES.items()]
DOCS['STORY.md']=R
# ---------------- TOWNSFOLK_COMBAT.md
C=['# 마을 강자 · 마을 사람 전투','','> 데이터: `data/towns.json` → `towns[].strongman`, `towns[].npcs[].combat`, `strongman_rule`, `townsfolk_rule`. 선악·현상금은 SYSTEMS.md 3·4장.','',
 '# 1부. 마을 강자 (마을마다 1명, 보스급 인간)','',f"규칙: {STRONGMAN_RULE['phases']}",'',f"- 체력: {STRONGMAN_RULE['hp_scale']}",f"- 필살기: {STRONGMAN_RULE['ultimate']}",'',
 '## 선의 길: 죽이지 않고 이기기',STRONGMAN_RULE['good_path'],'',STRONGMAN_RULE['dark_path'],'',STRONGMAN_RULE['relearn'],'']
for i,s in enumerate(STRONGMEN,1):
    C+=[f"## {i}. {s['name']} — {s['town']} {TN[s['town']]} · {s['title']}",'',f"무기: {s['weapon']} · 체력 {s['hp']} · 기본 공격 {s['atk']}칸",'',s['background'],'']
    C+=[f"{k} {n}: {d}" for k,n,d in s['patterns']]
    C+=['',f"2페이즈 (50%): {s['phase2']}",'',f"**필살기 「{s['ultimate'][0]}」** (맞으면 최대 체력 50% 감소): {s['ultimate'][1]}",'',
        f"**흡수 스킬 「{s['skill']['name']}」**: {s['skill']['desc']}",f"- 빛 변형 (전수): {s['skill']['light']}",f"- 어둠 변형 (강탈): {s['skill']['dark']}",'',
        f"결투 퀘스트 {s['duel_quest'][0]} 「{s['duel_quest'][1]}」 / 암살 퀘스트 {s['murder_quest'][0]} 「{s['murder_quest'][1]}」",'']
C+=['# 2부. 마을 사람 전투 (80명)','',f"- {TOWNSFOLK_RULE['reaction']}",f"- {TOWNSFOLK_RULE['absorb']}",f"- {TOWNSFOLK_RULE['children']}",f"- {TOWNSFOLK_RULE['scale']}",f"- {TOWNSFOLK_RULE['essential']}",
 f"- 일반 경비병: {BOUNTY['guards']['generic']['note']}",'']
for t in TOWNS:
    C+=[f"## {t['id']}. {t['name']}",'','| 이름 | 체력 | 공격 | 반응 | 공격 패턴 | 흡수 능력 (악의 길) | 선악 |','|---|---|---|---|---|---|---|']
    for n in t['npcs']:
        c=n['combat']; C.append(f"| {n['name']} | {c['hp']} | {c['atk']} | {c['behavior']} | "+'<br>'.join(f"{a['name']}: {a['desc']}" for a in c['attacks'])+f" | {c['absorb']['name']}: {c['absorb']['effect']} | {c['karma_penalty']}{'' if c['lethal'] else ' (기운 강탈)'} |")
    C.append('')
DOCS['TOWNSFOLK_COMBAT.md']=C
for name,lines in DOCS.items():
    p=os.path.join(REPO,name); open(p,'w').write('\n'.join(lines)+'\n')
    for d in COPY_DIRS:
        if os.path.isdir(d): shutil.copy(p,os.path.join(d,name))
for d in ['/workspace/town-demo/data']:
    if os.path.isdir(d): shutil.copy(os.path.join(REPO,'data','towns.json'),d)
print(json.dumps(COUNTS,ensure_ascii=False))
