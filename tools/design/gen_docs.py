# -*- coding: utf-8 -*-
# towns_data.py (+ story_data.py) → data/towns.json + TOWNS.md / ITEMS.md / EQUIPMENT.md / SYSTEMS.md / STORY.md / TOWNSFOLK_COMBAT.md
import json, sys, os, shutil
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from towns_data import *
import craft_data as _cd
from towns_data import RECIPES, NPC_DROPS
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
# ---------------- 제작·재료 검증
MOBS_EXPECT={a:[m[0] for m in _cd.AREAS[a]['mobs']] for a in range(1,10)}
dropped={(d['area'],d['mob']) for d in MOB_DROPS if d['drops']}
for a,ms in MOBS_EXPECT.items():
    for m in ms: assert (a,m) in dropped and (10,'강화 '+m) in dropped,(a,m)
for a,ch,*_ in _cd.CHAMPS: assert (a,ch) in dropped and (10,'강화 '+ch) in dropped,ch
for a,b,*_ in _cd.BOSSES: assert (a,b) in dropped,b
assert sum(d['kind']=='normal' for d in MOB_DROPS)==72 and sum(d['kind']=='champion' for d in MOB_DROPS)==18 and sum(d['kind']=='boss' for d in MOB_DROPS)==10
def _matok(m): return m in MATERIALS or m.startswith('enh:')
for d in MOB_DROPS+NPC_DROPS:
    assert 1<=len(d['drops'])<=3,d
    for m,_ in d['drops']: assert _matok(m),m
for t in TOWNS:
    for n in t['npcs']:
        if n['combat']['lethal']: assert any(x['npc']==n['id'] for x in NPC_DROPS),n['id']
        else: assert not any(x['npc']==n['id'] for x in NPC_DROPS),n['id']
for e in EQUIP_ITEMS:
    r=RECIPES.get(e['recipe']); assert r and r['item']==e['id'],e['id']
    for x in r['materials']: assert x['mat'] in MATERIALS,(e['id'],x['mat'])
    if r['upgrade_from']: assert EQ[r['upgrade_from']]['tier']<e['tier']
assert len(RECIPES)==len(EQUIP_ITEMS)==90
for m in MATERIALS.values(): assert m['sources'] and m['icon']['shape'] and m['name']
assert len({m['name'] for m in MATERIALS.values()})==len(MATERIALS)
for t in TOWNS:
    assert t['forge'] and t['raze']
    for m,_ in t['raze']['loot']: assert m in MATERIALS,m
    for m in t['forge']['sells']: assert m in MATERIALS,m
for m,_n,_r in FINAL_HUMAN['drops']: assert m in MATERIALS,m
assert len(FINAL_HUMAN['patterns'])==6 and FINAL_HUMAN['ultimate'] and FINAL_HUMAN['phase2']
assert len(RAZE)==8 and {r['town'] for r in RAZE}==set(TN)
_ft=[t['forge']['tier'] for o in order for t in TOWNS if t['id']==o]; assert _ft==sorted(_ft)
for _f in ['STORY','TOWNSFOLK_RULE','RAZE_RULE','FINAL_HUMAN','QUEST_REWRITES','GREETING_REWRITES']:
    import re as _re; assert not _re.search(r'하루(?!\s*(1회|최대|\d|한 번|에|동안|종일))',json.dumps(globals()[_f],ensure_ascii=False)),_f
