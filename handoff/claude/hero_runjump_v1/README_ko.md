# hero_runjump v1 (2026-10-20, 사장님 OK · 인게임 세팅)

## 동작
- CMU 모션캡처 127_25 "run jump over" (달리다 넘어 뛰기). 원본: mocap.cs.cmu.edu, BVH는 github.com/una-dinosauria/cmu-mocap.
- 몸을 앞으로 숙이고 공중에서 무릎을 끌어올림, 칼은 뒤로, 망토 펄럭임. 옆모습 10프레임, 왼쪽은 좌우 반전.

## 만든 방법
1. tools/anim/retarget_jump_cmu.py — 이륙 0.22초 전 ~ 착지 0.12초 후 구간을 15개 뼈대로, 주인공 뼈 길이(reftrail2_kp)에 맞춤. 칼 든 팔은 달리기 자세 유지.
2. PixelLab animate-with-skeleton-v3 (시작 그림 = 인게임 달리기 칼 뒤로 든 프레임, seed 903) — 4 크레딧.
3. 팔레트 고정, 잡티 제거, 발 y=189. 공중 구간 프레임 3~12만 사용.

## 인게임 (test128)
- Space = 점프 (물가에서 잠수 가능할 때만 잠수). 터치는 새 "점프" 버튼(달리기 버튼 위).
- 점프 0.5초, 높이 = 주인공 키의 약 2/3 (84 논리px). 달리는 중이면 rjump 모션 + 달리기 속도 1.8배로 날아감.
- 점프 중 공격·회피 입력 무시, 피격/사망 시 점프 취소.
- FEEL.jumpTicks / jumpLogical / rjumpCarry 로 조절.
- tools/anim/apply_runjump_v1.py — hero8_jump.webp 에 rjump_right/left 추가.
