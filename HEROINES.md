# 히로인과 동료 퀘스트

> 데이터: `tools/design/heroines_data.py` → `data/towns.json` → `heroines`. 동료 퀘스트는 각 마을 `quests`에도 `companion` 필드와 함께 들어 있다. 모든 히로인은 성인이며 장면은 비노출이다.

## 동료 시스템

- **ai**: 임시 AI 동료: 주인공을 1.5타일 뒤에서 따라오며, 화면 안 가장 가까운 적을 우선 공격(기본 공격 + 고유 스킬 1개, 쿨타임 제). 전용 HP바(화면 좌상단 주인공 HP 아래)를 가진다.
- **down**: HP 0이면 「쓰러짐」 상태로 30초 동안 바닥에 남는다. 주인공이 옆에서 공격 버튼을 2초 누르거나 회복약을 쓰면 HP 30%로 부활. 30초가 지나면 마을로 귀환하고 해당 퀘스트 단계는 실패(재도전 가능). 사망하지 않는다(마왕 루트의 직접 살해 제외).
- **limit**: 동료는 한 번에 1명. 동료 퀘스트 진행 중에만 필드 동행, 호감도 80 이상이면 퀘스트 밖에서도 마을에서 불러 동행 가능.
- **affinity**: 호감도 0~100. 퀘스트 단계 완료 +15~25, 선물(취향 품목) +5~10 하루 1회, 싫어하는 선물 -5, 동행 중 쓰러뜨림 방치(귀환) -10. 선악 수치와 별개지만 아래 루트 규칙을 따른다.
- **karma**: 선악이 「악명」 이하로 떨어지면 히로인별 반응(떠남/적대/잔류). 마왕 루트에서는 다른 성인 NPC와 마찬가지로 살해할 수 있으며, 살해 시 다시 되돌릴 수 없다.
- **portraits**: 대화 초상화: 1순위 `<id>_<expr>_bu.png` (192×256 바스트업, 머리~허리, 대화창에서 1.5~2배 크게 표시 권장), 작은 창은 `<id>_<expr>_bu_s.png` (96×128), 없으면 기존 `<id>_<expr>.png`/`<id>.png` (128×128 얼굴). 경로 town/assets/portraits/, 목록은 index.json의 expressions_bustup.
- **outfit_rule**: 성인 여성 의상 규칙: 상의는 배가 완전히 드러나는 짧은 크롭 탑 또는 비키니 탑만(원피스·코르셋·배를 덮는 상의 금지, 비노출). 하의 선택지: 짧은 주름 미니스커트, 비키니 하의/마이크로 비키니(축제 변형), **H라인(펜슬) 미니스커트**(몸에 딱 붙는 일자, 허벅지 중간), **머메이드 미니스커트**(엉덩이까지 밀착, 허벅지 중간 밑단이 살짝 퍼짐). 적용: 로자린드=검은 가죽 H라인, 이벨린=흰 머메이드, 상인 미라벨=갈색 H라인, 책벌레 이브넬=보라 H라인, 공주 세린=보라·금 머메이드. 비키니 탑 변형(가리는 면적은 일반 비키니 이상, 언더붓 노출 금지): **스트래피 비키니**(일반 비키니 탑 + 갈비뼈·허리를 감는 가는 교차 끈), **홀터넥 비키니**(목 뒤로 묶는 삼각 탑, 컵 사이 작은 키홀 허용), **메탈 장식 비키니**(금·은 판금, 체인, 보석 장식의 비키니 아머). 적용: 미라벨=빨강 스트래피, 이브넬=보라 홀터넥, 빛나=노랑 홀터넥, 세린=금·보라 메탈 장식. 참고 샘플: female_sample_hline_mermaid.jpg, female_sample_bikini_variants.jpg. 아이는 대상 아님. **삼각 비키니 단독 착용**(상·하의 모두 일반 삼각 비키니, 치마·바지 없음; 샌들·작은 장신구·소지품만 허용, 일반 비키니 노출 범위, 비노출, 명백한 성인): 쪽빛(b_dyer, 강변 염색공방·남색), 사프란(g_tool, 사막 바자르 도구상·빨강), 자스민(g_tailor, 사막 바자르 의상상·연보라), 진주(f_tailor, 항구 의상상·라벤더). 히로인(베일라 등)은 고유 의상 유지. **세계관 의상 원칙(2026-10-17)**: 현대 의상은 유나(d_yuna, 현대에서 온 히로인)만. 나머지 모든 여성은 판타지 세계 의상(가죽·천·모피·룬 금속·보석·자수, 벨트·암가드·망토·장신구)으로 표현하되 위 상·하의 규칙(배 노출 크롭/비키니형 상의, 미니스커트류)은 유지. 세린 랩스커트 유지. 차기 의상 v3(스텔라블레이드풍 판타지 바디수트 + 부분 아머, docs_art/outfits_v3)는 오너 승인 대기 — 승인되면 이 규칙을 v3 기준으로 갱신.
- **body_standard**: 성인 여성(및 모든 인간형 캐릭터) 맵 스프라이트 체형 기준 = **주인공 정면 idle과 동일 비율** (2026-10-17 오너 승인 "좋심다", 7.9등신 규칙 폐지). 768x432 그리드(신규 스타일): 키 56px, 머리(정수리~턱) 14px = 4.0등신, 다리(가랑이/치마 밑단~발바닥) 20px = 키의 0.357, 정수리 0행·턱 13행·가랑이 36행·발바닥 55행(기준선 공통). 현행 384x216 게임 그리드: 키 28px, 머리 7px, 가랑이 18행(town/assets/npcs/v2). 정면·측면·후면, idle·walk 전 프레임 동일(±1px; 측정표 town/style_sample/female_proportions_v2.csv, fem_anim_metrics.csv; 비교 female_vs_hero_v2.png). 어깨 폭은 캐릭터별 차이 허용(주인공 대비 0.75~1.0). 아이 NPC는 키를 줄여도 되지만 같은 머리 비율 스타일 유지. 비노출, 명백한 성인.

