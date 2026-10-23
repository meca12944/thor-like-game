# 회피대시·맞기 v1 (모션연구방, 2026-10-23, 사장님 "3번까지 전부 인게임 적용해")

- `apply.py`: 주인공 dash_right/down, hurt_right/down/up, 리네트 dash·hurt 옆/정면/뒷면 박자(그림 그대로, 합계 그대로). 회피대시는 가장 빠를 때 숙이게, 맞기는 맞자마자 젖혀지게.
- 코드: `world.js` 들판에서 맞으면 때린 쪽을 봄(공격 중이 아닐 때) + 8px를 7틱 동안 미끄러지듯 밀림(전: 1틱 순간이동). `index.html` 마을에서도 맞으면 때린 쪽을 봄(밀림은 원래 부드러움).
- 확인: `motion_lab/research_v1/videos/ingame_hit.mp4`(등 뒤에서 맞기 전·후), dash_v1·hurt_v1, 들판·마을·샌드박스·test_place_all 오류 0.