COUNTS.update(materials=len(MATERIALS),recipes=len(RECIPES),mob_drop_tables=len(MOB_DROPS),npc_drop_tables=len(NPC_DROPS),forges=len(FORGES),razeable_towns=len(RAZE),craft_only=len(CRAFT_ONLY))
# ---------------- 마왕 모드 검증
DK_=DEMON_KING
assert len(DK_['skills'])==3 and all(k['motion'] and k['effect'] and k['cost'] and k['cooldown'] for k in DK_['skills'])
assert len({k['id'] for k in DK_['skills']})==3 and DK_['map_skill']['children'] and len(DK_['map_skill']['motion'])>=3
assert '아이' in DK_['map_skill']['children'] and '죽일 수 없다' in RAZE_RULE['children']
assert {g['slot'] for g in DK_['gear']['items']}>={'weapon','armor','helmet','offhand'}
for g in DK_['gear']['items']: assert g['palette'] in DK_['gear']['palettes'] and g['id'] not in EQ
_allnpc={n['id'] for t in TOWNS for n in t['npcs']}
_kids={n['id'] for t in TOWNS for n in t['npcs'] if not n['combat']['lethal']}
assert _kids=={'a_kid','b_twins','h_boy','g_thief','f_kid','e_apprentice','c_child'},_kids
for a,_n,_r,fb in DK_['essential']['list']: assert (a in _allnpc or a=='strongman') and a not in _kids and fb,a
for t in TOWNS:  # 강림 후 아이 외 전원 처치 가능 = 아이가 아닌 NPC는 모두 lethal
    for n in t['npcs']: assert n['combat']['lethal'] or n['id'] in _kids
assert RAZE_RULE['structures']['threshold']==70
for z in RAZE: assert z['structures']['house']+z['structures']['shop']>0 and z['structures']['landmark']>=1 and z['ruin_power'] and ('제단' in z['gained'] or '상인' in z['gained'])
for i,ms,so in MAGMA_ALTAR:
    assert i in TOOLS,i
    for m,c in ms: assert m in MATERIALS,m
assert '불태운다」를 고르면' not in json.dumps(RAZE_RULE,ensure_ascii=False)
COUNTS.update(dk_skills=len(DK_['skills']),dk_gear=len(DK_['gear']['items']),essential_fallbacks=len(DK_['essential']['list']))
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
 strongman_rule=STRONGMAN_RULE,townsfolk_rule=TOWNSFOLK_RULE,
 materials=list(MATERIALS.values()),recipes=list(RECIPES.values()),
 drops=dict(monsters=MOB_DROPS,townsfolk=NPC_DROPS),forges=dict(rules=FORGE_RULES,towns=FORGES),
 final_human=FINAL_HUMAN,raze=dict(rule=RAZE_RULE,towns=RAZE),demon_king=DEMON_KING,magma_altar=[dict(item=i,materials=[dict(mat=m,count=c) for m,c in ms],souls=so) for i,ms,so in MAGMA_ALTAR])
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
R+=['## 마을 강자와 이야기','','각 마을의 강자는 낙인을 지닌 필멸자를 「심판」하려 한다. 결투에서 살려 주면 피의 맹세로 기술을 받는다. 이것이 「받은 힘」이고, 진엔딩의 열쇠가 된다. 죽이면 기술을 빼앗는다. 이것이 「빼앗은 힘」이고, 굶주림을 키운다.','']
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
# ---------------- 제작 공통
MN=lambda m: (m[4:]+' (강화 재료)') if m.startswith('enh:') else MATERIALS[m]['name']
def rate(r): return f"{r}%" if isinstance(r,(int,float)) else str(r)
def mats(r): return ', '.join(f"{MN(x['mat'])} ×{x['count']}" for x in r['materials'])
FN={f['town']:f for f in FORGES}
KIND_KO={'mob':'일반 몹','champion':'챔피언','boss':'보스','townsfolk':'마을 사람','strongman':'마을 강자','forge_shop':'대장간'}
TYPE_KO={'hide':'가죽','bone':'뼈·뿔','crystal':'결정','essence':'정수','cloth':'천·실','wood':'목재','metal':'금속','shell':'껍데기','core':'핵','token':'징표','scrap':'잡동사니'}
# ITEMS.md: 레시피 열 추가 (장비 표 행 끝에 붙임)
_I=[]
for line in DOCS['ITEMS.md']:
    if line.startswith('| ID | 이름 | 종류 | 티어 |'): line+=' 레시피 |'
    elif line.startswith('|---|---|---|---|---|---|---|---|') and line.count('|')==9: line+='---|'
    elif line.startswith('| `') and line[3:line.index('`',3)] in EQ:
        e=EQ[line[3:line.index('`',3)]]; r=RECIPES[e['recipe']]; line+=f" `{r['id']}` ({r['town']}, {r['success']}%{', 제작 전용' if r['craft_only'] else ''}) |"
    _I.append(line)
