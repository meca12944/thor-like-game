# docs_art — 일러스트 레퍼런스 (게임 코드/에셋과 분리)

## bust/ — 대화용 바스트업 일러스트 (진행 중)
- 규격: 1024×1280 투명 PNG, 머리~배꼽 아래, 얼굴 크게. 경로 `bust/<id>/<expr>.png`, id는 `town/tachie.js`·`town/assets/tachie/index.json`과 동일.
- 표정 6종: neutral smile angry sad surprised blush (별칭은 `bust/index.json`의 alias, tachie와 동일).
- 몸·의상 동일, 얼굴만 교체: neutral 원본 1장 생성 → 표정별 편집 생성 → ECC 정렬 후 얼굴 타원 영역(페더)만 원본에 합성. 배경 제거(흰 배경 플러드필 + rembg isnet-anime 보조, 가장자리 흰색 오염 제거)는 neutral 알파를 모든 표정에 공통 적용.
- 스타일: 승인된 VN CG(town-demo/src/heroines/cg_modern_sample.jpg, cg_*_1.jpg) 기준, 의상·머리색은 town-demo/style_sample/female_vs_hero_v2.png 기준. 유나만 현대 의상.
- 완료: a_tailor(나비), d_yuna(유나). 남은 것: hero, h_mystic(운), g_dancer(방울), f_diver(숨비), e_tailor(루비), c_priest(설화).
- 미리보기: `bust/preview_bust.png`, `preview_all.png`.
- 재생성 스크립트: `tools/bust.py <id> <crop_cx> <face_x> <face_y> <rx> <ry>` (1280×720 생성본 좌표), `tools/sheet.py`.

규칙: 모든 여성은 명백한 성인, 비노출·비선정(배꼽 드러나는 크롭/비키니 탑까지, 언더붓 없음).

## outfits_v3/ — 신규 의상 디자인 (승인 대기)
- 판타지 소재(가죽·룬 각인 금속·보석·자수·천)의 몸에 맞는 바디슈트 + 부분 갑옷, 캐릭터별 3~4색. 유나만 현대 의상(기존 바스트와 같은 넥라인).
- 전원 정면 전신, 900×1320 투명 PNG, 같은 몸 높이(1200px, 정수리 y=60 ~ 발바닥 y=1260 기준선). 파일명 = tachie id (`hero.png`, `a_tailor.png` …), 라인업 `outfits_v3/lineup.png`.
- 재생성: `tools/outfits.py` (흰 배경 생성본 → 배경 제거 → 정수리·발바닥 기준 스케일 정규화 → 라인업).
- 바스트 일러스트(bust/)는 승인 후 이 의상으로 다시 그린다.
