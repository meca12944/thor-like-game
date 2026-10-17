# 마을 밖 세계 (WORLD) — 필드 · 던전 · 보스 · 길 안내

Ys VIII 처럼 마을 문을 나서면 **월드맵 아이콘 이동 없이** 그대로 걸어서 이어진 필드를 지나 던전까지 간다.
월드맵(왕국 전도)은 **지도 화면의 보기 전용 그림**으로만 남는다.
비율은 `SCALE.md`(DQ6, 16×16 타일, 논리 화면 384×216 정수배)를 따르고, 모든 공격은 예고가 있어 회피(잔상 대시)로 피할 수 있다.

| 파일 | 역할 |
|---|---|
| `world.js` | 장면 관리자(페이드 · 지역 카드), 필드/던전/보스 진행, 전투, 함정, 퍼즐, 렌더(저해상도 + 선명한 HUD), 고정 60fps 루프 |
| `world_mobs.js` | 1지역 몹 · 챔피언 · 보스 행동 (`WorldMobs.def`) — 모든 공격이 예고(hazard)를 거침 |
| `world_nav.js` | 탐험 안개, 미니맵, 지도 화면, 목표, 경로 찾기(A*), 안내선 · 화면 끝 화살표, 퀘스트 ! / ?, 비석 순간이동 |
| `maps/*.json` | 지도 데이터 (지도 JSON 이 원본). `index.json` = 지역/목적지 목록, `quests.json` = 퀘스트, `tilesets.json` = 타일 규칙 |
| `assets/world/` | 타일 시트 · 스프라이트 아틀라스 (`tools/world_assets.py` 가 생성, png 압축) |
| `assets_src/world/` | 원본 그림 (#FF00FF 배경 생성 시트, 몹/보스/월드맵 원본). 커지면 Git LFS 로 옮길 폴더 |
| `tools/world_maps.py` | 1지역 지도 초안 생성기 (한 번 만든 뒤에는 JSON 을 직접 고친다) |
| `tools/test_balance.py` | 밸런스 검사 (BALANCE_TODO 적용값 · 난이도별 예고 하한 · 회피 창 · 토큰 · 물약) |
| `tools/test_world.py` | 헤드리스 전체 진행 테스트 (24항목) · `tools/record_world_gif.py` = 마일스톤 GIF |

템플릿 수정은 `tools/game.template.html` 의 `[world]` 주석 한 줄(스크립트 3개)과 `bgm.js` 의 `[world]` 두 줄뿐이다.

## 1. 흐름 (1지역)

```
마을 A 남쪽 문 ─▶ 바람길(field00, 마을 외곽) ─동쪽 끝─▶ 시작의 숲(field01, 던전 가는 길) ─북쪽 절벽 입구─▶
고대 숲 신전 B1 (열쇠 · 잠긴 문 · 가시/구멍) ─계단─▶ B2 (레버 2개 · 철창 · 봉인된 문) ─▶ 골렘의 방 (보스)
  └ 보스 격파 후 빛의 문 → 신전 입구로.  돌아올 때는 같은 길을 거꾸로 걸어 마을 문으로 (마을 위치는 나간 곳 그대로).
```

- 장면 전환: 페이드 아웃 → 로드 → (처음 가는 곳이면) **지역 카드**(지역 이름) → 페이드 인. BGM 은 지도마다 `bgm` (`area01_forest`, 챔피언 근처 `battle_champion`, 보스 `battle_boss` → 2페이즈 `battle_boss_phase2`, 승리 징글).
- 바람길 갈림길: 북쪽 마을 / 서쪽 바람의 언덕(비석 · 상자) / 동쪽 숲 / 남쪽 수정 동굴(2지역, 낙석으로 막힘 + 표지판).
- 필드 몹은 돌아다니며 시야 밖에서 다시 나온다 (`respawn` 초).
- 비석(waystone): 조사하면 등록 + 체력 회복. 지도 화면에서 등록한 비석으로 순간이동.

## 2. 조작 (밖 세계)

| 키 | 동작 |
|---|---|
| 방향키 / WASD | 이동 |
| J / Z | 공격 (3타 콤보, 3타째 2배) |
| Shift / K / X | **회피 · 잔상 대시** (0.22초 중 앞 0.18초 무적, 재사용 0.4초 — 난이도 보정 쉬움 +0.06 · 어려움 -0.02 · 악몽 -0.03). 막기는 없다 — 유일한 방어. 적 공격 판정은 0.05초라 맞기 직전 약 0.13초 안에 구르면 피함 |
| 방향키 더블탭 + 유지 | **달리기** (0.25초 안 두 번 → 출발 대시 + 흙먼지, 걷기 ×1.9 · 걸음 애니 속도도 이동 속도에 비례, 손 떼면 짧은 미끄러짐). 달리며 공격 = 달리며 베기, 달리며 회피 = 속도 유지. Esc **달리기 기본** = 항상 달리기 |
| 공격 판정 | 정면 부채꼴: 반경 29px(1.8타일, 한손검 기준 — 무기별 반경 비율은 마을 표와 같음) · 150°(3타 = 마무리 베기: 100° · 반경 ×1.15 · 판정 0.07~0.24초 · 전체 0.38초), 궤적이 같은 반경 · 각도로 그려짐. 2타는 반대 방향으로 정면을 가로지름 |
| L / C / Enter | 조사 · 대화 · 상자 · 레버 · 비석 |
| E | 회복약 |
| **M** | 지도 화면 열기/닫기 (게임 정지) |
| **V** | 미니맵 크기: 작게 → 크게 → 끔 |
| **G** | 목표 전환: 자동(퀘스트) → 시작 마을 → 고대 숲 신전 입구 → 골렘의 방 → 핀 → 안내 끔 |
| Esc | 일시정지 (T: 마을로 귀환) |

지도 화면: 방향키 = 커서 (Shift 빠르게), Enter = 커서 아래 표식을 목표로 (등록한 비석이면 순간이동), P = 핀 꽂기/빼기 (핀이 목표가 됨), G = 목표 전환, M/Esc = 닫기.
키 설정(`__game.ctl.KEYMAP`)의 이동/공격/회피/조사/물약 키를 그대로 따른다. B / N / - / = (BGM 키)는 밖에서도 동작한다.

## 3. 길 안내 · 미니맵 · 지도 (world_nav.js)

- **탐험 안개**: 지나간 곳 주변(필드 8타일, 던전 5타일)만 미니맵/지도에 나타난다. 지도마다 비트로 저장 (`SAVE.explored`).
- **미니맵**: 화면 오른쪽 위, `--ui-alpha` 를 따르는 반투명. 지형 · 길 · 출구 · 마을 · 던전 · 비석 · NPC(! / ?) · 목표 ★ · 핀 · 주인공(방향 화살표) · 경로선.
- **목표**: 자동 = 진행 중 퀘스트의 다음 목표 (없으면 줄 수 있는 퀘스트의 NPC, 그다음 던전 입구). `G` 로 마을/던전/보스/핀/끔 선택, 지도 화면 Enter 로 아무 표식이나 목표로.
- **경로 찾기**
  - 지역 단위: `index.json` 의 지도들을 노드로, 출구(`exit`) · 계단(`stairs_*` + `links`) · 보스 문을 간선으로 하는 Dijkstra → 지금 지도에서 나갈 출구를 고른다.
  - 타일 단위: 지금 지도 안에서 8방향 A* (모서리 끼기 없음). 미리 할당한 typed array 만 쓰고, 한 프레임에 최대 900 노드씩 이어서 계산(증분).
  - 비용: 구멍 · 가시 9, 수풀 2, 잠긴 문 · 철창 · 보스 문은 닫혀 있으면 20 (그래서 경로가 "문까지" 안내한다), 목표가 아닌 출구는 막힘 (실수로 지도를 나가지 않게).
  - 다시 계산: 목표/지도가 바뀔 때, 경로에서 2.5타일 넘게 벗어났을 때(0.25초마다 검사), 3초마다(문이 열렸을 수 있어서). 평소에는 계산 0.
- **표시**: 땅 위 안내 점(흐르는 빛), 목표 지점 링 · ▼, 미니맵 경로선, 목표가 화면 밖이면 화면 끝 화살표 + 남은 거리(m, 1타일 = 1m, 다른 지도 구간 포함), 왼쪽 위 `◆ 목표: … (→ 다음 지역) 76m`.
- **지도 화면 (M)**: 지금 지역(`index.json` regions)의 지도들을 `mapPos` 대로 붙여서 탐험한 부분만 그림 + 표식 이름 + 목표 + 핀 + 경로. 오른쪽에 목표 · 퀘스트 목록 · 등록한 비석 · **왕국 전도(옛 월드맵, 보기 전용, 지금 지역 깜빡임)**.
- 성능: 헤드리스에서 필드 한 프레임(로직 + 길 안내 + 렌더) 평균 약 0.4ms.

## 4. 지도 JSON 형식 (`maps/<id>.json`)

```jsonc
{
  "id": "field00", "type": "field",            // field | dungeon | boss  (world = 보기 전용 왕국 전도)
  "area": 1, "region": "area1", "mapPos": [0, 0], // 지도 화면에서 이 지도가 놓일 위치 (지역 타일 좌표)
  "name": "마을 외곽 — 바람길", "title": {"kicker": "1지역 · AREA 1", "name": "바람길", "sub": "시작 마을 외곽"}, // 첫 방문 카드
  "bgm": "area01_forest", "battleBgm": "battle_champion", "dark": 0.35,   // dark = 던전 어둠 (횃불 · 수정이 밝힘)
  "tileset": "field", "tile": 16, "w": 56, "h": 36,
  "legend": { ".": "grass", "=": "dirt", "~": "water", "T": {"ground": "grass", "deco": "tree"}, "Y": {"ground": "grass", "deco": "tree", "solid": false} },
  "solid": ["~", "#", "T"],                    // 막히는 글자 (legend 의 "solid" 가 우선)
  "spawns": {"default": [27.5, 2.5, "down"], "town": [27.5, 2.5, "down"], "east": [53.5, 19.5, "left"]}, // 들어올 때 위치 (타일, 방향)
  "objects": [ ... ],                          // 아래 표
  "ground": ["TTPTT...", "..."]                // h 줄 × w 글자
}
```

| object type | 필드 | 설명 |
|---|---|---|
| `exit` | x, y, w, h, to, spawn, label | 이 사각형에 들어가면 `to` 지도의 `spawn` 으로. `to: "town"` = 마을로 귀환. 길 안내 간선도 된다 |
| `spawn` | mob, x, y, respawn | 몹 (respawn 초 뒤 시야 밖에서 다시) |
| `champion` | id, mob, x, y | 챔피언 (쓰러뜨리면 `flags[id]`) |
| `sign` | x, y, text | 표지판 (`\n` 줄바꿈) |
| `chest` | id, x, y, loot | 상자 (`[[아이템id, 개수], …]`, 마을 가방으로) — 던전은 `chests: {"x,y": {...}}` 로도 |
| `hidden` | id, x, y, loot | 수풀 속 반짝임 (조사) |
| `heal` | x, y | 쉼터 (체력 회복) |
| `waystone` | id, x, y, name | 비석 (등록 · 회복 · 순간이동 지점, spawn 이름 `ws:<id>`) |
| `npc` | id, x, y, sprite, name, quests, idle | NPC. `quests` = 이 NPC 가 주는 퀘스트 id 순서 |
| `landmark` | id, x, y, name | 가까이 가면 "발견" (지도에 표시) |
| `door_deco` | x, y, sprite | 장식 문 그림 |

던전 글자 오브젝트(legend `obj`): `stairs_up` / `stairs_down` (+ `links: {"stairs_down": {"to", "spawn"}}`), `door_locked` (열쇠 `keys: {"x,y": "열쇠id"}`), `key`, `lever` + `gate` (`gateNeeds: "levers"` = 모든 레버로 철창), `boss_door` (`links.boss_door.needFlags`), `pit`, `spikes`, `torch`, `chest`.
보스 지도: `boss: {kind, x, y, flag, name, absorb, reward, exit: {to, spawn}}`, `bgm2` = 2페이즈 곡.

타일 이름은 `assets/world/world_atlas.json` 의 시트 인덱스. `maps/tilesets.json`: `alias`(없는 이름 대체), `variants`(무작위 변형), `soft`(둥근 경계 · 테두리색), `bridgeUnder`.

### `maps/index.json`
`maps` = 길 안내/지도 화면이 미리 읽는 지도 목록, `regions` = 지도 화면 묶음 (`maps`, `town` 위치, 왕국 전도의 `worldNode`), `destinations` = G 로 고르는 목적지 (`kind`: town / dungeon / boss).

### `maps/quests.json`
```jsonc
{"id": "q_forest_chiefs", "title": "숲의 두 우두머리", "giver": "npc_bori", "requires": [],
 "offer": "…", "progress": "…", "done": "…",
 "need": {"flags": ["champ_boar", "champ_wasp"]},                 // 완료 조건
 "targets": [{"map": "field01", "x": 49, "y": 26, "label": "돌엄니 (챔피언)", "untilFlag": "champ_boar"}], // 목표 표식 · 경로 (조건 충족 시 다음 것)
 "reward": [["potion", 2]]}
```
NPC 머리 위: `!` 줄 수 있는 퀘스트, `…` 진행 중, `?` 완료 보고 가능. 퀘스트를 받으면 자동으로 그 목표로 안내.

## 5. 2 – 10 지역 추가하는 법

1. 그림: `#FF00FF` 배경 16비트 3/4 시점 시트를 `assets_src/world/` 에 넣고 `tools/world_assets.py` 에 자르기 규칙 추가 → `python3 tools/world_assets.py` (타일 16×16, 주인공 ≈ 16×27, 나무 2 – 3 주인공 키, 문 ≈ 1.5).
2. 지도: `maps/field02a.json` … 을 위 형식으로 작성 (생성기를 써도 되고 직접 써도 됨). 지도끼리는 가장자리 `exit` ↔ 상대 지도 `spawns` 로 잇는다. 갈림길 · 랜드마크 · 비석 · NPC 를 둔다. `region` + `mapPos` 를 정해 지도 화면에서 이어 보이게.
3. `maps/index.json` 의 `maps` 와 `regions` 에 추가, 필요하면 `destinations`.
4. 1지역 낙석(바람길 남쪽)이나 다른 지역 끝의 막힌 길을 열어 `exit` 로 연결 (플래그 조건이 필요하면 `exit` 앞에 표지판/보스 문 방식).
5. 몹: `world_mobs.js` 의 `WorldMobs.def` 에 `{hp, spr, h, r, update(m, W, dt)}` 추가. 공격은 반드시 `W.hazard({shape: 'circle'|'ring'|'line'|'all', warn, act, …})` 로 예고 후 판정 (act ≤ 0.18초), 투사체는 `line` 예고 뒤 `W.shot`.
6. 왕국 전도(`maps/world.json`) 의 해당 `area` 노드 `locked: false` — 지도 화면 미니 전도에 표시용.
7. `tools/test_world.py` 에 진행 구간 추가.

## 6. 보스 공략 (이끼 수정 골렘, HP 44)

- 문: B2 의 봉인된 문은 챔피언 2마리(돌엄니 · 여왕 말벌) 처치 후 열림. 들어가면 문이 봉인되어 이길 때까지 못 나감.
- 1페이즈 A 대지 강타(3겹 고리) · B 수정 파편(부채꼴 5줄) · C 이끼 재생(HP 85% 이하, 3번 때리면 끊기고 2.2초 휘청 → 2배 피해). 같은 패턴 연속 없음.
- 2페이즈(50%): 1.8초 무적 연출, 곡 바뀜, D 구르기 돌진(3번 튕김, 매번 선 예고) · E 수정 감옥(틈 2칸 + 2초 후 내려찍기) · F 낙석 11개 추가, 재생은 50% 까지만.
- 필살 「대지 붕괴」: 2페이즈 6초 뒤, 이후 24초마다. 2.6초 카운트 + 화면 전체 붉은 예고 — **기둥 그림자에 숨거나 폭발 순간 회피**로 피함.
- 보상: 대지의 수정(quake) 흡수, 재료 · 하트 조각. 빛의 문 → 신전 입구.

## 7. 테스트

```
python3 tools/test_world.py         # 24항목: 문 → 바람길(카드) → 안내선 따라 NPC → 퀘스트 → 지도 화면 → 지역 넘는 경로 → 숲 → 챔피언 → 신전 → B1/B2 퍼즐 → 보스(패턴 A-F, 2페이즈, 필살 회피) → 비석 → 보고 → 순간이동 → 걸어서 마을 → 성능
python3 tools/record_world_gif.py   # world_milestone.gif (문 → 바람길 → 지도 화면 → 숲 길 → 신전 입구)
```
자동 이동은 게임 안의 경로(`WorldNav.path`)만 읽고 키를 누른다 — 길 찾기가 실제로 작동하는지 검사.
`?worldreset` 로 밖 세계 저장(`localStorage['thor.world.v1']`)을 지운다.
