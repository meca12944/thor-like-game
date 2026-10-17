# 시작 마을 A — map notes

Runtime: `town_a.js` (hooks marked `[town_a]` in `tools/game.template.html`). Data and art: `assets/level.json` → `ta`, `assets/town_a/*`.
Build: `python3 tools/town_a/build_town_a.py <town dir>` (procedural painted pixel art, 3/4 front view, A=0.6 art px per world px), then `tools/build.py`.
Labelled overview: `python3 tools/town_a/overview.py <town dir> /tmp/ta/overview_raw.png out.png`.

Outdoor map: x -1300..2500, y -1050..790 (3800×1840 world px, about 3×2.5 screens). The camera clamps to the current room. Interiors are separate rooms placed east of x 4400.
Doors: walk up into a door to enter; walk out through the bottom gap to leave. Trapdoors use the interact key. Locked doors show a message.

| Where | What |
|---|---|
| 분수 광장 (777,415) | fountain (dive: 생명의 진주 + A6 「요람의 장부 조각」 flag), 엘스베트, 하수로 쇠창살, 게시판, 경종탑, 빗물 웅덩이 (dive) |
| North of the plaza | 대장간 옆 이끼 낀 우물 (dive), 대장간 (브란트, shop opens on the 대장간 tab, trapdoor → 지하 창고 with a cracked wall) |
| 바렌의 수련장 (SW sand yard) | 바렌 도장 (interior + scroll), 사범의 집 (interior + unsent letter), 바렌 (tutorial), dummies / target / rack, tame practice slimes and the boar champion kept inside the yard |
| West | 하로의 농가 (locked), carrot and pumpkin fields, scarecrows, 세레스의 약초 오두막 (locked), herb beds, west stairs |
| North terrace | 필멸자의 집 (interior + foundling cradle basket), 촌장 오스왈드의 집 (interior, trapdoor → cellar with the 세금 상자 / 요람의 장부), chief's pond (dive), back alley |
| East · 장인 거리 | 도구상점 「보따리」 (미라벨, shop), 리네트 재봉소 (interior, 리네트/nabi), bell tower, stall, 2 locked houses, 엘스베트의 집 (locked), magpie-nest wall, tailor back yard |
| South | palisade, 남문 · 바람길 gate (x 560..800, y ≥ 690) → world.js → 시작의 숲. HUD: minimap + 「남문 → 시작의 숲」 arrow with distance; M: town map + world map |

Chests: tailor-yard basket, scarecrow haystack, gate supply crate (easy) · under the mossy bench (hidden, sparkles up close) · pond gold chain chest (oath 8), granny alley (after the area-1 boss), forge cellar crack (bomb or ore pick) (return later).
A3: three of 토비's wooden toys (behind the smithy · chief's fence · fountain flower bed) → 토비 gives a 하트 조각.
Save: localStorage `townA.v1` (opened chests, flags; skipped with `?nosave`).
