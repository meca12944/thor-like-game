# docs_art — 일러스트 레퍼런스 (게임 코드/에셋과 분리)

## bust/ — 대화용 바스트업 일러스트 (8명 완료)
- 규격: 1024×1280 투명 PNG, 머리~배꼽 아래, 얼굴 크게. 경로 `bust/<id>/<expr>.png`, id는 `town/tachie.js`·`town/assets/tachie/index.json`과 동일.
- 표정 6종: neutral smile angry sad surprised blush (별칭은 `bust/index.json`의 alias, tachie와 동일).
- 몸·의상 동일, 얼굴만 교체: neutral 원본 1장 생성 → 표정별 편집 생성 → ECC 정렬 후 얼굴 타원 영역(페더)만 원본에 합성. 배경 제거(흰 배경 플러드필 + rembg isnet-anime 보조, 가장자리 흰색 오염 제거)는 neutral 알파를 모든 표정에 공통 적용.
- 스타일: 승인된 VN CG(town-demo/src/heroines/cg_modern_sample.jpg, cg_*_1.jpg) 기준, 의상·머리색은 town-demo/style_sample/female_vs_hero_v2.png 기준. 유나만 현대 의상.
- 완료(8명×6표정): hero(「낙인의 자식」 필멸자), a_tailor(「은바늘의」 리네트), h_mystic(「별을 엮는 점성녀」 베일라), g_dancer(「사막방울의 무희」 자이라), f_diver(「잿물결의 해녀」 마렌), e_tailor(「불꽃실의 직녀」 로자린드), c_priest(「서리 성녀」 이벨린), d_yuna(「차원을 건넌 이방인」 유나, 본명 한유나). 이름·칭호는 `docs_story/names_eldenring.md` 기준.
- 비율: 전원 `ref/user_proportion_ref.png` 기준으로 머리·얼굴 크기, 눈선·어깨선·어깨폭·가슴·허리 위치 통일 → `bust/proportion_check.png`.
- 미리보기: `bust/preview_bust.png`, `preview_all.png`.
- 재생성 스크립트: `tools/bust.py <id> <crop_cx> <face_x> <face_y> <rx> <ry>` (1280×720 생성본 좌표), `tools/sheet.py`.

## outfits_v3/ · characters/ — 전신 설정화 (900×1320 투명, 바닥선 y1260)
- outfits_v3: 주인공+히로인 7명 의상 확정본, `outfits_v3/lineup.png`. characters: 마을 사람·강자·보스 프로필, 배치별 `characters/batch_<배치>.png`, `characters/index.json`.
- 비율 통일(사장님 지시): 어른 전원 눈~턱 77px(머리 높이 약 184px), 눈선 y207·턱 y284·고관절(엉덩이선) y694·바닥 y1260 → 다리 길이 동일. 아이는 별도 아이 템플릿(눈~턱 71px, 눈 y648·턱 y716·고관절 y1037·바닥 y1260). 허리 굽은 노인(엘스베트)은 머리 크기·다리 길이는 같고 굽은 자세만 유지. 확인용 `characters/proportion_check.png`.
- 도구: `tools/characters.py`(배경 제거·정렬·라인업), `tools/proportion.py`+`tools/normalize.py`(눈·턱·고관절 랜드마크 → 비율 템플릿으로 워프).

규칙: 모든 여성은 명백한 성인, 노출 많고 섹시(노골적 성 묘사 없음)(배꼽 드러나는 크롭/비키니 탑까지, 언더붓 없음).
