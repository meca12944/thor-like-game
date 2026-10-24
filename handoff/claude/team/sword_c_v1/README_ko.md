# C안: 평소 칼 든 채, 벨 때만 칼 없는 몸 + 코드 칼날 (사장님 10-24 「C안으로 가자」) — 브랜치 claude/sword-c (claude/linette-8dir 위)
`test128/world.js`: swordHidden / nsImg / gkGrip / gkBlade. 검기가 열리는 0~4.5틱 동안 칼 없는 사본 그림으로 바꿔 그리고, 코드 칼날(남색 테두리 + 은빛 날 + 흰 날빛 + 금빛 손잡이, 길이 74 그림px)이 손에서 검기 앞쪽 끝을 향해 함께 휘둘러짐. ?gk=sweep 시안과 같이 동작.
- 그림 받는 법(모션연구방): 칼 든 시트마다 칸 배치가 같은 칼 없는 사본 `anim/ns/<같은 이름>.webp`, H8 에 `nsSheets: {시트번호: 경로}`. 손: `grip: {"시트:칸": [dx, dy, deg]}` (앵커=발 기준 그림px, deg 오른쪽 0° 아래 +90°). 없으면 가슴 높이 추정 손.
- 지금은 `?sword=mock` 일 때만 켜짐(칼만 자동으로 지운 시험 그림 assets/anim/ns_mock/, strip.py 로 만듦 — 옆모습에 칼자루가 조금 남음). 모션 그림(nsSheets)이 들어오면 주소 없이 기본으로 켜지고 ns_mock 폴더는 지운다(예전 판 남기지 않기).
- 그림이 없으면 칼 숨김·코드 칼날 모두 꺼짐 → 칼 두 자루가 되지 않음. ?sword=off 로 끌 수 있음.
그림 sweep_vs_c.png (위 ?gk=sweep, 아래 ?gk=sweep&sword=mock), 비교 영상 sword_hold_v1.mp4. test_openworld 17/17.
