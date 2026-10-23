# 기존 주인공(망토) 모션 다시 그리기 v1 (2026-10-22)

주인공2(새 디자인)는 봉인, 기존 주인공을 고침. 2번방 최종 방식(핵심 자세 1장 + 한 주기 8장, 모션 교과서 부록 A 8번).

| 고친 것 | 방법 | 크레딧 |
|---|---|---|
| 아래로 달리기 (옆보며 웅크림 → 앞보며 달림) | keys/run_down_key + cyc_run_down | 18 |
| 위로 걷기 (칼 옆으로 고정 → 아래로 내림) | keys/walk_up_key2 (1번 다시) + cyc_walk_up | 28 |
| 앞으로 걷기 (다리 안 움직임) | keys/walk_down_key + cyc_walk_down | 18 |
| 옆 대시 4장 → 10장 | tw_dash_a / tw_dash_b (원래 4장 사이 채움) | 8 |
| 맞기 앞·뒤 새로 | keys/hurt_down_key, hurt_up_key + tw_hurt_* | 28 |
| 합계 | | **100** (잔액 8394.95 → 8294.95) |

- `pl.py` PixelLab 호출(키는 환경변수), `assemble.py` 크기·발 맞춰 `test128/assets/anim/hero8_fix.webp` + index.html H8 아틀라스 수정.
- 왼쪽은 오른쪽 좌우 반전(H8.left=0)이라 오른쪽만 그림.
