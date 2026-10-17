# -*- coding: utf-8 -*-
# towns_data.py → data/towns.json + TOWNS.md + EQUIPMENT.md + SYSTEMS.md
import json, sys, os
sys.path.insert(0,os.path.dirname(__file__))
from towns_data import *
EQ={e['id']:e for e in EQUIP_ITEMS}
SLOTN={'weapon':'무기','armor':'방어구','helmet':'투구','accessory':'보조장비'}
TN={t['id']:t['name'] for t in TOWNS}
# ---- validate
for t in TOWNS:
    ids={n['id'] for n in t['npcs']}; assert len(t['npcs'])==10,t['id']
    shops=[n.get('shop') for n in t['npcs'] if n.get('shop')]; assert sorted(shops)==['cosmetic','tool','weapon'],t['id']
    assert len(t['quests'])>=5
    for qq in t['quests']: assert qq['giver'] in ids,(t['id'],qq['id'])
    for i,_ in t['shops']['tool']: assert i in TOOLS,i
    for i,_ in t['shops']['weapon']: assert i in EQ,i
    for i,_ in t['shops']['cosmetic']: assert i in COSMETICS,i
for e in EQUIP_ITEMS: assert e['visual']['palette'] in PALETTES,e['id']
# ---- json
def shopj(t):
    return {k:[{'item':i,'price':p} for i,p in v] for k,v in t['shops'].items()}
data=dict(version=1,note='게임에 아직 연결하지 않은 편집용 데이터. tools/towns_data.py 를 고치고 tools/gen_docs.py 를 실행하면 이 파일과 TOWNS.md/EQUIPMENT.md/SYSTEMS.md 가 함께 갱신된다.',
 towns=[dict({k:v for k,v in t.items() if k!='shops'},shops=shopj(t)) for t in TOWNS],
 catalog=dict(tools=TOOLS,cosmetics=COSMETICS),
 equipment=dict(slots=EQUIP_SLOTS,layer_order=['body','boots','armor','helmet','cape','weapon','offhand'],
   cosmetic_rule=COSMETIC_RULE,palettes=PALETTES,items={e['id']:{k:v for k,v in e.items() if k!='id'} for e in EQUIP_ITEMS}),
 travel=dict(rule=TRAVEL_RULE,roads=ROADS),
 enhancement=dict(rules=ENH_RULES,tiers=ENH_TIERS,levels=ENH_LEVELS,champion_drops=CHAMPION_DROPS),
 respawn=RESPAWN)
os.makedirs('/workspace/town-demo/data',exist_ok=True)
json.dump(data,open('/workspace/town-demo/data/towns.json','w'),ensure_ascii=False,indent=1)

def nm(i,kind):
    if kind=='tool': return TOOLS[i]['name'],TOOLS[i]['effect']
    if kind=='cosmetic': return COSMETICS[i]['name'],COSMETICS[i]['look']
    e=EQ[i]; st=f"공격 {e['atk']}" if e['slot']=='weapon' else (f"방어 {e['defense']}" if e.get('defense') else '')
    ef=', '.join(f"{v}" for v in e.get('effect',{}).values() if v not in('shield','bracer','amulet','boots'))
    return e['name'],f"[{SLOTN[e['slot']]}] {st}{(' · '+ef) if ef else ''} — {e['visual']['look']}"