| 호감도 | 보상 |
|---|---|
| 20 | 개인 대화 해금 |
| 40 | 고유 보조무기/장신구 선물 |
| 60 | 듀오 합동기 해금 |
| 80 | 특별 장면(비노출, 모닥불 대화·축제 데이트 등) + 상시 동행 |
| 100 | 엔딩 후일담 장면 |

## 리네트 — A 시작 마을

_시작 마을의 발랄한 재봉사. 바늘 두 개로 싸우는 첫 동료._

- 역할: 외형상점 「리네트 재봉소」 주인 · 쌍침 재봉사 · 22세 (성인) · 동료 HP 60
- 성격: 밝고 수다스럽다. 유행과 색 이야기에 눈이 반짝이지만, 실은 겁이 많아 혼자 숲에 못 간다.
- 사연: 왕도 궁정 의상실 견습이었으나 스승(비단결)과 다툰 뒤 고향으로 돌아왔다. 언젠가 「영웅의 망토」를 직접 지어 주는 게 꿈.
- 전투: 근접·속도형. 길쭉한 재봉 바늘 두 자루로 3연 찌르기. / 스킬 「실타래 묶기」 전방 부채꼴 적 2초 속박 (쿨 10초)
- 의상: 짧은 하늘색 주름 미니스커트, 배꼽이 드러나는 나비 리본 크롭 블라우스, 허리에 바늘꽂이 벨트, 무릎 위 줄무늬 스타킹. 금발 트윈테일.
- 선물: 좋아함 비단 천, 나비 날개 가루, 꽃 / 싫어함 광석
- 선악·마왕 루트: 악명: 울면서 재봉소 문을 닫고 B로 떠난다. 마왕: 겁에 질려 도망치며 공격하면 살해 가능 (전투력 낮음).
- 표정 초상화: `a_tailor_normal.png`, `a_tailor_smile.png`, `a_tailor_angry.png`, `a_tailor_blush.png`

