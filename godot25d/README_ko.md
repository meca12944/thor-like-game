# 고도(Godot) 2.5D 시험 (팀장, 2026-10-26)

사장님 10-26: 「3D로 가자」 → 「2.5D 가보고 고도로 가자. 시험 영상 하나 만들자.」

- Godot 4.3 (gl_compatibility). 바닥·경관 = 그록 동쪽 들판 그림 그대로(빛 안 받음), 주인공 = 3D 인형.
- 카메라: 정사영, 45도 아래. 바닥 세로를 1/sin(45도)배 늘려 2D 그림 비율 그대로. 1 단위 = 지도 1칸(16px), 주인공 화면 키 42px.
- 주인공은 임시: three.js 예제 Soldier.glb(믹사모 움직임 Idle/Walk/Run). 칼은 오른손 뼈에 상자로 붙임.
- 찍기 (작업 상자 안, 화면 없이):
  `xvfb-run -a -s "-screen 0 1280x720x24" Godot_v4.3-stable_linux.x86_64 --path godot25d --rendering-driver opengl3 --write-movie out.avi --fixed-fps 30 --quit-after 900`
- 그림은 저장소 test128/assets/world/ch1_east 에서 webp → png로 바꿔 넣음.

## 시험 2: 우리 주인공 3D (Meshy, 2026-10-26)
- 입력: 그록 설정화 `handoff/claude/team/grok_illust_20261024/jp_style/01_hero_sheet.jpg` 정면·옆·뒷면 3장 → Multi-Image to 3D (meshy-6, A자 자세, 30크레딧) → 관절 넣기(5, 걷기·달리기 같이 옴) → 움직임 7개(21): Idle, Left_Slash, Right_Hand_Sword_Slash, Charged_Slash, Roll_Dodge, Stand_Dodge, Hit_Reaction. 합계 56크레딧(잔액 1100 → 1044).
- 파일: art/actions.glb(인형 + 움직임 7), art/walking.glb, art/running.glb. 고도에서 실행 중에 불러와 한 AnimationPlayer에 합침. 칼 = 오른손 뼈(cm 단위)에 상자.
- 열쇠: `MESHY_API_KEY` (환경 변수로만, 저장소에 넣지 않음).

## 시험 3: 하데스풍 (크레딧 0)
- toon.gdshader: 3단 만화풍 빛 + 테두리 빛 + 채도·붉은 안감 올림 / outline.gdshader: 화면 픽셀 두께 외곽선(뒤집은 껍질)
- 가슴 코어 푸른빛(Spine02 뼈, 더하기 빛 판), 칼(칼날·가드·손잡이) + 칼끝 청록 궤적(ImmediateMesh), 카메라 size 17 → 11
- 공격 힘주기(punch): 칼끝 빠르기로 준비(0.8배) → 휘두름(2.1배) → 멈춤 0.09초 + 화면 흔들림 → 회복(1.35배), 눌림·늘림
- 코드 판: main_test3.gd.txt

## 시험 4: 3D인데 2D 느낌 (지금 main.gd)
- 화면을 640×360으로 그려 가장 가까운 칸으로 2배 키움(도트 느낌), MSAA 끔
- 움직임을 1초 12장으로 끊어 재생(AnimationPlayer 수동 advance, 이동·궤적은 부드럽게)
- 외곽선 1px

## 시험 5: 사장님 「4번으로, 모션은 기존 미니 귀여운 버전 캐릭 모션 다 가지고 와」 (10-26)
- 옛 주인공(7093980f) 동작: 서기·걷기·달리기·멈춤·회피대시·점프·달리기 점프·베기 1~3·맞기·크게 맞기·쓰러짐·기술 S1~S3
- Meshy 움직임 8개 추가(24크레딧, 잔액 1020): Regular_Jump(466), Jump_Run(13), Sprint_and_Sudden_Stop(531), dying_backwards(189), BeHit_FlyUp(7), Charged_Spell_Cast(125), mage_soell_cast(129), mage_soell_cast_3(132) → art/actions2.glb
- 미니 비율: 뼈 크기로(크레딧 0) CHIBI = 머리 1.75, 허벅지 0.82, 등 0.9, 팔 0.92 — 진짜 귀여운 얼굴은 미니 설정화로 인형을 다시 만들어야 함

## 시험 6 (10-26): 옛 주인공 비율 — 뼈 크기 머리 1.45·허벅지 0.86·장화 1.25·몸 가로 1.1, 가슴 빛 뺌, 카메라 35도. 한계: 얼굴이 머리카락에 가리고 흐림 → 미니 설정화로 인형 다시 만들기 추천.