# ---- TOWNS.md
L=['# 마을 설계서 (8개 마을)','',
 '> 원본 데이터: `data/towns.json` (생성기: `tools/design/towns_data.py` → `tools/design/gen_docs.py`). 장비 외형은 [EQUIPMENT.md](EQUIPMENT.md), 강화·리스폰은 [SYSTEMS.md](SYSTEMS.md) 참고.',
 '> 지도: `world_map_v4.jpg` / 번호판 `maps/world_map_v4_numbered.png` (빨강 1~10 = 지역, 파랑 A~H = 마을; 좌표는 1024 폭 기준).','',
 '## 진행 순서와 마을 도착 시점','',
 '| 순서 | 지역 | 직전 거점 마을 |','|---|---|---|',
 '| 프롤로그 | — | A 시작 마을 |','| 1 | 시작의 숲 | A |','| 2 | 수정 동굴 | B → H (1지역 후) |','| 3 | 모래 사막 | G (2지역 후) |','| 4 | 피라미드 | G |',
 '| 5 | 산호 바다 | F (4지역 후, 배로 출항) |','| 6 | 해안 절벽 | F |','| 7 | 화산 성채 | E (6지역 후) |','| 8 | 설산 뇌전 탑 | C (7지역 후) |','| 9 | 어둠 신전 | D (8지역 후) |','| 10 | 마룡의 둥지 | D |','',
 '공통 규칙: 마을마다 NPC 10명(그중 3명은 도구상점·무기상점·외형상점 주인), 서브 퀘스트 5개 이상. 무기상점 주인은 그 마을의 대장장이로 강화도 맡는다. 외형상점 물건은 능력치 없는 순수 외형이다.','']
for t in TOWNS:
    L+=[f"## {t['id']}. {t['name']}"+(f" {t['subtitle']}" if t['subtitle'] else ''),'',
        f"- **테마**: {t['theme']}",
        f"- **연결**: 지역 {', '.join(str(a)+'지역' for a in t['connects']['areas'])} / 마을 {', '.join(x+' '+TN[x] for x in t['connects']['towns'])}",
        f"- **도착 시점**: {t['arrival']}",
        f"- **지도 위치(1024 기준)**: {t['map_xy_1024']}",
        f"- **강화 가능 단계**: +{t['enhance_max']}까지",'',
        '### NPC (10명)','','| 이름 | 역할 | 성격 | 인사말 |','|---|---|---|---|']
    for n in t['npcs']: L.append(f"| {n['name']} | {n['role']} | {n['personality']} | “{n['greeting']}” |")
    nmap={n['id']:n['name'] for n in t['npcs']}
    L+=['','### 서브 퀘스트','']
    for qq in t['quests']:
        L+=[f"**{qq['id']}. {qq['title']}** · {qq['type']} · 의뢰: {nmap[qq['giver']]}"+(f" · 조건: {qq['requires']}" if qq.get('requires') else ''),
            f"- 이야기: {qq['story']}",f"- 목표: {qq['objective']}",f"- 보상: {qq['reward']}",'']
    for kind,title in [('tool','도구상점'),('weapon','무기상점'),('cosmetic','외형상점')]:
        owner=[n['name'] for n in t['npcs'] if n.get('shop')==kind][0]
        L+=[f"### {title} ({owner})",'','| 품목 | 가격(금화) | 설명 |','|---|---|---|']
        for i,p in t['shops'][kind]:
            a,b=nm(i,kind); L.append(f"| {a} | {p} | {b} |")
        L.append('')
L+=['## 이동 거리와 길의 몹 배치','',TRAVEL_RULE,'','| 길 | 화면 수 | 몹 배치 (화면 구간: 몹) | 비고 |','|---|---|---|---|']
def lbl(x): return f"{x} {TN[x]}" if x in TN else x
for r in ROADS: L.append(f"| {lbl(r['frm'])} ↔ {lbl(r['to'])} | {r['screens']} | "+' / '.join(f"{a}: {b}" for a,b in r['mobs'])+f" | {r['note']} |")
open('/workspace/thor-like-game/TOWNS.md','w').write('\n'.join(L)+'\n')

# ---- EQUIPMENT.md
E=['# 장비와 외형 시스템','','> TOWNS.md 의 무기상점 품목이 모두 여기 정의된다. 데이터: `data/towns.json` → `equipment`. (아직 게임에 구현하지 않음 — 설계만)','',
 '## 장비 칸 (4칸)','','| 칸 | 레이어 | 외형 변화 |','|---|---|---|']
