---
name: add-field
description: 「필멸자」 test128에 들판/던전 맵을 추가하거나 지역 들판을 다시 만들 때 쓴다 ("맵 추가", "지역 열어", "들판 만들어"). 맵 JSON 형식, 월드맵 연결, index.json 등록까지.
---
# 맵 추가 (test128/maps)

## 빠른 길: 지역 들판 2~9 재생성
`cd test128 && python3 tools/gen_region_fields.py` — `TH` 표(지역 이름·바닥 타일·벽·장식·물·BGM)를 고치고 다시 돌린다. world.json 의 area 노드 열기, index.json 등록도 같이 한다.

## 직접 만들 때 (맵 JSON)
- 필수: `id, type('field'|'dungeon'|'boss'), area, region, mapPos, name, title{kicker,name,sub}, bgm, tileset('field'|'dungeon'), tile:16, w, h, legend, solid, spawns, objects, ground`
- `ground` = 문자열 줄(가로 w, 세로 h). `legend` 글자 → 타일 이름(`assets/world/world_atlas.json` sheets.*.index) 또는 `{"ground":..,"deco":..}`. 장식: tree pine stump boulder rocks bush crystal pillar rubble tablet fence mushrooms.
- `solid` = 막히는 글자 목록. 물·절벽·장식 글자를 넣는다.
- `spawns` = 들어오는 위치 `{"default":[x,y,"right"], ...}` (타일 좌표, .5 = 칸 가운데).
- `objects`: `exit{x,y,w,h,to,spawn,label}` (to:'world' + spawn:'area3' 이면 월드맵 그 노드로), `spawn`(몹), `sign`, `chest{id,loot}`, `heal`, `waystone`, `champion`.
- 연결: world.json 노드 `scene` 에 맵 id, `locked:false`. 지도 화면용으로 `maps/index.json` 의 maps / regions 에 추가.

## 확인
- `?go=<맵id>` 로 바로 들어가 본다: `https://meca12944.github.io/thor-like-game/test128/?go=field05` (머지 후) 또는 로컬 서버.
- ingame-test 스킬로 녹화해서 보낸다. 라이브 `/town/` 은 절대 건드리지 않는다.