| 퀘스트 | 제목 | 목표 | 보상 |
|---|---|---|---|
| `A_TAILOR1` | 실 한 타래의 용기 | 가까운 숲에서 「은빛 거미줄」 5개 채집 — 리네트 동행, 거미 몹으로부터 그녀를 지킨다 | 호감도 +20, 금화 100 |
| `A_TAILOR2` | 허수아비 패션쇼 | 하로의 허수아비 옷감을 훔쳐 간 까마귀 무리 처치 후 옷감 회수 — 리네트 동행 | 호감도 +20, 외형 「나비 리본 망토」 |
| `A_TAILOR3` | 영웅의 망토 | B 강변 수정 동굴 입구까지 동행해 「물빛 실크」 획득, 재봉소로 귀환 | 호감도 +25, 망토 염색 무료권 |

| 호감도 | 보상 |
|---|---|
| 40 | 보조무기 「나비 골무 부적」 (회피 +5%) |
| 60 | 듀오 합동기 「매듭 베기」: 리네트가 속박 → 주인공 회전베기 피해 2배 |
| 80 | 장면 「분수 축제의 밤」: 분수 광장 축제에서 함께 등불을 띄우는 데이트 |

- Visual (EN): petite cheerful adult woman (22), golden blonde twin-tails, bright amber eyes, sky-blue pleated mini skirt, cropped white blouse with big butterfly ribbon showing midriff, needle-cushion belt, striped thigh-high stockings, playful energetic vibe
- CG `first meet`: cheerful blonde twin-tail seamstress in mini skirt waving a giant needle in front of a cozy tailor shop at sunset
- CG `festival date`: blonde twin-tail woman in butterfly crop top releasing a paper lantern by a town fountain at night festival, warm lights, smiling at viewer

## 베일라 — H 서쪽 광산 마을

_광산의 수수께끼 점술가. 수정 구슬로 원거리 마법을 쏜다._

- 역할: 보랏빛 점술가 · 수정 술사 · 27세 (성인) · 동료 HP 50
- 성격: 몽환적이고 말을 빙빙 돌린다. 운명을 믿지만 정해진 미래를 바꾸는 사람을 보고 싶어 한다.
- 사연: 광산 깊은 곳 「노래하는 수정」의 목소리를 듣고 마을에 정착. 필멸자의 운명이 두 갈래로 갈라지는 환시를 보았다.
- 전투: 원거리형. 떠다니는 수정 구슬 2개가 보라색 광탄 발사. / 스킬 「예지의 장막」 3초간 주인공 피격 1회 무효 (쿨 15초)
- 의상: 보라색 반투명 베일, 금 동전 장식 비키니 탑, 옆트임이 허벅지까지 있는 짧은 보라 랩스커트, 팔찌와 발찌 다수. 은빛 긴 생머리.
- 선물: 좋아함 수정 원석, 향초 / 싫어함 횃불
- 선악·마왕 루트: 악명: 「예견한 대로군요」 하고 사라져 마왕 루트 최종장에 적으로 재등장(환영 마법). 마왕: 마주치면 적대, 살해 가능.
- 표정 초상화: `h_mystic_normal.png`, `h_mystic_smile.png`, `h_mystic_angry.png`, `h_mystic_blush.png`

| 퀘스트 | 제목 | 목표 | 보상 |
|---|---|---|---|
| `H_MYSTIC1` | 노래하는 수정 | 폐갱도 3층까지 동행해 「노래하는 수정 조각」 회수 — 박쥐 떼 습격 | 호감도 +20, 금화 200 |
| `H_MYSTIC2` | 갈라진 운명 | 베일라의 환시 속 장소(지하 호수)에서 수정 골렘 처치 | 호감도 +25, 「점술 카드」 3 |
| `H_MYSTIC3` | 별이 보이는 갱도 | 천장이 뚫린 옛 갱도에서 함께 별자리 점 — 도중 광석 도마뱀 무리 | 호감도 +20, 장면 해금 조건 충족 |