_I.insert(3,f"> 장비 90종 모두 대장간 제작 레시피가 있다 (`r_<아이템id>`, 칸: 최초 제작 마을·성공률). 재료는 [MATERIALS.md](MATERIALS.md), 레시피 상세는 [CRAFTING.md](CRAFTING.md). 「제작 전용」 {len(CRAFT_ONLY)}종은 드롭되지 않고 보스 핵으로만 만든다.")
DOCS['ITEMS.md']=_I
# ---------------- MATERIALS.md
MT=['# 재료 목록','',f"> 데이터: `data/towns.json` → `materials`, `drops`. 재료 {len(MATERIALS)}종. 제작 레시피는 [CRAFTING.md](CRAFTING.md), 장비는 [ITEMS.md](ITEMS.md).",
 '> 아이콘: 32×32 시트 `ui_materials.png`. 모양은 종류로, 주색은 아래 색 코드로 그린다. 판매가는 대장간·도구상점 기준 (선악 가격 배율 적용).','',
 '## 드롭 규칙','',
 '- 일반 몹: 대표 재료 1종(45~55%) + 지역 공통 재료(12%). 각 지역 첫 번째 몹은 레시피 두루마리 조각(1%)도 떨어뜨린다.',
 '- 챔피언: 기존 강화 재료(SYSTEMS.md 1장 확률 그대로) + 챔피언 고유 재료(첫 격파 2개 확정, 이후 35%) + 지역 공통 재료 확정.',
 '- 보스: 고유 핵 100% + 지역 공통 재료. 보스는 리스폰하지 않으므로 **핵은 게임당 1개**.',
 '- 10지역 강화판: 일반 몹은 원래 대표 재료(40%) + 「타락한」 공통 재료(15%), 강화 챔피언은 「타락한」 챔피언 재료(30%) + 원래 재료(60%) + 강화 재료.',
 '- 마을 사람: **악의 길 전용**. 죽였을 때만 역할별 재료 1종(60%) + 원한 서린 혼석(15%), 대장장이는 주괴(40%)도. 선악 감소는 살해 페널티 그대로이며 재료로 상쇄되지 않는다. **아이들은 드롭 표가 없다** (죽일 수 없음).','',
 '## 재료 전체','','| ID | 이름 | 티어 | 종류 | 아이콘 | 출처 (확률) | 판매가 | 비고 |','|---|---|---|---|---|---|---|---|']
for m in sorted(MATERIALS.values(),key=lambda m:(m['tier'],m['id'])):
    MT.append(f"| `{m['id']}` | {m['name']} | {m['tier']} | {TYPE_KO[m['type']]} | {m['icon']['shape']} `{m['icon']['color']}` | "+'<br>'.join(f"{KIND_KO[s['kind']]}: {s['where']}"+(f" ({rate(s['rate'])})" if s.get('rate') is not None else '')+(f" — {s['price']}금화" if s.get('price') else '') for s in m['sources'])+f" | {m['sell']} | {m.get('note','')} |")
MT+=['','## 몬스터별 드롭 표','']
for a in range(1,11):
    MT+=[f"### {a}지역 {AREA_NAMES[a]}",'','| 몬스터 | 구분 | 드롭 (확률) |','|---|---|---|']
    for d in [d for d in MOB_DROPS if d['area']==a]:
        MT.append(f"| {d['mob']} | {dict(normal='일반',champion='챔피언',boss='보스',enhanced='강화판',enhanced_champion='강화 챔피언')[d['kind']]} | "+', '.join(f"{MN(m)} {rate(r)}" for m,r in d['drops'])+' |')
    MT.append('')
