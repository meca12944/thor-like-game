# hero_afterimage v2 (2026-10-20, 사장님 OK · 저장만, 게임 미적용)
- 1·2타(모든 방향): 공격 시작~타격+3틱 동안 2틱마다 현재 프레임을 잔상으로 남김, 14틱(0.23초)에 걸쳐 사라짐.
- 연하게: 불투명도 0.28에서 시작, 필터 brightness(1.7) sepia(1) hue-rotate(160deg) saturate(2) = 옅은 하늘색 (iOS Safari 는 필터 없이 반투명).
- 샌드박스 G 키 / "잔상" 버튼. 코드: patch_vg.py (GHOST/GH, drawHero 안 잔상 그리기).
- 영상: hit12_afterimage_v2.mp4 (왼쪽 원래 / 오른쪽 잔상).
