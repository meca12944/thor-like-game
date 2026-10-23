# 몬스터 샌드박스 소스
- 공개 페이지: https://claude.ai/artifact/RKP5Cw7HHRa7oKH7wmRLGD
- index.html 옆에 놓을 파일: test128/assets/mobs47/*.webp, test128/sfx_synth.js, 펠트 스트립(c1_*.webp), 주인공 hero_game.json + hero_game_0.webp (= 게임 주인공, `python3 tools/sandbox/build_hero_game.py <폴더>`로 만듦).
- 51종 = 펠트 4 + 1~9지역 47 (AI는 test128 world_mobs.js s47과 같음). 효과음 = sfx_synth.js (M키로 끄기).

- **주인공은 항상 게임 주인공** (사장님 10-23): 게임 주인공 그림이 바뀌면 `build_hero_game.py`를 다시 돌리고 샌드박스를 다시 올린다. 조작은 키보드(이동 WASD/방향키, 공격 J, 회피대시 Shift/K, 점프 Space) + 폰 터치.