MT+=['## 마을 사람 드롭 (악의 길 전용)','','| 마을 | NPC | 드롭 (확률) | 선악 |','|---|---|---|---|']
MT+=[f"| {d['town']} | {d['name']} | "+', '.join(f"{MN(m)} {rate(r)}" for m,r in d['drops'])+f" | {d['karma']} |" for d in NPC_DROPS]
MT+=['','마을 강자는 「심판의 징표」(살려 주면 건네받고, 죽이면 시신에서), 원탁의 주인 아스란은 영겁의 핵·원탁의 파편·복원 두루마리를 떨어뜨린다 (STORY.md).']
DOCS['MATERIALS.md']=MT
# ---------------- CRAFTING.md
FR=FORGE_RULES
CR=['# 제작 · 대장간','',f"> 데이터: `data/towns.json` → `recipes`, `forges`. 레시피 {len(RECIPES)}개 (장비 90종 전부). 재료는 [MATERIALS.md](MATERIALS.md).",'',
 '## 대장간 서비스 (마을마다 대장장이 = 무기상점 주인)','']+[f"- {x}" for x in FR['services']]+['',
 '## 대장간 등급','','레시피의 「필요 등급」 이상이어야 제작할 수 있다. 각 마을 대장간 의뢰(⑪)를 끝내면 등급이 1 오른다. E는 「장인의 시험」(E3)을 끝내면 마스터 대장간(등급 10)이 된다.','',
 '| 마을 | 대장간 | 대장장이 | 기본 등급 | 의뢰 후 | 의뢰 | 파는 기본 재료 |','|---|---|---|---|---|---|---|']
allnpc={n['id']:n['name'] for t in TOWNS for n in t['npcs']}
for f in FORGES:
    CR.append(f"| {f['town']} {TN[f['town']]} | {f['name']}{' ★마스터' if f.get('master') else ''} | {allnpc[f['npc']]} | {f['tier']} | {f['tier_after']} | {f['quest']} | {', '.join(MN(m) for m in f['sells'])} |")
CR+=['',FR['demon']+' 대신 검은 성채와 일부 폐허의 **마염 제단**에서 소모품을 만든다 (아래 표, SYSTEMS.md 7장).','',
 '### 대장간 의뢰','']
for t,q in FORGE_QUESTS.items(): CR+=[f"**{q[0]}. {q[1]}** ({t} {TN[t]}) — {q[2]}",f"- 목표: {q[3]}",f"- 보상: {q[4]}",'']
CR+=['## 성공률과 실패','','| 레시피 | 성공률 |','|---|---|']+[f"| {a} | {b}% |" for a,b in FR['success']]+['',FR['fail'],'',
 '## 레시피 해금','']+[f"- {x}" for x in FR['unlock']]+['',f"## 승급 제작",'',FR['upgrade'],'',
 '## 제작 전용 전설 장비','','| 장비 | 필요한 핵 | 원래 출처 |','|---|---|---|']
for i,c in CRAFT_ONLY.items(): CR.append(f"| {EQ[i]['name']} | {MATERIALS[c]['name']} | {EQ[i]['source']['where']} |")
CR+=['','그 밖에 「선대의 부러진 검」은 아스란이 떨어뜨리는 복원 두루마리 + 영겁의 핵으로 다시 벼릴 수 있다(퀘스트 보상판과 별개로 한 단계 강한 복원판을 만드는 것이 아니라, 퀘스트를 놓쳤을 때의 대체 경로). 「그림자 망토」는 그림자 천과 쌍검사의 그림자 칼날이 필요하다.','',
 '## 레시피 전체','']