for s in EQUIP_SLOTS: E.append(f"| {s['name']} | `{s['layer']}` | {s['desc']} |")
E+=['','**외형상점(코스메틱)**: '+COSMETIC_RULE,'',
 '## 그리기 방식: 레이어 페이퍼돌','',
 '주인공을 한 장의 그림이 아니라 여러 레이어를 겹쳐 그린다. 모든 레이어 시트는 **같은 프레임 배치·같은 앵커(발 중심)** 를 쓴다. 그래서 몸 프레임 번호 하나로 모든 레이어의 같은 칸을 겹치면 된다.','',
 '기본 순서 (아래 → 위): **몸(기본 신체·머리) → 장화 → 방어구 → 투구 → 망토 → 무기·보조장비(방패)**','',
 '| 방향 | 실제 그리는 순서 (아래→위) | 이유 |','|---|---|---|',
 '| 아래(정면) | 망토 → 몸 → 장화 → 방어구 → 투구 → 방패(왼팔) → 무기 | 망토가 등 뒤에 있음 |',
 '| 위(뒷면) | 무기 → 방패 → 몸 → 장화 → 방어구 → 투구 → 망토 | 망토가 몸 전체를 덮고, 무기·방패는 몸 앞쪽(화면 안쪽)에 가려짐 |',
 '| 오른쪽 | 방패(왼팔, 뒤쪽 팔) → 망토 → 몸 → 장화 → 방어구 → 투구 → 무기 | 왼팔은 몸 뒤, 오른손 검은 앞 |',
 '| 왼쪽 | 오른쪽을 좌우 반전 (방패·무기 손 위치도 반전되는 것은 허용 — 기존 데모와 같은 방식) | 시트 절약 |','',
 '- 프레임 단위: 걷기 4방향×4, 3단 콤보(횡베기 2·찌르기 2·돌려베기 5, 위/아래 각 3), 스킬 포즈 약 40프레임, 피격 1, 잠수/수영 2. 프레임마다 각 레이어 그림이 따로 있고, 무기 레이어는 프레임별 손 위치·각도에 맞춰 그려진다.',
 '- 돌려베기 회전 프레임(정면→옆→뒷면)에서는 프레임마다 위 표의 방향 순서를 따로 적용한다 (데이터에 프레임별 layerOrder 오버라이드 칸).',
 '- **팔레트 스왑**: 방어구·투구·무기·방패 시트는 회색 4단계(어두움→밝음) 원본으로 한 번만 그린다. 실행할 때 각 아이템의 `palette`(4색 램프)로 치환해 티어별 변형을 만든다 → 같은 모양의 철/청동/미스릴을 다시 그릴 필요 없음. 외곽선(검정)과 피부·눈 색은 치환 대상에서 제외.',
 '- 치환 방법: 시트를 불러올 때 오프스크린 캔버스에서 4개 회색값을 4색으로 바꾼 사본을 아이템별로 캐시(장착 바꿀 때 1회). 매 프레임 비용 없음.',
 '- 강화 외형(+4 발광, +7 오라, +9 최대 오라)은 무기 레이어 위에 코드로 덧그린다 (SYSTEMS.md).',
 '- 코스메틱: 망토 색은 망토 레이어 팔레트 교체, 의상 스킨은 방어구 레이어 그림 교체(능력치는 그대로), 머리 장식은 투구 칸이 비었을 때(또는 "투구 숨기기" 옵션) 투구 레이어 자리에, 궤적 스킨은 무기 `trail` 색 교체.','',
 '## 앞으로 필요한 스프라이트 시트','',
 '1. `body_base` — 기본 신체(얼굴·갈색 머리·맨손·속옷 수준), 위 프레임 전부. 기존 걷기/콤보/스킬 시트를 다시 그려 분리.',
 '2. `armor_*` 회색 원본: tunic, quilted, leather, light, mail, plate, fur (7종 형태) × 전 프레임.',
 '3. `head_*` 회색 원본: hood, circlet, cap_lamp, turban, shell, helm_horn, helm_fur, helm_visor (8종) × 4방향 + 콤보/스킬 프레임(머리 위치만 따라감, 프레임별 오프셋 표로 재사용 가능).',
 '4. `cape` 회색 원본 1종 (펄럭임 프레임 포함) + 코스메틱 장식 레이어(cape_deco: 단추·방울).',
 '5. `wpn_*` 회색 원본: straight, straight_long, leaf, crystal, broad, curved, wavy, ornate (8종 날 모양) × 손 위치 프레임. 베기 궤적은 코드로 그리므로 시트 불필요.',
 '6. `off_shield_round`, `off_shield_kite` (왼팔 방패), `acc_bracer`(팔뚝), `acc_amulet`(가슴), `acc_boots`(발) 오버레이.',
 '7. `head_deco`, `neck_deco` 코스메틱 오버레이 (모자·리본·목도리·물안경).','',
 '제작 팁: 기존 파이프라인(마젠타 배경 시트 → 크로마키 → 연결 요소 분리)을 그대로 쓰되, 레이어 시트는 "몸 실루엣 위에 해당 부분만" 그린 시트로 주문하고 몸과 같은 칸 배치·같은 크기로 맞춘다.','',
 '## 장비 목록과 외형 설명','','| 아이템 | 칸 | 능력치 | 스프라이트 키 | 팔레트 | 궤적 | 외형 | 판매 마을 |','|---|---|---|---|---|---|---|---|']