| 호감도 | 보상 |
|---|---|
| 40 | 보조무기 「운명의 수정구」 (오브, 스킬 게이지 +10%) |
| 60 | 듀오 합동기 「별똥 낙하」: 수정 광탄 5발 + 주인공 찌르기 연계 |
| 80 | 장면 「갱도 위의 별」: 뚫린 천장 아래 모닥불 앞에서 서로의 운명을 이야기 |

- Visual (EN): mysterious adult fortune teller (27), long straight silver hair, violet glowing eyes, sheer purple veil, gold-coin bikini top, short purple wrap skirt with high slit, many bangles, two floating crystal orbs, dreamy enigmatic vibe
- CG `fortune reading`: silver-haired fortune teller in purple veil and gold-coin bikini top reading a glowing crystal ball in a dark mine tent
- CG `stars campfire`: silver-haired woman sitting by a campfire under a starry sky seen through a collapsed mine ceiling, soft violet glow

## 자이라 — G 사막 바자르 ★특별

_짙은 붉은 머리의 사막 무희 상인. 쌍곡도 칼춤으로 싸우는 특별 히로인._

- 역할: 무희 겸 바자르 장신구 상인 · 24세 (성인) · 동료 HP 70
- 성격: 명랑하고 능청스럽다. 소문과 흥정에 밝지만 약속은 반드시 지킨다.
- 사연: 대상 행렬의 고아로 자라 춤과 장사로 살아남았다. 도적에게 빼앗긴 어머니의 「태양 방울」을 되찾는 것이 소원.
- 전투: 근접 회전형. 초승달 쌍곡도 칼날 회전 춤. / 스킬 「방울 매혹」 주변 적 1.5초 경직 + 받는 피해 +20% (쿨 12초)
- 의상: 짙은 붉은 긴 웨이브 머리, 금 동전과 방울이 달린 진홍 비키니 탑(풍만한 가슴), 허리에 걸친 짧은 반투명 시폰 스커트, 금팔찌·발찌. 이벤트 변형: 마이크로 비키니 축제 의상(female_sample_microbikini.jpg).
- 선물: 좋아함 사막 태양석, 향신료, 금 장신구 / 싫어함 모래쥐 고기
- 선악·마왕 루트: 악명: 장사꾼답게 「거래 끝」을 선언하고 가격 3배. 마왕: 도적 편에 붙어 적대, 살해 가능. 단, 호감도 100이면 단 한 명 「마왕의 무희」로 잔류(동행 유지, 아이를 해치면 떠남).
- 표정 초상화: `g_dancer_normal.png`, `g_dancer_smile.png`, `g_dancer_angry.png`, `g_dancer_blush.png`
- 견본 아트: `/workspace/town-demo/src/npcs/female_sample_desert_v2.jpg`, `/workspace/town-demo/src/npcs/female_sample_microbikini.jpg`

| 퀘스트 | 제목 | 목표 | 보상 |
|---|---|---|---|
| `G_DANCER1` | 대상 행렬 호위 | 바자르 → 오아시스 길에서 자이라의 장신구 수레 호위 (도적 3파) | 호감도 +20, 금화 300 |
| `G_DANCER2` | 도둑맞은 태양 방울 | 사막 도적 은신처 잠입, 두목 처치 후 「태양 방울」 회수 — 자이라 동행 | 호감도 +25, 「사막 태양석」 2 |
| `G_DANCER3` | 오아시스 축제의 춤 | 축제 무대를 노리는 전갈 떼를 막아 공연을 지킨다 | 호감도 +20, 외형 「축제 무희 장식 망토」 |

| 호감도 | 보상 |
|---|---|
| 40 | 보조무기 「태양 방울 팔찌」 (공격 속도 +8%) |
| 60 | 듀오 합동기 「모래 폭풍 왈츠」: 둘이 등을 맞대고 회전, 광역 연속 피해 |
| 80 | 장면 「오아시스 축제 데이트」: 축제 무대 뒤 등불 아래 둘만을 위한 춤 |

