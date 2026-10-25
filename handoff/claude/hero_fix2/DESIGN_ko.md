# 새 주인공 동작 설계표 (10-25 회의 2차, 모션 = 주인공 동작 책임)

사장님 결정: 「옛 주인공으로 돌리지 마. 교본 꼼꼼히 보고 검수, 그록에서 넘어온 것 확인해서 전부 다시.」
근거: 모션 교과서 0부·1부(특히 긴급회의 규칙), main world.js 숫자.

## 0. 코드에서 확인한 사실 (main world.js)

| 동작 | 코드 길이 | 출처 | 재생 방식 |
|---|---|---|---|
| 회피대시 | 20틱 | 27줄 DG `durTicks: 20` (엘든링식 0.33초, 무적 13틱) | 비례 재생. `seq(L, t/rollDur × 합)` → 그림 틱은 비율 |
| 점프 | 42틱 | 1620줄 JUMP: 웅크림 4 + 공중 30 + 착지 8 | 비례 재생 |
| 공격 1·2타 | 30틱 | 50줄 ATK.dur 0.50. 검기 활동 8~15틱 (GK_FAN t0 3 + SW8 5) | 비례 재생. **단 몸 그림은 `?atkbody=1`일 때만**(1587줄 ATK_BODY). 평소에는 서기·걷기 몸 + 코드 칼·몸 반동 |
| 공격 3타 | 45틱 | 51줄 ATK3.dur 0.75. 검기 11~21틱 | 위와 같음 |
| 맞기 | 20틱 | 1561줄 `hero.inv > .67` 동안(1.0 → 0.67 = 0.33초) | 절대 틱 |
| 쓰러짐 | 끝까지 | `S.deadT × 60` | 절대 틱 |
| 걷기·달리기 | 보폭 | gait walkCyc 74.4 · runCyc 87.3, 다리 빠르기 = 속도 × 0.9 | 거리 비례 |

→ **평소 게임에서 공격 그림 1~3타는 안 나와요.** 팀장 장표에서 보인 「정지 그림 공격」은 아틀라스 내용이에요. 게임에서는 서기 몸 + 코드 칼이 보여요. 공격 몸 그림을 쓰려면 ATK_BODY를 켜야 하고, 그때 아래 공격 칸이 필요해요.

## 1. 동작별 설계 (보이는 장 최소 3틱, 치는 칸 = 코드 활동 시작)

| 동작 | 방향 | 장 수 | 장마다 틱(합) | 치는 칸·가운데 | 지금 있는 그림 | 모자란 것 → 어디서 |
|---|---|---|---|---|---|---|
| 서기 | ↓↘→↗↑ | 1 + 코드 숨쉬기 | 60 | — | 걷기 중 발 모인 장(PixelLab 걷기) | 없음 |
| 걷기 | ↓↘→↗↑ | 8 (↑ 6) | 6×8 | — | PixelLab(B·앞머리) | 없음 |
| 달리기 | ↓↘→↗↑ | 8 | 4×8 | — | PixelLab | **↓·↑ 무릎이 낮아 걷기처럼 보임** → 그록 원본 또는 PixelLab 핵심 자세 2×18 = 36 |
| 회피대시 | ↓↘→↗(↑=↗) | 6 | [3,3,6,3,3,2] = 20 | 낮은 자세(3번째)가 6~12틱 = 무적 13틱 가운데 | PixelLab 핵심 + 사이 장 | ↘↗ 사이 장이 깡충 → **그록 「낮은 회피대시」 원본(그리는 중)** 칸 맞추기 0 |
| 점프 | ↓↘→↗ | 7 | [4,4,4,10,6,6,8] = 42 | 가장 높은 칸 12~22틱(공중 가운데 19) | PixelLab | 없음(틱만) |
| 달리기 점프 | → | 6 | [4,4,14,6,6,8] = 42 | 공중 칸 8~22 | PixelLab | 없음(틱만) |
| 맞기 | ↓→↑ | 3 | [4,10,6] = 20 | 맞는 칸 0틱 | ↓·→ 1장, ↑ 3장 | **그록 「맞기」 원본(그리는 중)** → 맞는 순간·버팀·돌아옴 |
| 쓰러짐 | → | 9 | [3,3,3,3,3,4,4,6,60] | — | PixelLab 9장 | 없음 |
| 공격 1타 | ↓→↑ (↘↗=가까운 쪽) | 4 | 서기→예고 8 · **치기 8**(8~15) · 따라 돌기 7 · 복귀 7 = 30 | 치는 칸 8틱 | 그록 자세 1장 + 사이 장 0~3 | **그록 원본 4장 × 3방향** |
| 공격 2타 | ↓→↑ | 4 | 같음 30 | 8틱 | 1~2장 | 그록 원본 |
| 공격 3타 | ↓→↑ | 4 | 예고 11 · **치기 10**(11~21) · 따라 돌기 12 · 복귀 12 = 45 | 치는 칸 11틱 | 1~3장 | 그록 원본 |

