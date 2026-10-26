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