- Visual (EN): voluptuous curvy adult desert dancer-merchant (24), long wavy dark-red hair, golden eyes, tanned skin, crimson bikini top with gold coins and tiny bells, low-slung short sheer chiffon skirt, gold bangles and anklets, twin crescent scimitars, flirty confident vibe
- CG `bazaar meet`: curvy dark-red haired desert dancer in crimson bikini top with gold coins winking behind a jewelry stall in a sunny bazaar
- CG `blade dance`: dark-red haired dancer spinning with twin scimitars among scorpions at an oasis, flowing chiffon skirt, dynamic action
- CG `festival dance`: dark-red haired dancer in micro bikini festival costume dancing on a lantern-lit oasis stage at night, playful smile

## 마렌 — F 남쪽 항구 마을 ★특별

_항구 최고의 해녀. 작살로 싸우는 건강미 넘치는 특별 히로인._

- 역할: 해녀 · 작살 잠수꾼 · 25세 (성인) · 동료 HP 80
- 성격: 당차고 큰소리 잘 치는 누님 기질. 바다 앞에서만은 진지하다.
- 사연: 유령 해적에게 배를 잃은 아버지의 작살을 물려받았다. 가라앉은 아버지의 배에서 유품을 건지고 싶어 한다.
- 전투: 중거리 찌르기형. 작살 찌르기 + 수중에서 이동 속도 증가. / 스킬 「물보라 작살」 직선 관통 작살 투척, 물가에서 피해 1.5배 (쿨 9초)
- 의상: 짧은 흑청색 해녀 비키니 아머(풍만한 가슴), 허리에 그물 사롱, 조개 장식 목걸이, 다리에 물갈퀴 장화. 젖은 흑발 포니테일, 태닝 피부.
- 선물: 좋아함 진주, 구운 생선 / 싫어함 유령 해적 깃발
- 선악·마왕 루트: 악명: 항구 사람들을 지키려고 주인공에게 결투를 신청(적대). 마왕: 항구 수호자로 적대, 살해 가능.
- 표정 초상화: `f_diver_normal.png`, `f_diver_smile.png`, `f_diver_angry.png`, `f_diver_blush.png`

| 퀘스트 | 제목 | 목표 | 보상 |
|---|---|---|---|
| `F_DIVER1` | 물질 대결 | 산호초에서 진주 5개를 누가 먼저 캐는지 대결 — 상어 몹 출현 시 협공 | 호감도 +20, 잠수 시간 +2초 |
| `F_DIVER2` | 가라앉은 배 | 침몰선 잠수 스폿에서 아버지의 유품 회수, 유령 선원 처치 | 호감도 +25, 「바다 진주」 3 |
| `F_DIVER3` | 등대의 밤 | 유령 해적 정찰대를 등대 앞에서 격퇴 — 마렌·빛나와 함께 | 호감도 +20, 금화 400 |

| 호감도 | 보상 |
|---|---|
| 40 | 보조무기 「아버지의 작살촉 부적」 (수중 공격 +15%) |
| 60 | 듀오 합동기 「해일 찌르기」: 마렌 작살 관통 후 주인공 돌진 찌르기 |
| 80 | 장면 「해변 모닥불」: 등대 아래 해변 모닥불에서 아버지 이야기와 구운 생선 |

- Visual (EN): athletic busty adult sea diver (25), wet black ponytail, sea-green eyes, tanned skin, dark teal bikini armor with shell plates, fishnet sarong, shell necklace, harpoon, confident big-sister grin
- CG `pearl contest`: busty tanned diver with black ponytail in teal bikini armor surfacing from turquoise water holding a pearl, laughing
- CG `beach campfire`: black-haired diver wrapped in a towel sitting by a beach campfire under a lighthouse at night, gentle expression

## 로자린드 — E 화산 기슭 대장장이 마을

_도도한 화산 마을 직조공. 불에 안 타는 채찍으로 싸운다._