## 2. 그록 원본 칸 맞추기 계획 (오는 대로, 크레딧 0)
1. `motion_lab/grok_hero/faceplate/snap.py`처럼 그록 그림을 10×10 칸이면 1배로, 그림체면 `cut.py`처럼 자른 뒤 **걷기와 같은 배율**(얼굴 맞추기 0.95~1.05)로 맞춰요.
2. 발 189, 몸 가운데 128을 동작 하나에 한 번만 맞춰요. 몸에서 떨어진 조각(먼지·글자)은 지워요.
3. 144로 줄이고(`final144.py`), 얼굴 B는 동작 전체 겹침 80% 이상일 때만 찍어요.
4. **grip 찍기** (`grip_make.py`, 검흔 담당): 새 장마다 칼 손잡이 [dx,dy,deg] → `grip.json`(동작 이름 형식, apply.py가 칸으로 바꿈). 빈 손이라 grip 없으면 코드 칼이 안 붙음.
5. 아틀라스(`build_atlas.py`) → hero_check 빨간 칸 0 → 게임 안 영상(1배·0.25배, 몹 쳐서) → 4번방 검수 → 팀장 → 사장님.

## 3. 그록 부탁 글 초안 (공격 36장)
```
Please draw ATTACK BODY POSES for the same young swordsman (long black hair, dark coat, bronze shoulder armor, dark red cape lining, brown boots; same proportions as the walk sheet, about 5.5 heads tall).
BODY ONLY: empty hands as if holding an invisible sword (the sword and all slash effects are drawn by the game code). NO sword, NO slash trails, NO glow, NO motion lines, NO dust.
3 combo hits x 4 poses each, in 3 views (front facing the viewer / side facing right / back view):
 - hit 1 (horizontal slash right-to-left): ready stance -> wind-up (arm pulled back across the body) -> strike (arm fully extended forward-left) -> follow-through
 - hit 2 (horizontal slash left-to-right): wind-up -> strike -> follow-through -> recover
 - hit 3 (big finishing slash, wide arc, step forward): wind-up (body twisted back) -> strike (lunge, arm extended) -> follow-through (body turned) -> recover
ALSO 2 RUNNING KEY POSES (body only): front view running toward the viewer and straight back view running away — the driving knee lifted HIGH (thigh near horizontal), the pushing foot clearly off the ground behind, arms pumping with elbows bent; feet movement at least 15 game pixels between the two feet.
Same character size in every pose (feet on the same ground line), true pixel art on a grid where 1 game pixel = exactly 10x10 image pixels, transparent PNG (not JPG), one row per hit and view, no text.
```

## 4. 2단계 (크레딧 0, 브랜치 claude/hero-fix2)
- 회피대시 [3,3,6,3,3,2], 점프 [4,4,4,10,6,6,8], 달리기 점프 [4,4,14,6,6,8], 맞기 ↑ [4,10,6]으로 아틀라스 틱만 바꿔요.
- 공격: ATK_BODY는 끄고(지금처럼 코드 공격) 그록 원본이 올 때까지 둬요.
- hero_check(2번방) 빨간 칸 0 + 게임 안 영상.

## 4-1. 연습장 (교과서 0부 11절)
- hero-fix2에서 `python3 tools/sandbox/build_hero_game.py test128/sandbox/assets` 다시 뽑음(48동작 249칸).

## 4-2. 검수 목록 번호별 숫자 (4번방 CHECKLIST, 잰 것 `check_numbers.json`, 144 그림)
| # | 결과 | 숫자 |
|---|---|---|
| A1 | ○ | 모든 동작 출발 = 그록 걷기 시트(방향별) → PixelLab 핵심 자세. 글만으로 뽑은 장 0 |
| A2 | △ | 걷기 ±1~2.4%, 달리기 ±0.7~2.9%(↗ ±8.6), 대시 ±4~15%·점프 ±3~10%는 웅크림 자세 차이(크기 아님). 동작 하나에 한 번만 맞춤 |
| A3 | ○ | 걷기 5방향 키 141~148(얼굴 맞추기 0.98~1.04) |
| A4 | △ | 얼굴 B: 걷기·달리기 살색 넓이 원래 −8~0%. 새 동작은 도장 안 찍음(겹침 80% 미만) |
| A5 | △ | 땅 디딘 장 발 188~189 ○, **atk1_up 192(3px 땅 밑) ×** → 고침 필요 |
| A6 | ○ | 옆 걷기 머리 4px·좌우 7.6, 달리기 머리 6~8(달리기 발 폭은 hero_check로) |
| A8 | ○ | 청색(검기) 칸 0, 흰 칸은 눈 반짝임 0~20 |
| A10 | ○ | 8방향 표 `../hero_grok_v1/ingame_8dir_table.png` 빈 칸 0 |
| B1 | ○(fix2) | 대시 [3,3,6,3,3,2]→실제 3~7틱, 점프 4.1틱 이상, 맞기 20. 공격 몸은 ATK_BODY 꺼짐(안 나옴) |
| B2 | △ | 맞기 1장 20틱·점프 공중 10틱 → 코드 움직임(맞기 밀림·기울기)만 있음, 점프는 망토 흔들림 없음 |
| B4 | ○ | 코드 DG durTicks 20·iframe 13 (옛 17/9 아님), 낮은 자세 6~12틱 |
| C1 | ○ | 1·2타 활동 8~15, 3타 11~21 (GK_FAN t0/t1 + SW8 5) |
| C2 | × | 공격 몸 예고 자세 없음 → 그록 공격 원본 36장 뒤에 |
| 나머지 C3~E3 | 검흔·2번방 표와 합쳐서 |

## 5. 크레딧 예상
- 0: 틱 다시 나누기, 그록 원본 칸 맞추기
- 36: 정면·뒷면 달리기를 그록이 안 그리면 PixelLab(쓰기 전에 다시 물어봄)
