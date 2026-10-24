# 콤보 1~3타 검흔 = 판정 부채꼴 그대로 (그록 다크 검흔 v3, 사장님 「4 파쇄 강철」) + C안 코드 칼 — 지금 claude/linette-8dir (fan-slash2 6f18ed32 + motion-lab 2f0625a6) + claude/fan-fix 한 줄
모두 코드(시트 안 붙임), 크레딧 0.
1. 그림 = 판정: gkFanPolar 하나로 판정(gkFanIn)과 그림(gkFanImg)이 같은 식. 1 그림px = 필드 1px, 땅 평면 회전 8방향, 왼쪽 뒤집기. 열림 = gkFanHead(t), 판정 끝 뒤 GK_FADE 10틱:
   면이 안쪽부터 접혀 테두리로 모이고, 테두리 날이 15조각으로 금 가며 하나씩 꺼지고, 각진 강철 조각이 떨어짐. 면(어두운 3단 + 1px 선)은 주인공 뒤, 테두리 날·1px 바깥선·칼끝 반짝임·조각은 앞.
   콤보 1~3타의 날아가는 하늘색 호·?gk=sweep 없음. 돌진·차지(i≥3)는 예전 호 그대로.
2. 색 = 파쇄 강철 하나(#0f1318 #45515e #6d7d8d #a8b5c1 #dce3ea, 면 #1a1f27 #1d232c #222933, 선 #0b0e12). 6종·?gkstyle 없음.
3. C안(모션연구방 2f0625a6): 콤보 1~3타 공격 내내 칼 없는 몸(H8.nsSheets) + heroBlade(효과 쪽 gkFanBlade 모양: #0d0f13 / #9aa3ad / #cfd5db, 금 날밑)가 손(grip + gripKick 몸 반동)에서 당김 → 부채꼴 앞끝(gkFanPt) 휘두름 → 끝에 멈춤. 칼 없는 그림 미리 읽기(nsPreload).
4. 고친 것: killMob mob_die 소리, index.html hitFeel 불꽃(주석 버그). claude/fan-fix: gkFanBlade 첫 줄 // 주석이 뒤 코드를 삼켜 공격 때 "gx0 is not defined" (test_openworld 16 → 17/17).
측정(동굴, 실마물 3마리 × 옆·아래·위 × 3연타; 전 = linette-8dir 8eb0de0b): 누르고 맞기 2.3틱(같음), 누르고 검흔 보이기 4.6 → 0.7틱, 그림 밖에서 맞음 4/27(15%) → 0/27.
영상 fan_steel_final.mp4 (옆·아래·위: 전 / 후 / 후 + ?hitdebug=1, fan-fix 판으로 녹화), 그림 chk5.png. 녹화 스크립트 cap.js(몹 3마리·숫자), clean.js(몹 없이).