- 역할: 외형상점 「불꽃 옷감」 주인 · 화염 채찍술사 · 26세 (성인) · 동료 HP 65
- 성격: 도도하고 자신만만, 칭찬에 약하다. 실력을 인정한 상대에게만 존댓말을 버린다.
- 사연: 불사조 깃털로 「영원히 타지 않는 천」을 짜는 것이 일생의 목표. 화산 정상에 오를 동료를 찾고 있었다.
- 전투: 중거리형. 불꽃 채찍 2연타, 화상 부여. / 스킬 「화염 고리」 주변 원형 불꽃, 2초 화상 (쿨 12초)
- 의상: 가슴 아래에서 끝나는 검은 가죽 크롭 뷔스티에(배 완전 노출), 몸에 딱 붙는 검은 가죽 H라인(펜슬) 미니스커트(허벅지 중간, 옆트임), 불꽃 무늬 사이하이 부츠, 허리에 감긴 채찍. 붉은 단발과 루비 귀걸이.
- 선물: 좋아함 불사조 깃털, 흑요석 / 싫어함 물
- 선악·마왕 루트: 악명: 「실망이야」 한마디로 상점 거래 거부. 마왕: 마왕군과 싸우다 적대, 살해 가능.
- 표정 초상화: `e_tailor_normal.png`, `e_tailor_smile.png`, `e_tailor_angry.png`, `e_tailor_blush.png`

| 퀘스트 | 제목 | 목표 | 보상 |
|---|---|---|---|
| `E_TAILOR1` | 타지 않는 실 | 용암 동굴에서 「화염 누에고치」 6개 — 로자린드 동행 | 호감도 +20, 금화 300 |
| `E_TAILOR2` | 불사조의 깃털 | 화산 중턱에서 불새 무리 처치 후 깃털 회수 | 호감도 +25, 외형 「불꽃 실크 망토」 |
| `E_TAILOR3` | 불꽃 옷감 품평회 | 품평회를 망치려는 쇠메의 라이벌 상인 패거리 격퇴 | 호감도 +20, 방어구 화염 저항 염색 |

| 호감도 | 보상 |
|---|---|
| 40 | 보조무기 「루비 채찍 팔찌」 (화상 확률 +10%) |
| 60 | 듀오 합동기 「불꽃 회오리」: 화염 고리 + 주인공 회전베기 = 화염 소용돌이 |
| 80 | 장면 「용암 강가의 밤」: 식은 용암 바위 위에서 완성한 천을 주인공 망토에 둘러 준다 |

- Visual (EN): haughty adult weaver (26), sharp red bob haircut, ruby eyes, black leather cropped bustier ending under the bust with fully bare midriff, tight black leather H-line pencil mini skirt (mid-thigh, side slit), flame-pattern thigh-high boots, coiled fire whip, ruby earrings, proud tsundere vibe
- CG `workshop`: red bob haired woman in black corset crop top and ruby mini skirt weaving glowing fire cloth in a forge workshop
- CG `lava night`: red-haired woman draping a shimmering flame cloak over the viewer beside a cooled lava river at night

## 이벨린 — C 설산 산장 마을

_어둠 신전을 두려워하는 설산의 성녀. 유일한 치유형 동료._

- 역할: 눈의 신전 사제(성녀) · 서리 치유사 · 23세 (성인) · 동료 HP 55
- 성격: 온화하고 다정하지만 고집이 있다. 두려움을 숨기고 웃는다.
- 사연: 어린 시절 어둠 신전 사제들에게 납치될 뻔한 기억을 지녔다. 신전의 봉인을 지키는 마지막 성녀.
- 전투: 후방 지원형. 서리 지팡이로 얼음 탄환. / 스킬 「눈꽃 축복」 주인공 HP 25% 회복 (쿨 20초)
- 의상: 흰 털 장식 짧은 크롭 상의(배 완전 노출)와 분리형 털 소매, 몸에 붙다가 밑단이 살짝 퍼지는 흰 머메이드 미니스커트(허벅지 중간), 하늘색 보석 장식, 흰 사이하이 스타킹, 눈꽃 머리장식. 연한 하늘빛 긴 머리.
- 선물: 좋아함 눈꽃 결정, 따뜻한 수프 / 싫어함 어둠의 파편
- 선악·마왕 루트: 악명: 신전에 틀어박혀 회복 서비스 거부. 마왕: 마지막 봉인을 지키며 적대(정화 마법이 마왕에게 추가 피해), 살해 가능.
- 표정 초상화: `c_priest_normal.png`, `c_priest_smile.png`, `c_priest_angry.png`, `c_priest_blush.png`

