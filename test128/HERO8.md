# test128 — 새 주인공 모션 (8 동작 × 8 방향)

- 그림: `char_v4/pixellab/hero/vid/px_*` (작업 폴더) → `tools/hero8_atlas.py` → `assets/anim/hero8_{walk,run,atk,dash,hurt,cast}.webp` (무손실 WebP, 투명 여백 잘라 묶음) + `hero8.json` (index.html 에 `const H8` 로 들어 있음).
- 방향: **그림은 4방향** (오른쪽 · 아래 · 위, 왼쪽 = 오른쪽 좌우 반전). 이동 · 공격 판정 · 대시는 8방향, 대각선은 옆모습(좌/우) 그림. 기준점 = 각 클립 0번 프레임의 발끝.
- 걷기 / 달리기: 한 주기(두 걸음) **전체 프레임**(걷기 옆 21 · 앞 19 · 뒤 24장, 달리기 12 · 13 · 13장)을 이동 거리에 맞춰 재생 — 한 주기 = 걷기 84 · 달리기 119 월드 px (발 미끄러짐 측정값, 215 / 408 px/s 에서 약 1.1 / 1.5 틱/장). 위상은 걷기 · 달리기 · 방향 전환에도 이어짐. 주소 `?walkcyc=` · `?runcyc=` 로 조절. 서 있을 때 숨쉬기(상체 0 – 2px, 2.4초 주기).
- 3연타: 승인된 0.6초 (1타 8틱 · 2타 8틱 · 3타 20틱, combo_fast06.py 프레임). 다른 무기는 같은 비율로 줄임. 이어 치지 않으면 짧은 마무리 동작(이동하면 바로 끊김).
- 대시 v2: 14틱(0.23초) 동안 150px(1080p 기준) 앞쪽에 몰린 이동, 예비 동작 없음, 청록 잔상 5개 + 속도선 + 출발점 번쩍임, 3틱 회복.
- 피격: 맞으면 hurt (20틱). 스킬(1 · 2 · 3): cast — 73장 중 2장마다 1장을 **고른 속도**(3틱/장, 짧은 스킬은 최소 1.5틱/장까지 균일하게)로 예비동작 → 구슬 모으기(긴 스킬은 왕복 반복) → 발사, 스킬이 끝나면 마무리 동작(이동하면 끊김). Q 광역 = 발사 + 마무리. 사망은 옛 128 시트.
- 필드 · 던전(world.js)도 같은 프레임을 씀 (공격 판정 방향은 4방향 그대로).
- `?hero8=0` = 예전 4방향 128 주인공으로 비교.
- 시험: `python3 tools/test_hero8.py` (헤드리스 Chromium, 8방향 걷기 · 달리기 · 연타 · 대시 · 캐스트 · 피격 · 필드 · 콘솔 오류).

## 2026-10-18 hero v3 (교체)
- 그림: idle4 · walk5(앞으로 숙인 걷기) · run4 · 3연타 combo3_arc(+검기 fx 레이어) · 캐스트 S1/S2/S3(cast_proj/wave/slam + 마법진 뒤/앞 레이어) · dash4 · hurt4. 4방향(왼쪽 = 오른쪽 반전), 8방향 이동의 대각선은 가까운 4방향(hero.face).
- 기준점 = 고정 루트(발): 224x176 → (112,160), 연타 304x256 → (152,200), 마법진 288x248 → (144,208).
- 연타: combo3_arc.json 그대로 — 1타 20 · 2타 26 · 3타 39틱, 타격 6/28/59, 캔슬 16/41/79 (창 안에서 공격 입력 = 바로 다음 타). 적중 시 엔진 히트스톱 4/6/8틱.
- 캐스트: 스킬 슬롯 1/2/3 → S1/S2/S3 (슬롯 번호 % 3).
- 도구: tools/hero_v3_atlas.py → tools/patch_hero_v3.py, 시험 tools/test_hero_v3.py. 사망은 예전 128 시트.

## 2026-10-18 공격 범위
- 1~3타 판정 = combo3_arc 검기 도달거리 +10%(월드 px, hero.y-8 기준, 3/4 시점 y×0.75) 부채꼴. 반경 오른쪽/왼쪽 161/123/177, 아래 184/133/203, 위 186/158/205, 각도 150/170/160°. 타격 틱 그대로.
- 디버그: 주소 ?hitbox=1 또는 F2 = 판정 표시(노랑 = 대기, 빨강 = 판정 중).

## 2026-10-18 공속 · 검기 · 뒤 대기
- 연타 0.75x: 1타 3/2/3/6, 2타 4/2/4/8, 3타 7/2/6/12틱 (예비/스미어/히트스톱/팔로). 타격 5/20/41, 캔슬 12/29/55, 이어치기 약 54~57틱. 히트스톱 3/4/6.
- 검기 combo3_ref: 반투명 RGBA(칼끝 85% → 꼬리 15%), 가는 흰 심 + 반투명 청록 몸통 + 밝은 바깥선, 알파로 2~3프레임 사라짐, lighter 합성 옅은 빛(0.35).
- 판정 반경 재계산: 오른쪽/왼쪽 161/123/177, 아래 185/136/204, 위 186/182/205.
- idle_up: walk4_up 007에서 픽셀 편집한 숨쉬기 12프레임(8틱).

## 2026-10-18 hit2 blob fix, field hitboxes, idle_up stance, thinner trail
- RIGHT hit2 contact frames (9,10): stray head-like blob near the legs pixel-edited out (left = mirror). Other separated components in all combo frames = blade/hilt pieces (legit).
- Field/dungeon (world.js): hero basic attack hits 1-3 use the town H8HB table (per hit/direction, x29/96 town->field px, weapon scale kept, enemy margin r+h*.2). `?hitbox=1` / F2 draws the sector + enemy margins in the field too.
- idle_up: left leg moved 4px inward (feet together like other idles); 3% checks unchanged (H -2.2%, headw -2.7%, shw 0%).
- Sword trail thinner/more transparent: widths ~55% (hit3 head 16px), alpha head 55% -> tail 5%, fade frames 35/18/6%, 1px white core, additive glow 0.20. Gif: v3/preview/combo3_ref_vs_thin_4dir.gif.
