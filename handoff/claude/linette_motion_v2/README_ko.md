# 리네트 모션 v2 (모션연구방, 2026-10-23, 사장님 "리네트도 게임에 넣어주고")

- `apply.py`: `motion_lab/research_v1/linette` 결과를 `test128/assets/anim/linette8_lab.webp` + `linette8.json`에 넣음(걷기 8방향·달리기 6방향 박자·오르내림·좌우 흔들림, 대각선 서기 숨쉬기, 쓰러지기 중력 박자).
- 코드: `world.js` 동료 리네트가 걸음 장을 박자 합으로 고르고, 한 바퀴 거리 32/46 → 23.4/32.8 들판px(그린 걸음 폭과 같게 → 발 미끄러짐 1.4배 → 1배). `linette.html` 발 먼지·출발 장도 박자 합으로.
- 확인: field00 전·후 `motion_lab/research_v1/videos/ingame_linette.mp4`, test_place_all 오류 0.
