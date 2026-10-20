# 주인공 3타 검흔 제거 + 리네트식 검흔 (2026-10-20, 저장만 · 게임 미적용)
- 원본: main `test128/sandbox/assets/hero_sbx.json` 의 최종 공격 hit1 / hit2 / hit3s(하늘색 반달) × 6방향(→ ← ↘ ↙ ↗ ↖).
- 검흔 제거(`tools/anim/notrail/strip.py`): 반투명 하늘색 반달, 흰 반달·속도선(칼날보다 두꺼운 밝은 덩어리), 떠 있는 조각 삭제.
  옆 1타 마지막·2타 첫/마지막 장은 칼 전체가 흰 빛에 덮여 있어 같은 찌르기의 바로 앞 장으로 바꿈. 옆 3타는 원래 칼날이 짧게 잘려 있음.
- 리네트식 검흔(`tools/anim/notrail/linette_trail.py`): 타격 순간 칼끝·칼 방향을 찾아(trail.json) 칼끝 앞으로 빛줄기(리네트 fx.py 그대로).
  1타 작게, 2타 크게, 3타 두껍게. 그림에는 굽지 않음 → 게임 코드가 trail.json 으로 그림.
- frames/<hit>_<dir>/NN.png (256 캔버스, 발 128,189), clips.json = 틱, 영상 hero_3hit_linette_trail.mp4 (실제 속도 2번 + 1/3).
