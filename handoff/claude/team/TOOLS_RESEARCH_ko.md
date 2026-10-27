# 게임 만드는 데 필요한 도구·기능·외주 조사 (10-27, 사장님 「툴·기능·플러그인·픽셀랩처럼 외주 필요한 것 싹 다 팀원들이랑 조사해서 보고」)
- 참석: 팀장 + 조사 팀원 1 (웹 조사). 값은 공식 페이지 기준, (미확인) 표시는 다시 볼 것. 돈·유료 API 0.

## 지금 바로 추천 TOP 5
1. Sonniss GDC 묶음 (무료 효과음, 팔 때도 그냥 씀) — 소리 품질 바로 좋아짐. https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/
2. Retro Diffusion 조금 시험 (도트 AI, API, 값 미리 알려 줌, 실패 환불) — 바닥 타일·효과 그림. 상업 이용 약관 먼저 확인(미확인). https://github.com/Retro-Diffusion/api-examples
3. Playwright 화면 비교 + GitHub Actions — 고친 것 때문에 다른 데 망가지면 저절로 잡음 (무료).
4. Aseprite (19.99달러 한 번) — AI 그림 다듬기·묶기를 명령어로. https://www.aseprite.org/cli/
5. Electron + steamworks.js 시험판 (무료) — 일찍 PC 프로그램으로 싸 보기, 업적·클라우드 저장. Steam 등록비 100달러(매출 1000달러 넘으면 돌려받음) https://partner.steamgames.com/doc/gettingstarted/appfee

## 묶음별
- 그림: Retro Diffusion ★★★ · Aseprite ★★★ · LDtk/Tiled(지도 그리기, 무료) ★★ · Scenario ★ (도트 움직임 없음). PixelOver·Pyxel Edit는 봇이 못 다룸.
- 소리: Sonniss ★★★ · ElevenLabs 효과음(유료부터 상업) ★★ · jsfxr ★★ · Howler.js ★★. 대표 음악은 Suno·Udio 재판 위험 → 사람 작곡가.
- 게임 코드: 게임패드 버튼 그림 바뀌기(Steam 필수) ★★★ · PixiJS(느려질 때만) ★★ · Sentry(오류 알림, 무료 5천 건) ★★.
- PC·Steam: Electron ★★★ · steamworks.js ★★★ · Steam Deck 기준(패드만으로 끝까지, 1280×800에서 글자 9px↑) https://partner.steamgames.com/doc/steamdeck/compat
- 일하는 방법: Playwright 화면 비교 ★★★ · GitHub Actions ★★ · GitHub Issues 양식(사장님이 폰으로 버그 적기) ★★.
- 사람에게 맡기기: r/gameDevClassifieds·itch.io ★★★ (도트 움직임 한 장 3~20달러, 음악 1분 25~500달러), ArtStation ★★, Fiverr/Upwork ★. 계약에 「상업 권리」 꼭.
- 필요 없는 것: 3D 도구(봉인), PixelOver·Pyxel Edit, 엔진 갈아타기, 지금 PixiJS 바꾸기, Suno 대표 음악, Tauri·NW.js, 유료 효과음 구독, 분석 서비스.