for c,title in [('weapon','무기'),('armor','방어구'),('offhand','보조무기')]:
    CR+=[f"### {title}",'','| 레시피 | 장비 | 티어 | 재료 | 금화 | 등급 · 최초 마을 | 성공률 | 승급 재료 | 해금 |','|---|---|---|---|---|---|---|---|---|']
    for e in sorted([e for e in EQUIP_ITEMS if cat(e)==c],key=lambda e:(e['tier'],e['id'])):
        r=RECIPES[e['recipe']]
        CR.append(f"| `{r['id']}` | {e['name']}{' ★' if r['craft_only'] else ''} | {e['tier']} | {mats(r)} | {r['coins']} | {r['forge_tier']} · {r['town']} | {r['success']}% | {EQ[r['upgrade_from']]['name'] if r['upgrade_from'] else '—'} | {r['unlock']} |")
    CR.append('')
DOCS['CRAFTING.md']=CR
# ---------------- TOWNS.md: 대장간·폐허 정보
_T=[]
for line in DOCS['TOWNS.md']:
    _T.append(line)
    for t in TOWNS:
        if line.startswith(f"- **마을 강자**: {t['strongman']['name']} ("):
            f=t['forge']; z=t['raze']
            _T.append(f"- **대장간**: {f['name']} — 등급 {f['tier']} → {f['tier_after']} (의뢰 {f['quest']}). 제작·강화·수리·분해·판매 (CRAFTING.md)")
            _T.append(f"- **폐허판 (마왕의 길)**: 「{z['ruined_name']}」 · 아이 대피: {z['evac_leader']} → {z['evac_route']} · 난민 행선지: {z['refugees_to']} · 남는 것: {z['gained']} (SYSTEMS.md 6장)")
DOCS['TOWNS.md']=_T
# ---------------- SYSTEMS.md: 5장 대장간, 6장 마을 파괴
DOCS['SYSTEMS.md'][0]='# 시스템 설계: 무기 강화 · 몬스터 리스폰 · 선악 · 현상금 · 대장간 · 마을 파괴 · 마왕 모드'
S=DOCS['SYSTEMS.md']
S+=['','## 5. 대장간 · 제작 · 내구도','','상세 레시피는 [CRAFTING.md](CRAFTING.md), 재료와 드롭 표는 [MATERIALS.md](MATERIALS.md).','']+[f"- {x}" for x in FR['services']]
S+=['- 대장간 등급: '+' / '.join(f"{f['town']} {f['tier']}→{f['tier_after']}" for f in FORGES)+' (E는 마스터 대장간, 핵 레시피 전용)',
    '- 성공률: '+', '.join(f"{a} {b}%" for a,b in FR['success'])+'. '+FR['fail'],
    '- 장인 불칼(E)이 죽으면 마스터 대장간도 사라진다. 그 뒤로는 핵 레시피를 만들 수 없다 (핵은 판매·각인 봉헌용).','',
    f"- {FR['demon']}",'',
    '## 6. 마을 파괴 (마왕의 길, 자유 파괴)','',f"**발동**: {RAZE_RULE['trigger']}",'','### 구조물','','| 종류 | 이름 | HP | 붕괴 단계 |','|---|---|---|---|']+[f"| `{a}` | {b} | {c} | {d} |" for a,b,c,d in RAZE_RULE['structures']['types']]+['',
    f"- 단계: {RAZE_RULE['structures']['stages']}",f"- 피해: {RAZE_RULE['structures']['damage']}",f"- 저장: {RAZE_RULE['structures']['persist']}",
    f"- 파괴 판정: 소품을 뺀 건물 HP 합계의 **{RAZE_RULE['structures']['threshold']}%** 이상이 무너지면 파괴됨 (상징물 붕괴는 +15%p).",f"- 부분 파괴: {RAZE_RULE['structures']['partial']}",
    '','```js','// 구조물 피해 (마왕 상태에서만 호출)','function hitStructure(s, dmg){','  s.hp = Math.max(0, s.hp - dmg);','  const st = s.hp<=0 ? 3 : s.hp<=s.max*0.33 ? 2 : s.hp<=s.max*0.66 ? 1 : 0;',
    '  if (st !== s.stage){ s.stage = st; save.townStruct[town.id][s.id] = st; burstDebris(s); shake(st===3?8:4); gainRuin(1); }','  if (st===3 && s.kind!==\'prop\') checkRazed(town);','}',
    'function checkRazed(t){','  const tot = sum(t.structs.filter(b=>b.kind!==\'prop\'), b=>b.max);','  const down = sum(t.structs.filter(b=>b.kind!==\'prop\' && b.stage===3), b=>b.max);',
    '  const bonus = t.structs.some(b=>b.kind===\'landmark\' && b.stage===3) ? 0.15 : 0;','  if (down/tot + bonus >= 0.70) razeTown(t);   // 폐허판 전환, town_razed[t.id]=true','}','```','',
    '### 진행 순서','']+RAZE_RULE['siege']