where={}
for t in TOWNS:
    for i,p in t['shops']['weapon']: where[i]=f"{t['id']} ({p})"
for e in EQUIP_ITEMS:
    st=f"공격 {e['atk']}" if e['slot']=='weapon' else f"방어 {e.get('defense',0)}"
    ef=[v for k,v in e.get('effect',{}).items() if k!='kind']; st+=(' · '+', '.join(ef)) if ef else ''
    pal=' '.join(f"`{c}`" for c in PALETTES[e['visual']['palette']])
    tr=' '.join(f"`{c}`" for c in e['visual'].get('trail',[])) or '—'
    E.append(f"| {e['name']} | {SLOTN[e['slot']]} | {st} | `{e['visual']['sprite']}` | {e['visual']['palette']} {pal} | {tr} | {e['visual']['look']} | {where.get(e['id'],'—')} |")
E+=['','## 외형상점 아이템 (능력치 없음)','','| 아이템 | 종류 | 레이어 | 팔레트 | 외형 | 비고 |','|---|---|---|---|---|---|']
for i,c in COSMETICS.items():
    E.append(f"| {c['name']} | {c['kind']} | `{c['layer']}` | "+' '.join(f"`{x}`" for x in c['palette'])+f" | {c['look']} | {'퀘스트 보상 전용' if c.get('quest_only') else ''} |")
open('/workspace/thor-like-game/EQUIPMENT.md','w').write('\n'.join(E)+'\n')

# ---- SYSTEMS.md
TT={x['tier']:x for x in ENH_TIERS}
S=['# 시스템 설계: 무기 강화 · 몬스터 리스폰','','> 데이터: `data/towns.json` → `enhancement`, `respawn`. (설계 문서 — 아직 게임 미구현)','',
 '## 1. 무기 강화 (+0 ~ +9)','',
 f"- 대상: **무기만**. 방어구·투구·보조장비는 강화 없음.",f"- 강화 담당: {ENH_RULES['npc']}",
 '- 파괴 없음. +1~+6 실패는 단계 유지(재료·금화만 소모), **+7 이상 시도 실패 시 1단계 하락**.',
 f"- 실패 보정: {ENH_RULES['pity']}",f"- 성공률 보정: "+' / '.join(ENH_RULES['boosts']),
 f"- 보호 아이템: {ENH_RULES['protection']}",
 '- (참고: 아직 소모품 60종 목록 문서는 저장소에 없어서, 수호의 부적·행운의 숫돌을 강화 보조 소모품으로 새로 정의했다. 목록이 생기면 거기에 편입.)','',
 '### 단계별 표','','| 단계 | 성공률 | 재료 | 금화 | 공격력 보너스(누적) | 실패 시 |','|---|---|---|---|---|---|']