| 퀘스트 | 제목 | 목표 | 보상 |
|---|---|---|---|
| `C_PRIEST1` | 얼어붙은 순례길 | 신전 순례길의 설인 무리 정리 — 이벨린 동행 | 호감도 +20, 회복약 3 |
| `C_PRIEST2` | 봉인의 종 | 설산 동굴의 「봉인의 종」 3개를 다시 울린다, 어둠 사제 처치 | 호감도 +25, 「성수」 2 |
| `C_PRIEST3` | 눈꽃 축제 | 눈꽃 축제 등불을 노리는 서리 늑대 떼 격퇴 | 호감도 +20, 외형 「눈꽃 망토」 |

| 호감도 | 보상 |
|---|---|
| 40 | 보조무기 「성녀의 눈꽃 부적」 (부적, 받는 피해 -5%) |
| 60 | 듀오 합동기 「성광 서리검」: 축복 후 주인공 검에 빙결 부여 10초 |
| 80 | 장면 「눈꽃 축제 데이트」: 산장 앞 눈꽃 축제에서 따뜻한 수프를 나누며 걷기 |

- Visual (EN): gentle adult snow priestess (23), long pale ice-blue hair, soft blue eyes, short white fur-trimmed crop top with fully bare midriff, detached fur-trimmed sleeves, snug white mermaid-silhouette mini skirt flaring slightly at the mid-thigh hem, ice-jewel accents, white thigh-high stockings, snowflake hair ornament, frost staff, kind but brave vibe
- CG `temple`: ice-blue haired priestess in short white fur-trimmed dress praying in a snowy temple with glowing snowflakes
- CG `snow festival`: ice-blue haired priestess holding a warm soup bowl at a snow festival with lanterns, blushing smile

## 유나 — D 성벽 왕도 ★특별

_현대 세계에서 떨어진 흑발 대학원생. 짧은 검과 「낙인 공명」으로 싸우는 특별 히로인._

- 역할: 현세에서 온 이방인 · 왕도 서고의 객원 조사원 · 25세 (성인) · 동료 HP 65
- 성격: 밝고 붙임성 있지만 속으로는 집이 그리워 밤마다 휴대폰(배터리 0%)을 만지작거린다. 이 세계를 「게임 같다」며 의외로 빨리 적응했다.
- 사연: 서울의 대학원생(고고학). 박물관에서 낙인 문양이 새겨진 동판을 만진 순간 빛에 삼켜져 왕도 성벽 밖 폐허에 떨어졌다. 그녀의 손등에도 옅은 「포식의 낙인」 문양이 떠 있어, 그 낙인이 세계 사이의 문을 여는 열쇠라는 것을 서고지기 더스턴과 함께 알아낸다. 귀환 방법은 마룡의 심장에서 흘러나오는 차원 균열뿐 — 필멸자와 함께 끝까지 가야만 선택할 수 있다. 엔딩(호감도 100)에서 귀환할지 남을지 직접 고른다.
- 전투: 근접 기동형. 박물관 진열장에서 함께 떨어진 짧은 의례용 검으로 빠른 2연 베기 + 백스텝. / 스킬 「낙인 공명」 주인공의 포식의 낙인과 공명, 5초간 둘 다 공격력 +20%·흡수 효율 +1 (쿨 18초)
- 의상: 흰 오프숄더 크롭 블라우스(풍만한 가슴, 배꼽 노출), 검은 주름 미니스커트와 체인 벨트, 검은 사이하이 스타킹, 하트 펜던트 초커, 허리에 짧은 검. 긴 흑발에 앞머리, 보랏빛 눈.
- 선물: 좋아함 단 과자, 고대 문서, 반짝이는 돌(휴대폰 충전용이라 믿음) / 싫어함 벌레
- 선악·마왕 루트: 악명: 「너 그런 사람 아니었잖아…」 하고 서고에 숨어 동행 거부. 마왕: 포식의 낙인이 공명해 마왕에게 끌려가며 적대하지 않지만 대화 불가 상태로 따라오다가, 아이를 해치는 순간 낙인을 거꾸로 써서 마왕에게 저주(최대 HP -10%)를 건 뒤 적대. 다른 성인처럼 살해 가능 — 살해하면 귀환 엔딩은 영구 소실.
- 표정 초상화: `d_yuna_normal.png`, `d_yuna_smile.png`, `d_yuna_angry.png`, `d_yuna_blush.png`
- 견본 아트: `/workspace/town-demo/src/heroines/cg_modern_sample.jpg`