S+=['',f"### 아이들의 대피 (절대 규칙)",'',RAZE_RULE['children'],'',f"### 폐허판 맵",'',RAZE_RULE['ruined'],'',f"### 보상",'',RAZE_RULE['rewards'],'',
    '### 세계의 반응','']+[f"- {x}" for x in RAZE_RULE['world']]+['','### 마을을 모두 파괴해도 깰 수 있는 이유','']+[f"- {x}" for x in RAZE_RULE['beatable']]
S+=['','### 마을별 파괴','','| 마을 | 폐허 이름 | 구조물 (민가/상점/상징물/성벽/소품) · 건물 HP 합 | 아이 대피 인솔 | 대피로 | 난민 행선지 | 잃는 것 | 생기는 것 | 전리품 | 폐허 권능 |','|---|---|---|---|---|---|---|---|---|---|']
for z in RAZE:
    S.append(f"| {z['town']} {TN[z['town']]} | {z['ruined_name']} | {'/'.join(str(z['structures'][k]) for k in ['house','shop','landmark','wall','prop'])} · {z['structure_hp']} | {z['evac_leader']} | {z['evac_route']} | {z['refugees_to']} | {z['lost']} | {z['gained']} | "+', '.join(f"{MN(m)} ×{c}" for m,c in z['loot'])+f" | {z['ruin_power']} |")
S+=['','- 저장 플래그: `town_razed[A~H]`, `corruption_stage`, `black_citadel_unlocked`. 파괴된 마을의 NPC는 `npc_dead[]`가 아니라 `npc_fled[]`(난민) 또는 `npc_dead[]`(싸우다 죽은 어른)로 나뉜다. 아이는 항상 `npc_evacuated[]`.']
# ---------------- STORY.md: 칭호, 최종 인간 보스, 파괴 영향
FH=FINAL_HUMAN
R=DOCS['STORY.md']
i=R.index(f"**주인공**: {STORY['hero']}")+1
R[i:i]=['','| 칭호 | 조건 |','|---|---|']+[f"| {h['title']} | {h['cond']} |" for h in STORY['hero_titles']]+['','NPC 대사·UI의 주인공 이름은 그때의 칭호로 표시된다 (예: 「영웅님」, 「마왕이다!」).']
j=R.index('## 엔딩')
R[j:j]=[f"## 숨은 최종 인간 보스: {FH['name']} — {FH['title']}",'',FH['background'],'',f"- **장소**: {FH['location']}",f"- **해금**: {FH['unlock']}",'',
        '| 변형 | 조건 | 내용 |','|---|---|---|']+[f"| {v['name']} | {v['cond']} | {v['desc']} |" for v in FH['variants']]+['',f"- **결말**: {FH['resolution']}",'- 패턴과 드롭은 TOWNSFOLK_COMBAT.md 3부.','',
        '## 마을 파괴와 이야기 (마왕의 길)','',RAZE_RULE['trigger'],'',RAZE_RULE['children'],'']+[f"- {x}" for x in RAZE_RULE['world']]+[f"- {RAZE_RULE['beatable'][0]}",'']