for l in ENH_LEVELS:
    S.append(f"| +{l['level']} | {l['success']}% | {TT[l['tier']]['name']} ×{l['count']} | {l['coins']} | +{l['atk_pct']}% | {l['fail']} |")
S+=['',ENH_RULES['stat_note'],'','### 강화 재료 티어 (챔피언 전용 드롭)','','| 티어 | 재료 | 나오는 지역 | 쓰는 강화 단계 |','|---|---|---|---|']
use={}
for l in ENH_LEVELS: use.setdefault(l['tier'],[]).append(f"+{l['level']}")
for x in ENH_TIERS: S.append(f"| {x['tier']} | {x['name']} | {', '.join(str(a)+'지역' for a in x['areas'])} | {', '.join(use[x['tier']])} |")
S+=['','재료는 **챔피언 몬스터만** 떨어뜨린다 (일반 몹·보스는 안 줌, 퀘스트 보상으로 일부 지급). 각 챔피언 **첫 격파는 해당 재료 2개 확정**, 리스폰 후 격파는 아래 확률로 1개(그중 5%는 2개).','',
 '| 지역 | 챔피언 | 재료 | 드롭률 | 수호의 부적 | 비고 |','|---|---|---|---|---|---|']
for d in CHAMPION_DROPS:
    S.append(f"| {d['area']} | {d['champion']} | {TT[d['tier']]['name']} | {d['drop']}% | {str(d['guard'])+'%' if d.get('guard') else '—'} | {d.get('note','')} |")
S+=['','### 강화 외형 (무기 스프라이트 위 코드 효과)','','| 단계 | 효과 | 설명 |','|---|---|---|']
for v in ENH_RULES['visuals']: S.append(f"| +{v['level']} 이상 | `{v['fx']}` | {v['desc']} |")
S+=['','## 2. 몬스터 리스폰','',f"- **규칙**: {RESPAWN['rule']}",f"- **단위**: {RESPAWN['unit']}",f"- **챔피언**: {RESPAWN['champions']}",f"- **보스**: {RESPAWN['boss']}",
 '- **저장 플래그**: '+', '.join(f"`{x}`" for x in RESPAWN['save_flags']),f"- **스폰 구역**: {RESPAWN['spawn_zones']}",f"- **수량**: {RESPAWN['counts']}",'','### 배치 규칙 (무작위 위치)','']
S+=[f"{i+1}. {p}" for i,p in enumerate(RESPAWN['placement'])]
S+=['',f"- **선택 규칙(파밍 완화)**: {RESPAWN['anti_abuse']}",'',
 '### 예시 의사코드','','```js','function respawnMap(map, entry){','  for (const g of map.mobGroups){            // 보스는 mobGroups에 없음','    if (g.champion && !map.champZone) continue;','    const n = g.min + rand(g.max - g.min + 1);',
 '    for (let i=0;i<n;i++) spawn(g.kind, pickSpot(map, entry, g.water));','  }','}','function pickSpot(map, entry, water){','  for (let k=0;k<30;k++){','    const p = randomPointIn(map.spawnZones);','    if (dist(p, entry) < 260) continue;',
 '    if (water ? !map.isWater(p) : (map.blocked(p, R) || map.isWater(p))) continue;','    if (nearAny(p, mobs, 72) || nearAny(p, map.props, 48)) continue;','    return p;','  }','  return farthest(map.fallbackPoints, entry);','}','```']
open('/workspace/thor-like-game/SYSTEMS.md','w').write('\n'.join(S)+'\n')
print('ok', sum(len(t['quests']) for t in TOWNS),'quests')
