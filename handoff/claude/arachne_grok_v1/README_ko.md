# 아라크네 그록판 v1 (4번방, 2026-10-24, 사장님 「아라크네도 이걸로. PixelLab 써도 되니 회의 의견으로」)
- 원본: 그록 `raw/arachne_4view.jpg`, `raw/arachne_motion.jpg` (팀장 linette-8dir 7e4b2a17)
- `cut.py`: 회색 배경·바닥 그림자 지우기(테두리에서 이어진 무채색만) + 원래 도트(약 2.5px)로 줄이기 → `clean/` (키 약 153px, 256칸, 다리 끝 y249)
- 노출: 지금 게임 그림 수준을 넘지 않게 앞·옆 모습 가슴에 찢어진 붉은 천 덧입힘 (PixelLab edit 2번, 20) → `clean/front_cov.png`, `side_r_cov.png`
- 옆 걷기: 걷는 자세 1장(edit 10) → 한 바퀴 8장(animate 8) → `build.py walk` (그림 도구가 넣은 글자 조각 지움) → `strips/c1_boss_arachne_g_walk.png`
- 크기: 게임에서 주인공(30 field px)의 3.2배 = 96 field px. 그림 키 153px → `anim.F` ≈ 160 (256칸 기준). 새 주인공 키가 정해지면 이 숫자만 바꿈.
- 미리보기: `walk_v1.mp4` (`preview.py`, 주인공 옆)
- 크레딧: 가슴 천 20 + 걷기 18 = 38