# ---------------- TOWNSFOLK_COMBAT.md 3부
C=DOCS['TOWNSFOLK_COMBAT.md']
C+=[f"# 3부. 최종 인간 보스 — {FH['name']} ({FH['title']})",'',f"무기: {FH['weapon']} · 체력 {FH['hp']} · 기본 공격 {FH['atk']}칸 · 마을 강자 8명 위의 존재",'',FH['background'],'',
    f"- 장소: {FH['location']}",f"- 해금: {FH['unlock']}",'']+[f"- 변형 「{v['name']}」 ({v['cond']}): {v['desc']}" for v in FH['variants']]+['']
C+=[f"{k} {n}: {d}" for k,n,d in FH['patterns']]
C+=['',f"2페이즈 (50%): {FH['phase2']}",'',f"**필살기 「{FH['ultimate'][0]}」** (맞으면 최대 체력 50% 감소): {FH['ultimate'][1]}",'',
    f"**흡수 스킬 「{FH['skill']['name']}」**: {FH['skill']['desc']}",f"- 빛 변형: {FH['skill']['light']}",f"- 어둠 변형: {FH['skill']['dark']}",'',
    f"결말: {FH['resolution']}",'','드롭: '+', '.join(f"{n} {r}%" for _,n,r in FH['drops']),'',f"리스폰: {FH['respawn']}",'',
    '# 4부. 마을 파괴 중 전투','','- 공성 중 어른 NPC는 반응(도주/반격)대로 행동하되, 도주형은 대피로로 빠져나가 난민이 된다(처치하지 않아도 공성 진행).','- 마을 강자는 항복 없이 필살기까지 쓴다. 이미 동료였어도 등을 돌린다.',
    f"- {RAZE_RULE['children']}"]

DK=DEMON_KING
S+=['','## 7. 마왕 모드 (마왕 강림 · 고정 장비 · 고정 스킬)','',f"- **발동**: {DK['trigger']}",f"- **되돌릴 수 없음**: {DK['irreversible']}",
    f"- **스킬 잠금**: {DK['lock']['skills']}",f"- **장비 잠금**: {DK['lock']['equipment']}",f"- **UI**: {DK['lock']['ui']}",'',
    f"### 기본 공격: {DK['normal_attack']['name']}",'',DK['normal_attack']['desc'],'',f"모션: {DK['normal_attack']['motion']}",'',
    '### 마왕 전용 스킬 (등록 3칸 고정)','','| 칸 | 스킬 | 게이지 | 재사용 | 효과 | 모션 |','|---|---|---|---|---|---|']
S+=[f"| {k['slot']} | **{k['name']}** `{k['id']}` | {k['cost']} | {k['cooldown']}초 | {k['effect']} | {k['motion']} |" for k in DK['skills']]
MS=DK['map_skill']
S+=['',f"### 맵 전체 스킬: {MS['name']} `{MS['id']}` (4번째 칸)",'',f"- **비용**: {MS['resource']}",f"- **파멸 게이지**: {MS['gauge']}",f"- **효과**: {MS['effect']}",f"- **아이**: {MS['children']}",'','**모션 (약 3.5초)**','']+[f"- {x}" for x in MS['motion']]+['',f"- 시트: {MS['sheets']}",'',
    '### 고정 마왕 장비','',f"콘셉트: {DK['gear']['concept']}",'','| 칸 | ID | 이름 | 스프라이트 | 팔레트 | 외형 |','|---|---|---|---|---|---|']