| 퀘스트 | 제목 | 목표 | 보상 |
|---|---|---|---|
| `D_YUNA1` | 하늘에서 떨어진 여자 | 성벽 밖 폐허에서 몹에 둘러싸인 유나 구출 후 왕도까지 호위 — 유나 동행 | 호감도 +20, 금화 300 |
| `D_YUNA2` | 낙인의 동판 | 서고지기 더스턴의 단서로 고대 묘지 지하에서 「낙인 동판 조각」 회수, 묘지기 해골 기사 처치 | 호감도 +25, 「고대 문서」 2 |
| `D_YUNA3` | 두 세계의 등불 | 왕도 등불 축제 날, 차원 균열에서 새어 나온 그림자 몹을 막아 축제를 지킨다 | 호감도 +20, 외형 「이방인의 초커」 |

| 호감도 | 보상 |
|---|---|
| 40 | 보조무기 「방전된 휴대폰」 (부적: 던지면 0.5초 섬광 경직, 쿨 30초) |
| 60 | 듀오 합동기 「쌍낙인 폭주」: 낙인 공명 중 동시 돌진 X자 베기, 흡수 게이지 즉시 1칸 |
| 80 | 장면 「노을빛 왕도 산책」: 등불 축제 저녁, 성벽 위에서 고향 이야기와 「여기도 나쁘지 않네」 |
| 100 | 엔딩 후일담: 차원 균열 앞에서 귀환/잔류 선택 — 잔류 시 필멸자의 집에 함께 사는 장면, 귀환 시 현대 거리에서 낙인이 빛나는 여운 |

- Visual (EN): curvy adult modern-world woman (mid-20s), long straight black hair with bangs, violet eyes, white off-shoulder puff-sleeve crop top showing midriff, black pleated mini skirt with chain belt, black thigh-high stockings, black choker with heart pendant, short ornate sword at hip, cheerful but homesick vibe
- CG `lantern street greeting`: black-haired woman with bangs in white off-shoulder crop top and black pleated mini skirt waving on a lantern-lit fantasy street at sunset (sample, cg_d_yuna_1.jpg)
- CG `fallen from the sky`: black-haired modern woman in white crop top sitting dazed among glowing ruins outside a castle wall, holding a dead smartphone, short sword beside her
- CG `rampart sunset talk`: black-haired woman in black choker sitting on a castle rampart at dusk beside the viewer, lanterns below, wistful smile

## 대사 표정 교체 훅

각 히로인 `lines[]`의 대사마다 `expr`(normal/smile/angry/blush)이 있다. 대화창은 `portraits/<id>_<expr>.png`를 띄우고, 파일이 없으면 `portraits/<id>.png`(normal)로 대체한다. 퀘스트 대사 등 다른 대사에도 같은 `expr` 필드를 붙이면 된다 (game.template.html은 아직 수정하지 않음 — 대화창 렌더에서 이 규칙만 적용하면 됨).
