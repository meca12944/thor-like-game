---
name: ingame-test
description: 「필멸자」 test128 변경을 실제 게임에서 돌려 확인하고 MP4로 보여줄 때 쓴다 ("인게임 확인", "녹화해서 보여줘", "소리 확인"). 로컬 서버 + Playwright 자동 플레이 + 영상(소리 포함 가능).
---
# 인게임 테스트 + 녹화

주인은 폰으로 본다 → 결과는 **MP4/이미지** (GIF 안 됨), 보고는 짧은 한국어.

## 준비 (서버는 명령마다 같이 띄운다 — 백그라운드 서버가 사라지는 일이 잦음)
```
cd test128 && (python3 -m http.server 8931 >/dev/null 2>&1 &) ; sleep 1
export PW_CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
```
`playwright install` 금지 (크로미움 미리 깔려 있음).

## 도구 (test128/tools)
- `test_place_all.py <url> <out>` — field00(리네트)·field01·field02~09 를 돌며 몹 전투 녹화, 페이지 에러/탄 종류 출력 → `place_all.mp4`
- `sfx_preview.py <url> <맵> <out>` — 자동 전투 + 소리 기록 → **소리 들어간** `sfx_preview.mp4` (소리 정의: test128/sfx_synth.js)
- `test_felt_mobs.py` — 1장 펠트 몹 4종 패턴 녹화
- url 은 `http://127.0.0.1:8931/index.html`. 주소 뒤 `?go=world|field00..09` 로 마을 건너뛰기.

## 테스트 API (window.__world)
`setManual(true)` 후 `advance(초)` 로 시간 진행, `go(맵,'default')`, `setHeroTile(x,y,face)`, `spawn(종류,x,y)`, `mobs`, `hazards`, `S`(상태), `tap('KeyJ')`/`key(code,down)` 입력. 무적: 매 프레임 `hero.hp = hero.maxHp`.

## 확인할 것
- `errors: []` (pageerror 0) 인지. 에러 나면 고치고 다시.
- 스크린샷 몇 장을 직접 보고(Read) 그림 위치·크기·빈칸 확인 후 SendUserFile 로 MP4 전송.
