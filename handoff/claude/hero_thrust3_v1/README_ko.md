# 주인공 3타 전부 찌르기 v1 (2026-10-20, 사장님 지시 "모든 공격 찌르기로 새로" · 저장만, 게임 미적용)
- 1타 빠른 찌르기 / 2타 한 발 들어가며 찌르기 / 3타 크게 웅크렸다 길게 뛰어드는 찌르기. 각 타는 앞 타의 끝 자세에서 시작.
- 방향: → ↘ ↗ 새로 그림, ← ↙ ↖ = 좌우 반전. 그림에 검흔 없음, 리네트식 빛줄기(trail.json)는 코드가 그림.
- 방법: 방향마다 "찌른 자세" 그림(edit-images-v2, pose/) → 그 그림을 첫 장으로 뼈대를 거꾸로(찌른 자세→시작) animate-with-skeleton-v3 → 뒤집어 재생.
  칼이 수평으로 유지되고 칼이 한 자루로 나옴. ↗ 는 옆 동작 변환 대신 ↗ 자세 뼈대를 직접 섞어 만듦(tools/anim/atk3/ne_thrust.py).
- 틱: clips.json, 타격 틱 hit.json(9/10/14). 도구: tools/anim/atk3/thrust3.py, anchor_rev.py, ne_thrust.py, tools/anim/notrail/linette_trail.py
- 크레딧(이번 작업): 약 93 (첫 시도 29 실패분 포함, 자세 그림 2장 20, 다시 그리기 약 43, 뼈대 추정 약 1.3).
