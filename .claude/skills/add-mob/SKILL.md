---
name: add-mob
description: 「필멸자」 test128에 몬스터를 추가하거나 기존 몹의 그림·AI를 바꿀 때 쓴다 ("몹 추가", "몬스터 넣어", "이 몹 인게임"). 스트립 가져오기 → world_mobs.js 등록 → 맵 배치 → 인게임 테스트까지.
---
# 몹 추가 (test128)

**먼저 `handoff/claude/MONSTER_TEXTBOOK_ko.md`(몬스터 교본)를 읽는다** — 만드는 순서(0부)와 공격 기준표(1부: 역할 1개 + 겨냥 공격 2~3개, 경고, 공격 뒤 빈틈). 이 스킬은 파일·코드 손순서만.

규칙: 작업은 브랜치 → PR. main 머지는 주인이 "인게임 넣어/적용해" 한 뒤에만. 이펙트(검기·투사체 빛)는 그림에 굽지 말고 코드로 그린다. PixelLab 쓰면 작업마다 크레딧 보고.

## 1. 그림 고르기
- **대기 8장 + 공격 12장 스트립**(3번방 형식, `art/mobs/idle/sheets`, `atk/`, manifest): `python3 tools/anim/mobs47/import.py <art/mobs/idle> test128` → `test128/assets/mobs47/<id>_idle.webp / _atk.webp` + `mobs47.json`. 왼쪽 보는 그림은 import.py 의 `MIRROR` 에 넣는다 (공격은 코드 돌진으로 대체됨).
- **PixelLab 걷기/공격/사격 스트립**(펠트 형식, 256칸): `test128/assets/mobs_felt/<id>_{walk,attack,shoot,...}.png`, `felt({...})` 로 등록 (world_mobs.js 의 c1_* 참고).

## 2. 등록 (test128/world_mobs.js `def`)
- 스트립 몹: `<id>: s47({ name, area, h, ai, fx, pat, fly, sp })`
  - `h` = 몸 키(필드 px) = 스트립 몸 높이(mobs47.json body) × 0.2. 주인공은 30.
  - `ai`: `melee`(앞 원) / `shoot`(조준선→탄) / `charge`(조준선→돌진) / `aoe`(자기 주변 원) / `drop`(주인공 발밑 원)
  - `fx`: 탄 종류 `beam arrow firearrow spike ink bolt feather orb` (world.js FELT_SHOT 에서 코드로 그림), drop/aoe 는 `rock sand bolt poison shock wave`
  - `pat`: `ring`(8방향) / `fan`(3갈래), `sp: 0` = 고정형
- HP·피해는 area 로 자동 (50+14×(area-1), 5+0.6×(area-1)).
- **모든 피해 공격은 예고 먼저** (W.hazard warn / lineTele). 예고 없는 공격 금지 — 회피대시로 피할 수 있어야 함.
- 기존 AI에 새 그림만 입힐 땐 `def[k].s47 = '<strip id>'`.

## 3. 배치
- 맵 JSON `objects` 에 `{"type":"spawn","mob":"<id>","x":..,"y":..,"respawn":30}`.
- 지역 들판 2~9는 `python3 test128/tools/gen_region_fields.py` 가 `a{지역}_*` 몹을 자동 배치 (다시 돌리면 맵 재생성).

## 4. 확인
- `node -e "new Function(require('fs').readFileSync('test128/world_mobs.js','utf8'))"` 문법 확인.
- ingame-test 스킬로 녹화 → MP4 를 주인에게 보내고 짧은 한국어로 보고.
