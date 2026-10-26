# 고도(Godot) 2.5D 시험 (팀장, 2026-10-26)

사장님 10-26: 「3D로 가자」 → 「2.5D 가보고 고도로 가자. 시험 영상 하나 만들자.」

- Godot 4.3 (gl_compatibility). 바닥·경관 = 그록 동쪽 들판 그림 그대로(빛 안 받음), 주인공 = 3D 인형.
- 카메라: 정사영, 45도 아래. 바닥 세로를 1/sin(45도)배 늘려 2D 그림 비율 그대로. 1 단위 = 지도 1칸(16px), 주인공 화면 키 42px.
- 주인공은 임시: three.js 예제 Soldier.glb(믹사모 움직임 Idle/Walk/Run). 칼은 오른손 뼈에 상자로 붙임.
- 찍기 (작업 상자 안, 화면 없이):
  `xvfb-run -a -s "-screen 0 1280x720x24" Godot_v4.3-stable_linux.x86_64 --path godot25d --rendering-driver opengl3 --write-movie out.avi --fixed-fps 30 --quit-after 900`
- 그림은 저장소 test128/assets/world/ch1_east 에서 webp → png로 바꿔 넣음.
