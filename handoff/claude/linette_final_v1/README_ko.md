# 리네트 모션 현황 (2026-10-20, 사장님 "세팅" → main PR #19, live test128/linette.html)

- 캐릭터: PixelLab `7e26e0f3`, 117px(여자라 주인공보다 작게), 256 캔버스, 발 기준점 (128,189)
- 방향 규칙: 위·아래(남북) 그림은 쓰지 않음. 위/아래를 볼 때는 대각선 ↘(down)/↗(up)을 쓰고, 왼쪽 성분이면 좌우를 뒤집음(downl/upl). 좌우는 옆모습이고, 왼쪽 = 오른쪽 반전.
- 아틀라스 `atlas/linette8.json` + 시트 11장. 게임 쪽 사본은 `test128/assets/anim/linette8*`.

| 동작 | 옆 | 대각선 | 출처 |
|---|---|---|---|
| 대기 | v1 텍스트 | 주인공 대각선 모션을 뼈대로 입힘 | linette_moves_v1 / linette_skel_v1 |
| 걷기 | 모캡 뼈대(07_01) | 주인공 대각선 | skel |
| 달리기 | 모캡 뼈대 + 손 허리·팔 뒤로(1번) | 주인공 대각선 + 리네트 팔 | skel run_east_back |
| 대시 | 자세 뼈대 | 주인공 대각선 | skel |
| 점프 | 주인공 점프 입힘 | 주인공 대각선 점프 | skel jump_* (높이는 코드) |
| 피격·사망 | 뼈대 / v1 | 없음(옆모습 사용, 주인공과 같음) | |
| 스킬 | v1 텍스트 | v3 대각선 | 마법진·불은 주인공 자산 hero8_castfx / hero8_castfire |
| 1·2·3타 | 찌른 자세 end_frame, 2타는 1타에서 팔만 바꾼 연타 | 대각선 그림 | linette_thrust_v1 / skel swap·atk2chain |

- 공격 흔적: 코드로 그림(`fx.py`, 샌드박스에서는 JS로 옮김). 바늘 끝과 방향은 `thrust`에 있고, 3타는 두 줄.
- 다시 만들 때: `assemble.py` → `polish.py` → `build_atlas.py` → `thrust_fx.py` 순서로 돌린 뒤 atlas를 test128로 복사하고 html의 `?v=` 캐시 번호를 올림.
- 리네트 PixelLab 누적: 약 770(시행착오 포함). 마지막 대각선 작업은 잔액 차이로 확인: 32.6 + 14.9.