## 시험 7 (10-26): 그록 작은그림 v3 → 새 인형
- 입력: handoff/grok_in/주인공_큰그림작은그림_20261026/작은그림 (T자, 정면·옆·뒤 투명 PNG, 흰 바탕으로 합성) → Multi-Image to 3D meshy-6 t-pose(30) → 관절(5) → 움직임 15개(45) → 다시 입히기 4K(10, 원래 UV 유지 → art/base4k.png만 바꿔 끼움). 합계 90, 잔액 940(이 다음 확인).
- 얼굴이 하얗게 날아가던 원인: toon light()에서 LIGHT_COLOR에 PI가 곱해져 있는데 나누지 않고, ALBEDO를 두 번 곱함 → DIFFUSE_LIGHT += LIGHT_COLOR / PI * b 로 고치고 해 1.0·주변광 0.45.
- 도트는 끔(1280×720), 동작 1초 12장은 유지. 외곽선 1.8px.
- 남은 것: Idle 움직임이 고개를 숙임(다른 Idle 11·12로 바꿔 볼 것), 손 피부가 밝음.

## 시험 8 (10-26): 회의 결론 4~6 (교본 handoff/claude/CHARACTER_3D_TEXTBOOK_ko.md)
- 4: 빛 2칸(밝음/그림자) + 보랏빛 그림자(shade_tint 0.7,0.64,0.8), 얼굴은 평평하게(머리뼈 무게×앞쪽 → 꼭짓점 색 r = 얼굴 표시), 얼굴엔 테두리 빛 없음, 최대 밝기 0.95, 색 보정 LINEAR.
- 5: 외곽선은 몸 둘레만 1.8px, 얼굴 안쪽은 0.2배.
- 6: 동작은 매 장면 부드럽게(STEP 0), 공격만 맞는 순간 0.06초 멈칫. 머리는 기본 자세 쪽으로 85% 돌려 고개 숙임 줄임. 뼈 크기 바꾸기(CHIBI)는 뺌.
- 남은 것: 1~3(그록 미니 설정화 → 새 인형, 얼굴 눈·눈썹·입 따로 붙이기), 임시 칼, 회피대시 때 그림자 뒤처짐.

## 시험 9 (10-26): 사장님 「이 작화 그대로」 「7~8등신으로 가야 돼」
- 새 인형: 그록 작은그림 v3(앞·옆·뒤) → meshy-7.1, image_enhancement 끔, 같은 그림으로 색칠(texture_image_urls), 4K (30) + 관절(5) + 움직임 15개(45) = 80크레딧, 잔액 850.
- 얼굴: 설정화 앞모습(art/art_front.png)을 머리 앞쪽에 비춰 입힘(UV2·COLOR.g, 크레딧 0). 고개 15도 들기.
- 고친 버그: 얼굴 표시가 Skin 이름이 비어 안 걸리던 것 → Skeleton 뼈 이름으로 찾음.
- 대각선 걷기 뺌(사장님 「대각선은 뺀다」). base4k.png(예전 인형용) 지움.
- 시험용 카메라: CAMSZ(화면 크기), CAMY(위로), HEADUP(고개 각도) 환경 변수.
- 남은 것: 임시 칼, 달리다 멈춤·회피대시 때 그림자 뒤처짐, 옆·뒤 얼굴은 그림을 안 입힘.

## 시험 10 (10-26): 사장님 「2번(아틀라스) 해 보자」
- 하데스식: 3D 인형(시험 9) 동작 16개를 4방향(아래·오른쪽·위·왼쪽)으로 1초 20장씩 투명 그림으로 찍음 → 동작마다 그림판 한 장(아틀라스)으로 묶음. 크레딧 0.
  - 찍기: `BAKE=1 xvfb-run ... --path godot25d` → godot25d/bake/ (낱장 2705장 + bake.json)
  - 묶기: `python3 godot25d/pack_atlas.py godot25d` → godot25d/atlas/ (*.png + atlas.json, 약 118MB라 저장소엔 안 올림, 위 두 줄로 다시 만듦)
  - 보기: `ATLAS=1` → 3D 인형은 숨기고 같은 시간·방향의 그림 칸을 Sprite3D로 보여 줌(검흔 궤적·멈칫은 숨은 인형 기준 그대로).
- 그림 크기: 1080p 게임 화면과 같은 1칸 = 98px. 회피대시·달리다 멈춤처럼 몸이 움직이는 동작은 제자리로 찍고 게임에서 그림·그림자를 옮김(잘림 없음, 그림자 안 뒤처짐).
- 다음: 얼굴·머리 칸만 손으로 고치기(설정화 얼굴), 그림판 줄이기(칼 칸 따로·크기 맞춤), 실제 게임(test128) 주인공 그림으로 넣을지 사장님 결정.
