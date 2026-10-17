# 대화 바스트업 일러스트 (원화 납품 폴더)

일러스트 담당이 여기에 **상반신 바스트샷** 원화를 넣는다. 게임은 이 폴더를 직접 읽지 않고, `town/tools/import_bust.py`가 최적화해서 `town/assets/bust/`로 복사한다.

## 규격

- 경로: `docs_art/bust/<id>/<expr>.png`
- 투명 배경 PNG, **1024×1280** (4:5 세로)
- 구도: 머리 위 약간 여백 ~ 허리 바로 아래까지. 캔버스 하단 = 허리 아래에서 잘림(게임에서 화면 하단에 붙여 세움). 얼굴이 크게, 몸은 정면~약간 3/4.
- 전원 같은 스케일/눈높이(대략 캔버스 위에서 20~28% 지점)로 맞추면 대화 중 교체가 자연스럽다. 표정마다 몸·머리 위치는 동일, 얼굴만 다르게(0.14초 크로스페이드).
- 주인공(hero)은 화면 왼쪽, 히로인은 오른쪽에 선다. 그림은 정면 기준으로 그리면 되고 좌우 반전은 하지 않는다.

| id | 이름 | 비고 |
|---|---|---|
| hero | 「낙인의 자식」 필멸자 | 주인공 |
| a_tailor | 리네트 | |
| h_mystic | 베일라 | |
| g_dancer | 자이라 | |
| f_diver | 마렌 | |
| e_tailor | 로자린드 | |
| c_priest | 이벨린 | |
| d_yuna | 「차원을 건넌 이방인」 유나 | 현대 의상은 유나만, v5 의상 완료 |

표정(`<expr>`): `neutral` `smile` `angry` `sad` `surprised` `blush`. 빠진 표정은 게임에서 neutral로 대체된다(neutral은 필수).

## 의상

- 의상은 승인된 `docs_art/outfits_v3/` (v5, 2D 애니 셀 셰이딩 + 밀착 슈트) 디자인과 동일하게 그린다. 미리보기: `bust/preview_bust.png`.

## 게임에 넣기

```
python3 town/tools/import_bust.py              # docs_art/bust -> town/assets/bust/<id>/<expr>.webp + index.json
python3 town/tools/import_bust.py --format png # 무손실 압축 PNG로
```

크기가 1024×1280이 아니면 비율 유지로 맞추고 하단 중앙 정렬(경고 출력). 원화가 아직 없는 id/표정은 임시 바스트(아래)로 채워 둘 수 있다.

## 임시 바스트 (원화 도착 전)

`python3 town/tools/make_bust_temp.py` — 기존 전신 스탠딩(`town/assets/tachie`, 750×2150)을 상반신으로 크롭해 1024×1280으로 만들고(`/tmp/bust_temp`), `import_bust.py --src /tmp/bust_temp`로 임포트한다. `docs_art/bust`에 있는 실제 원화가 항상 우선. `town/assets/bust/index.json`의 `source`가 `art`/`temp`로 어느 쪽인지 표시한다.
