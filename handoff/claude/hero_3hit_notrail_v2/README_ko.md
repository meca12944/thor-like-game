# 주인공 3타 v2: 다시 그리기 + 리네트식 검흔 (2026-10-20, 저장만 · 게임 미적용)
- v1 문제(사장님): 얼굴 뭉개짐, 팔 투명, 도트 크기 들쭉날쭉. 원인은 저장본 자체(장마다 크기를 바꾼 그림이 섞임, 얼굴·어깨가 빠진 장, 옆 3타 칼날 삭제).
- 고친 방법: 저장본 각 장의 뼈대를 추정(estimate-skeleton, 71장)해 동작은 그대로 두고, 깨끗한 회전 그림에서 PixelLab animate-with-skeleton-v3 로 다시 그림
  (→ ↘ ↗ × 1·2·3타 = 9개, seed 81). ← ↙ ↖ = 좌우 반전. 회색 얼룩은 코드로 제거. 검흔은 그림에 없음.
- 리네트식 검흔: trail.json(타격 장, 칼끝, 방향) → 게임 코드가 칼끝 앞으로 빛줄기를 그림. 영상 hero_3hit_linette_trail_v2.mp4.
- 크레딧: 뼈대 추정 71 x 0.1 + 그리기 9 x 3 = 약 34.1.
- 도구: tools/anim/notrail/retrace.py, linette_trail.py, tools/anim/atk3/clean.py