S+=[f"| {g['slot']} | `{g['id']}` | {g['name']} | `{g['sprite']}` | {g['palette']} "+' '.join(f"`{c}`" for c in DK['gear']['palettes'][g['palette']])+f" | {g['look']} |" for g in DK['gear']['items']]
S+=['',f"- **능력치**: {DK['gear']['stats']}",f"- **마왕 각인**: {DK['gear']['engrave']}",'','### 메아리 (강림 전 흡수 스킬의 변환)','',DK['echoes']['rule'],'','| 원래 스킬 | 메아리 효과 |','|---|---|']+[f"| {a} | {b} |" for a,b in DK['echoes']['list']]
S+=['','### 마염 제단 소모품 제작 (강림 후 유일한 제작)','','| 결과 | 재료 | 혼석 |','|---|---|---|']+[f"| {TOOLS[i]['name']} | {', '.join(f'{MN(m)} ×{c}' for m,c in ms)} | {so} |" for i,ms,so in MAGMA_ALTAR]
E_=DK['essential']
S+=['','### 모두 죽일 수 있다 — 핵심 인물 대체 경로 (진행 막힘 방지)','',E_['rule'],'']+[f"- {x}" for x in E_['general']]+['','| NPC | 이름 | 맡던 역할 | 죽었을 때 대체 경로 |','|---|---|---|---|']+[f"| `{a}` | {b} | {c} | {d} |" for a,b,c,d in E_['list']]
S+=['',f"- **아이 (절대 규칙)**: {RAZE_RULE['children']}",'','### 바뀐 규칙 정리 (충돌 해결)','','| 기존 규칙 | 마왕 모드에서 |','|---|---|']+[f"| {a} | {b} |" for a,b in DK['conflicts']]
S+=['','- 저장 플래그: `demon_king` (true면 영구), `dk_engrave` (0~9), `ruin_gauge`, `town_struct[마을][구조물]`, `npc_evacuated[]`.']
# STORY: 마왕의 길 요약
R=DOCS['STORY.md']; j=R.index('## 엔딩')
R[j:j]=['## 마왕 강림','',DK['trigger'],'',DK['irreversible'],'',f"- 고정 스킬: "+', '.join(k['name'] for k in DK['skills'])+f" + 맵 전체 스킬 「{MS['name']}」",
        '- 고정 장비: '+', '.join(g['name'] for g in DK['gear']['items']),'- 상세 규칙은 SYSTEMS.md 7장.','']
# EQUIPMENT: 마왕 세트
E=DOCS['EQUIPMENT.md']
E+=['','## 마왕 강림 시 고정 장비 (페이퍼돌 전 칸 잠금)','',f"콘셉트 아트: {DK['gear']['concept']}",'',DK['lock']['equipment'],'','| 칸 | 레이어 스프라이트 | 이름 | 팔레트 | 외형 |','|---|---|---|---|---|']
E+=[f"| {g['slot']} | `{g['sprite']}` | {g['name']} | {g['palette']} | {g['look']} |" for g in DK['gear']['items']]
E+=['','- 그리는 순서는 일반 장비와 같다. 단, 촉수(`off_dk_tentacles`)는 방패 자리 대신 **망토 바로 아래(등 뒤)** 에 그리고, 정면에서는 어깨 위로 끝만 보인다. 뒷면에서는 망토 위에 그린다.',
    '- 대검 `wpn_dk_greatsword`는 일반 검보다 커서 콤보 시트를 따로 둔다 (hero_dk_combo). 스킬 시트도 마왕 전용(skill_dk_*)이다.']
# TOWNSFOLK_COMBAT 4부 보강
C=DOCS['TOWNSFOLK_COMBAT.md']
C+=['',f"- 마왕 강림 후: {E_['rule']} 대체 경로는 SYSTEMS.md 7장.",'- 마을 강자는 강림 후 결투·항복 없이 바로 싸운다. 처치하면 메아리(+4%)와 심판의 징표.']
for name,lines in DOCS.items():
    p=os.path.join(REPO,name); open(p,'w').write('\n'.join(lines)+'\n')
    for d in COPY_DIRS:
        if os.path.isdir(d): shutil.copy(p,os.path.join(d,name))
for d in ['/workspace/town-demo/data']:
    if os.path.isdir(d): shutil.copy(os.path.join(REPO,'data','towns.json'),d)
print(json.dumps(COUNTS,ensure_ascii=False))
