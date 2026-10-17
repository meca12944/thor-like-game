# 대화 바스트업 일러스트 (원화 납품 폴더)

일러스트 담당이 여기에 **상반신 바스트샷** 원화를 넣는다. 게임은 이 폴더를 직접 읽지 않고, `town/tools/import_bust.py`가 최적화해서 `town/assets/bust/`로 복사한다.

## 규격

- 경로: `docs_art/bust/<id>/<expr>.png`
- 투명 배경 PNG, **1024×1280** (4:5 세로)
- 구도: 머리 위 약간 여백 ~ 허리 바로 아래까지. 캔버스 하단 = 허리 아래에서 잘림(게임에서 화면 하단에 붙여 세움). 얼굴이 크게, 몸은 정면~약간 3/4.
- **비율 통일(2026-10-17, 사장님 지시)**: 비율 기준 `docs_art/ref/user_proportion_ref.png`(약 5등신). 8명 전원 얼굴(눈~턱 174px)·눈선 y391·턱 y565·어깨선 y660(어깨 반폭 약 235px)·가슴 y843·허리 y1042·중심 x512로 동일. 확인용 `bust/proportion_check.png`. 표정마다 몸·머리 위치는 동일, 얼굴만 다르게(0.14초 크로스페이드).
- 주인공(hero)은 화면 왼쪽, 히로인은 오른쪽에 선다. 그림은 정면 기준으로 그리면 되고 좌우 반전은 하지 않는다.

| id | 이름 (칭호) | 비고 |
|---|---|---|
| hero | 「낙인의 자식」 필멸자 | 주인공 |
| a_tailor | 「은바늘의」 리네트 |  |
| h_mystic | 「별을 엮는 점성녀」 베일라 |  |
| g_dancer | 「사막방울의 무희」 자이라 |  |
| f_diver | 「잿물결의 해녀」 마렌 |  |
| e_tailor | 「불꽃실의 직녀」 로자린드 |  |
| c_priest | 「서리 성녀」 이벨린 |  |
| d_yuna | 「차원을 건넌 이방인」 유나 | 현대 의상은 유나만 (본명 한유나) |

표정(`<expr>`): `neutral` `smile` `angry` `sad` `surprised` `blush`. 빠진 표정은 게임에서 neutral로 대체된다(neutral은 필수).

## 게임에 넣기

```
python3 town/tools/import_bust.py              # docs_art/bust -> town/assets/bust/<id>/<expr>.webp + index.json
python3 town/tools/import_bust.py --format png # 무손실 압축 PNG로
```

크기가 1024×1280이 아니면 비율 유지로 맞추고 하단 중앙 정렬(경고 출력). 원화가 아직 없는 id/표정은 임시 바스트(아래)로 채워 둘 수 있다.

## 임시 바스트 (원화 도착 전)

`python3 town/tools/make_bust_temp.py` — 기존 전신 스탠딩(`town/assets/tachie`, 750×2150)을 상반신으로 크롭해 1024×1280으로 만들고(`/tmp/bust_temp`), `import_bust.py --src /tmp/bust_temp`로 임포트한다. `docs_art/bust`에 있는 실제 원화가 항상 우선. `town/assets/bust/index.json`의 `source`가 `art`/`temp`로 어느 쪽인지 표시한다.
