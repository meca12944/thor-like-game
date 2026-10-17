# 대화 전신 스탠딩 일러스트 (立ち絵 / tachie)

일본 게임식 대화 연출: 대화 중 주인공(왼쪽)과 상대 히로인(오른쪽)이 **전신 스탠딩 일러스트**로 대화창 옆에 크게 선다.

- 말하는 사람은 밝게, 듣는 사람은 어둡게(brightness .6, 2.5% 축소). 대사마다 표정 교체(0.14초 크로스페이드).
- 숨쉬기 아이들(3.6초 주기, 발 기준 세로 0.9% 미세 확대), 등장/퇴장 슬라이드+페이드(0.24~0.32초).
- 별도 DOM 레이어(`#tachie`)에 디스플레이 해상도로 부드럽게 축소 표시 — 월드 캔버스(저해상도 + nearest)와 분리돼 픽셀화되지 않는다. transform/opacity/filter만 애니메이션(GPU 합성) → 60 fps (F3 측정 60.0 FPS, rAF 평균 60.0 / p99 16.8 ms, tools/test_tachie.py).

## 대상 · 표정

| id | 이름 | 표정 |
|---|---|---|
| hero | 필멸자 | neutral smile angry sad surprised blush |
| a_tailor | 나비 | 〃 |
| h_mystic | 운 | 〃 |
| g_dancer | 방울 | 〃 |
| f_diver | 숨비 | 〃 |
| e_tailor | 루비 | 〃 |
| c_priest | 설화 | 〃 |
| d_yuna | 유나 (현대 의상은 유나만) | 〃 |

별칭: normal→neutral, happy→smile, mad→angry, cry→sad, shock→surprised, shy→blush. 없는 표정은 neutral로 대체.

## 데이터 (대사에 화자 + 표정)

`TALK[id].lines[i]()`가 `{who:'hero'|'<charId>'|'none', expr:'smile', t:'대사'}`를 반환하면 된다.
- `who` 생략 = 대화 상대(`TALK[id].tachie` 또는 `TALK[id].por`), `'none'` = 내레이션(둘 다 어둡게).
- `TALK[id].expr` = 상대 기본 표정, `TALK[id].heroExpr` = 주인공 기본 표정, `withHero:false` = 주인공 일러스트 숨김.
- 상대에게 전신 일러스트가 있으면 대화창 안 작은 얼굴 초상화 대신 전신이 뜬다. 없으면(이슬·미소 등) 기존 작은 초상화 유지, 주인공 대사가 있는 대화면 주인공 전신만 왼쪽에 선다.
- 시작 마을에 나비 NPC(400,570) 배치 — 근처에서 상호작용 키로 대화. 테스트/미리보기: `index.html?talk=<id>` 또는 `__tachie.openTalk('<id>')`.

## 파일

- `town/tachie.js` — 레이어 + 대화 훅(메인 스크립트의 renderUI/closeUI 전역 함수를 감쌈, 메인 스크립트 수정은 `<script src="tachie.js">` 한 줄).
- `town/assets/tachie/<id>_<expr>.png` — 750×2150 투명 PNG(전원 같은 캔버스·같은 기준선), `index.json` 목록.
- `town/tools/tachie/` — 아트 원본: `lib.js`(몸·얼굴·표정 공통), `chars.js`/`chars2.js`(캐릭터별 머리·의상), `render.py`(헤드리스 Chromium → PNG), `make_index.py`, `sheets.py`(라인업/표정 시트). 다시 만들기:
  `cd town/tools/tachie && python3 render.py ../../assets/tachie 1.25 hero:neutral ... && python3 make_index.py`
- 아트 방식: 절차적 벡터(SVG) 셀 셰이딩. 같은 몸·머리·의상 레이어에 얼굴 파츠만 바꾸므로 표정 간 일관성이 보장된다. 이번 작업 환경에서 이미지 생성 결과 파일을 박스로 가져올 수 없어 벡터 렌더로 제작 — 나중에 손그림/생성 일러스트로 바꿀 때는 같은 파일명·캔버스(750×2150, 발바닥 기준선 하단)로 덮어쓰면 된다.
- 규칙: 성인 여성, 비노출(배꼽 드러나는 크롭/비키니 탑 + 미니/비키니 하의, 언더붓 없음), 유나만 현대 의상, 나머지는 판타지 의상(가죽·천·털·금속 장식·팔찌·벨트).
