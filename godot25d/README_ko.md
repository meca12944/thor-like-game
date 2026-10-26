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
