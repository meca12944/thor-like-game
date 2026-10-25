# 새 그록 주인공 게임 연결 (모션연구방, 10-25 사장님 「팀장 추천대로 컨펌」 순서표 9)
- `build_atlas.py` → `hero_grok_0.webp` + `hero_grok.json` (H8 형식, 172칸, 41동작, figH 144)
- `apply.py [저장소]` (최신 main 위에서): 시트 복사, index.html `/*H8*/`에 붙이기(옛 칸은 그대로라 되돌리기 쉬움, cast 마법진 층 유지), world.js `H128FIG 30→34`, 그림 키 `117 → ART_FIG(=H8.figH)`
- 확인(최신 main 21968b8d 위에 apply, 1920×1080, field01): 콘솔 오류 0, 서기·걷기·달리기·회피대시 새 주인공으로 나옴 → `ingame_check.png`
- 걷기 보폭: gait walkCyc 74.4·runCyc 87.3, gaitMul walk_dr 1.41·run_dr 1.2 (옆 걷기 120·달리기 143 art px/바퀴, ↘ 85·119)
- 남은 것: 칼 grip(검흔 담당 `grip.json`을 이 폴더에 두면 apply가 넣음), world.js 2175줄 `FIG = 117`(얼굴 자르기)·리네트 117은 그대로, 걷기 보폭 `gait`는 키가 커져 발 미끄러짐 다시 재야 함
