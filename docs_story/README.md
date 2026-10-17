# docs_story — 스토리 대본 · 설정안 (1차: 시작 마을 A + 1지역)

게임 코드·지도·데이터 원본은 건드리지 않은 문서 묶음이다. 각 항목은 사람이 읽는 `.md`와 게임에 넣기 쉬운 `.json` 한 쌍이다 (JSON은 md와 같은 원본에서 생성, `python3 -m json.tool`로 파싱 검증).

| 파일 | 내용 |
|---|---|
| `town_A_npcs.md` / `.json` | A 시작 마을 NPC 10명 대사 전체 + 칭호(영웅/필멸자/필멸자·악명/타락한 필멸자/마왕)별 분기, 마왕 루트 파괴·아이 대피 규칙 |
| `town_A_events_quests.md` / `.json` | 마을 이벤트 8개(프롤로그~잿빛 분수 터), 퀘스트 A1~A11 대사(offer/progress/done), 보상 아이템 목록 |
| `chests_A_area1.md` / `.json` | 마을 A + 1지역 상자: 기존 상자 정리, 찾기 쉬운 숨은 상자, 나중 능력/열쇠 상자 |
| `heroine_quests.md` / `.json` | 히로인 7명 등장 장면 + 호감도 대화 3단계(20/60/80), 리네트(옛 나비) 동료 퀘스트(A_TAILOR1~3) 대본. 나머지 6명 동료 퀘스트 대본은 다음 작업 |
| `main_story.md` | **게임 전체 메인 스토리 줄거리** — 「필멸자」(가제). 억겁의 불사자 주인공, 반전 3개, 지역별 장, 칭호별 엔딩 4종, 히로인 엔딩 |
| `spirit_removal.md` | 정령(이슬/에스라) 삭제에 따른 게임 요소 대체안 + 코드에서 바꿀 파일 목록(수정은 안 함) |
| `ult_unlock_event.md` | 필살기(R) 해방 중반 이벤트 「낙인의 개화」 (4지역 세트라 흡수 + 전생 기억) |
| `names_eldenring.md` | 엘든링풍 이름표 — **확정 (2026-10-17 사장님 승인), docs_story 전체 적용 완료** |

## 대사 형식

```json
{"speaker": "리네트", "expression": "smile", "text": "역시! 같이 오길 잘했어요."}
```

- `expression`: `neutral` `smile` `angry` `sad` `surprised` `blush` 중 하나. 지금 있는 초상화는 normal/smile/angry/blush라 `neutral`→normal, `sad`·`surprised`는 파일이 생기기 전까지 normal로 대체.
- `speaker` 「필멸자」 = 주인공. 화면에는 현재 칭호로 표시. 「나레이션」은 이름표 없이.
- 칭호 분기 키: `hero`(선악 +40↑) / `mortal`(-19~+39) / `mortal_infamous`(-20~-39, 칭호는 필멸자지만 선악 등급이 「악명」이라 선의 퀘스트·동료가 거절) / `fallen`(타락한 필멸자 -40~-59) / `demon_king`(강림 후).

## 규칙 준수

- 여성 캐릭터는 모두 성인(설정 나이 그대로), 장면·대사는 비노출·비선정. 외모·신체 묘사 대사 없음.
- 미성년자(청소년 토비와 아이들)는 어떤 루트에서도 죽일 수 없다 — 마왕 루트에서는 대피 연출만, 성적 묘사 없음.
- 유나만 현대 세계 출신(현대 말투·현대 복장), 나머지 6명은 판타지 세계 출신. 히로인 대사는 설렘 정도의 로맨스까지.
- 말투: 판타지 세계 인물 대사는 엘든링풍(고어체, 묵직하고 쓸쓸한 톤). 마을 A NPC 10명 대사·퀘스트 대사도 확정 이름과 함께 다듬음(악명 분기 대사도 towns.json `greeting_dark` 대신 새로 씀). 토비는 15~16세 청소년 말투(팀장 결정), 유나는 현대 말투 유지.
- `speaker`는 칭호 없는 짧은 이름(예: 「오스왈드」). 칭호는 `town_A_npcs.json`의 `title`, 옛 이름은 `former_name`에 둠 — 대사창 이름표에 칭호를 붙일지는 미정.

## 팀장 결정 반영 (2026-10-17)

1. **주인공 나이 17세 → 성인 20세.** docs_story 안은 반영 완료(프롤로그 「스무 번째 생일 밤」, 바렌(옛 칼바람)·엘스베트(옛 물결 할머니) 대사 「20년 전」). 리네트(옛 나비) 대본은 호감도에 따라 설렘이 묻어나는 로맨스 톤(비노출·비선정)으로 수정.
   - **팀장이 수정 필요 (docs_story 밖, 손대지 않음)**: `STORY.md`, `TOWNS.md`, `TOWNSFOLK_COMBAT.md`, `data/towns.json`, `tools/design/story_data.py` — 「열일곱 번째 생일」「17년」 표현.
2. **바람길 「나그네 보리」 개명.** 새 이름은 「바람길의 순례자」 퀸트(**확정**). 농부 보리도 이름표에 따라 「허수아비지기」 하로로 **확정**. docs_story 본문에는 나그네가 등장하지 않아 이 README만 해당.
   - **팀장이 수정 필요**: `town/maps/field00.json`(npc_bori name), `town/tools/world_maps.py`, `town/maps/quests.json`(giver `npc_bori` — ID도 바꿀지 결정).
3. **리네트(옛 나비) 무기 = 재봉 바늘 두 자루 (HEROINES.md 기준).** 대본의 「가위」 표현 제거. **팀장이 수정 필요**: `data/towns.json`·`TOWNS.md`·`TOWNSFOLK_COMBAT.md`의 나비 전투 「재봉 가위 찌르기」.
4. **마을 A 상자 위치**: 좌표 없이 「구역 — 장소의 느낌」으로 다시 씀 (`chests_A_area1`).
5. **히로인 6명 등장 장면 + 호감도 대화 3단계 추가** (`heroine_quests`).

## 설정상 불분명했던 점 (확인 필요)

1. ~~주인공 나이 17세~~ → 해결: 20세로 결정 (위 1번).
2. **칭호 vs 선악 등급**: 칭호(영웅 +40 / 필멸자 ±39 / 타락한 필멸자 -40~-59)와 거절 기준(「악명」 -20 이하)이 어긋난다 → `mortal_infamous` 분기를 따로 둠. 악명 대사는 원래 `towns.json`의 `greeting_dark`였으나 엘든링풍으로 새로 씀(towns.json 쪽 교체는 팀장 판단).
3. ~~보리 두 명~~ → 해결: 나그네 개명 (위 2번). 원래 내용: 마을 A의 「농부 보리」(towns.json)와 바람길 지도의 「나그네 보리」(`npc_bori`, 음유시인 스프라이트, q_forest_chiefs 의뢰인)가 같은 이름이다. 같은 사람인지 확인 필요.
4. **quests.json 위치**: WORLD.md는 `maps/quests.json`이라 쓰지만 실제 파일은 `town/maps/quests.json`(1지역 퀘스트 2개뿐). 루트 `maps/`에는 PNG만 있다.
5. **heroines_data.py 경로·개수**: 실제 경로는 `tools/design/heroines_data.py`(town/ 아래 아님). 머리 주석은 「히로인 6명」인데 목록은 7명(유나 추가).
6. **A_TAILOR3 장소**: 원문 「B 강변 수정 동굴 입구」 — 수정 동굴은 2지역(바람길 남쪽 낙석 너머·H 근처)이라 「낙석이 치워진 뒤 수정 동굴 입구」로 해석했다.
7. **없는 몹**: A_TAILOR1의 거미, A_TAILOR2의 까마귀가 1지역 몹 목록(WORLD_PLAN.md)에 없다 → 색 변형 몹(은실거미·까마귀) 제안.
8. **숲의 단검 위치 불일치**: DIVE_SPOTS.md 표 순서로는 「버섯 군락 옆 늪」, ITEMS.md는 「큰 나무 뿌리 사이 샘」. 상자 JSON은 DIVE_SPOTS 기준.
9. ~~리네트(옛 나비)의 전투 묘사 불일치~~ → 해결: 바늘 (위 3번). 원래 내용: HEROINES.md는 재봉 바늘 두 자루, towns.json 마을 사람 전투는 「재봉 가위 찌르기·실타래 던지기」. 대본은 바늘로 씀.
10. **마을 A 지도**: A의 타일 지도 JSON이 없어 마을 상자 위치는 말로만 적었다. 촌장집 연못(잠수 지점)의 위치. (「분수 옆 연못」의 탁블레이드 상자는 숨은 검 해금 조건이 바뀌어 삭제했다.)
11. **보상 아이템 ID**: 「거친 수정 원석」「물방울 무늬 망토」「어머니의 편지」(→ 어머니 설정 삭제로 「요람의 장부 조각」 `k_cradle_page`)「나비 리본 망토」「망토 염색 무료권」 등은 이름만 있고 ID가 없어 `proposed_id`로 새 ID를 붙였다.
12. **「나비」가 들어간 아이템 이름**: 「나비 리본 망토」(`c_cape_nabi_ribbon`)·「나비 골무 부적」은 히로인 이름이 아니라 나비(butterfly) 무늬로 보고 그대로 뒀다. 히로인 이름을 딴 상점명은 「리네트 재봉소」로 바꿨다. 아이템명도 바꿀지 팀장 결정.

## 이름표 확정 적용 (2026-10-17, 사장님 승인)

docs_story 안 md/json 전체에 `names_eldenring.md` 이름을 적용했다(`speaker` 포함). 주인공 「필멸자」와 「이름 유지」 인물(카이렌·아스란·오르비스·자흐라·마고·가론·그림·아르덴·세린·루미엘·레온·사바·세트라·바르·미레·유나)은 그대로.

| 옛 이름 | 확정 이름 |
|---|---|
| 촌장 한결 / 미소 / 강철 / 나비 / 물결 할머니 / 도토리(아이) / 바위 / 보리(농부) / 소담 / 가락 | 오스왈드 / 미라벨 / 브란트 / 리네트 / 엘스베트 / 토비 / 베른 / 하로 / 세레스 / 라우렌 |
| 나그네 보리 / 운 / 방울 / 숨비 / 루비 / 설화 | 퀸트 / 베일라 / 자이라 / 마렌 / 로자린드 / 이벨린 |
| 이슬 / 칼바람 / 매눈 솔 / 곰쇠 / 한빙 / 먼지 / 책벌레 연 / 은갑 / 흑갑 / 불칼 / 거북 / 돌쇠 / 돌님 | (에스라 — 정령 삭제로 미사용) / 바렌 / 솔렌 / 고름 / 하르빅 / 더스턴 / 이브넬 / 실반 / 모르반 / 볼칸 / 토르투 / 도르크 / 넬 |

### 팀장이 수정 필요 — docs_story 밖에서 옛 이름이 남은 파일 (직접 수정하지 않음)

옛 이름 문자열 검색 결과(origin/main 기준). 「바위·운·방울·루비·먼지·강철·도토리·미소·나비·거북」은 일반 낱말(돌, 운명, 물방울, 보석, 강철 재질, 도토리 재료, 웃음, 나비 무늬, 거북 몹 등)과 겹치므로 파일마다 인물 이름인지 확인해야 한다. ID(`a_chief`, `npc_bori` 등)와 초상화 파일명은 ID 기반이라 그대로 두어도 되고, 표시 이름(`name`)만 바꾸면 된다.

- **설정 문서**: `STORY.md`, `TOWNS.md`, `TOWNSFOLK_COMBAT.md`, `HEROINES.md`, `SYSTEMS.md`, `MATERIALS.md`, `ITEMS.md`, `EQUIPMENT.md`, `CRAFTING.md`, `LEVELS.md`, `CONTROLS.md`, `WORLD_PLAN.md`, `BGM.md`, `STORY_GUIDE.md`, `MONSTERS.md`, `BOSS_PATTERNS.md`, `DIVE_SPOTS.md`, `CREDITS.md`, `town/WORLD.md`, `town/TACHIE.md`, `town/BALANCE_TODO.md`
- **게임 데이터**: `data/towns.json`(NPC·강자·히로인 `name`, `greeting_dark`), `data/levels.json`, `town/maps/field00.json`(나그네 `npc_bori` name), `town/maps/quests.json`(giver `npc_bori`)
- **데이터 생성 스크립트**: `tools/design/towns_data.py`, `tools/design/story_data.py`, `tools/design/heroines_data.py`, `tools/design/craft_data.py`, `tools/design/level_data.py`, `tools/design/difficulty_data.py`, `tools/design/gen_docs.py`, `tools/build_art.py`, `town/tools/world_maps.py`
- **게임 코드·화면**: `town/index.html`, `town/tools/game.template.html`, `town/world.js`, `town/world_mobs.js`, `town/tachie.js`, `town/tools/tachie/chars.js`, `town/tools/tachie/chars2.js`, `old_proto.html`
- **아트 색인**: `art/npcs/INDEX.md`, `art/npcs/portraits/index.json`, `art/icons/INDEX.md`, `art/icons/icons.json`, `art/mobs/INDEX.md`, `town/assets/portraits/index.json`, `town/assets/bust/index.json`, `town/assets/tachie/index.json`, `town/assets/icons/icons.json`, `town/assets/icons/items_demo.json`, `docs_art/bust/README.md`, `town/tools/import_bust.py`, `town/tools/tachie/sheets.py`, `town/tools/tachie/make_index.py`, `town/style_sample/tools/compose.py`
- **테스트**: `town/tools/test_world.py`, `town/tools/test_tachie.py`, `town/tools/test_inventory.py`, `town/tools/test_shop_sell.py` (이름 문자열을 확인하는 테스트는 데이터와 함께 고쳐야 함)
- **숨은 검 새 해금 조건 (사장님 확정)**: 탁블레이드 = 3번째 보스(모래 대지렁이) 처치, 규블레이드 = 6번째 보스(산호 거대게) 처치, 찬블레이드 = 8번째 보스(뇌전 와이번) 처치 직후 폭풍지기의 첨탑에서 두 검이 하나가 됨. 옛 조건(강자 8명 생존 + A 연못 상자 `a_chest_tak`, H 지하 수원 잠수 + 보스 10마리, E 대장간 등급 10 + 볼칸 생존 + 금화 5000 융합 `f_hs_chan`)은 모두 삭제한다. 고칠 곳: `ITEMS.md`(숨겨진 전설검 절), `STORY.md`, `SYSTEMS.md`, `TOWNS.md`, `EQUIPMENT.md`, `CRAFTING.md`(융합 레시피), `data/towns.json`(`hs_*` 항목, `f_hs_chan`), `tools/design/story_data.py`(HS 정의), `tools/design/craft_data.py`(`FUSION_RECIPES`), `tools/design/towns_data.py`, `tools/design/gen_docs.py`(「마스터 대장간에서 탁검+규검 융합」 문구·assert), `town/tools/game.template.html` → `town/index.html`(상자·해금 판정), `town/tools/test_shop_sell.py`. 숨은 검 표시 이름도 탁블레이드·규블레이드·찬블레이드로 바꾼다.
- **은팔찌 흔적 (은팔찌 설정 삭제)**: `SYSTEMS.md` 115행·`data/towns.json`·`tools/design/story_data.py` 80행의 「HUD: 팔찌의 이슬 보석 색」 → 손등 낙인 문양 HUD로 교체(`spirit_removal.md`), `old_proto.html`(옛 프로토타입의 「은빛 팔찌」 대사 2곳).
- **스토리 개연성 개편 (카이렌 삭제, 원탁 하나로 통합, 마룡 → 「삼킨 자」)**: 카이렌·사도단·마룡이 남은 docs_story 밖 파일. 설정 문서 `STORY.md`, `BOSS_PATTERNS.md`(10지역 보스·카이렌 패턴 → 아스란과 「삼킨 자」), `WORLD_PLAN.md`, `HEROINES.md`, `TOWNS.md`, `SYSTEMS.md`, `ITEMS.md`, `EQUIPMENT.md`, `MATERIALS.md`, `CRAFTING.md`, `MONSTERS.md`, `LEVELS.md`, `CONTROLS.md`, `DIVE_SPOTS.md`, `TOWNSFOLK_COMBAT.md`, `BGM.md` / 데이터 `data/towns.json`, `data/levels.json`, `audio/bgm/bgm.json`, `town/maps/world.json` / 스크립트 `tools/design/story_data.py`, `towns_data.py`, `heroines_data.py`, `level_data.py`, `craft_data.py`, `gen_docs.py`, `town/tools/world_maps.py`, `town/tools/paperdoll.py` / 게임 `town/tools/game.template.html` → `town/index.html` / 아트·아이콘 `art/icons/INDEX.md`, `art/icons/icons.json`, `art/skills/INDEX.md`, `town/assets/icons/icons.json`, `town/assets/icons/items_demo.json` / 음악 `docs_music/gemini_prompts.md`, `docs_music/matching_table.md`, `tools/music/V2.md`, `tools/music/gen_doc.py`, `tools/music/songs/area10_dragon_nest.py`, `tools/music/songs/battle_kairen.py`(곡 용도를 아스란 최종전으로).
- **음악 문서**: `docs_music/gemini_prompts.md`, `docs_music/SFX_LIST.md`, `docs_music/sfx_draft/index.html`, `tools/music/gen_doc.py`, `tools/music/songs/area02_cave.py`

## 메인 스토리 개편 반영 (2026-10-17)

- 제목 「필멸자」(가제). **정령 이슬/에스라와 주인공의 어머니는 이야기에서 삭제.** 주인공은 분수 가에서 발견된 업둥이(억겁을 다시 태어나 온 불사자) — 상세는 `main_story.md`.
- docs_story 안의 정령·어머니 대사를 교체함: 프롤로그 에스라 대사 → 엘스베트 「세 번째 붉은 물」, 골렘 귀환 → 바렌, 원탁의 심연 → 오스왈드, 여덟 맹세 → 나레이션. 오스왈드·엘스베트의 「네 어미」 대사 → 「스무 해 전 바구니」로 바꿈. A6 보상 「어머니의 편지」(`k_mother_letter`) → 「요람의 장부 조각」(`k_cradle_page`, 신규 ID 제안). 필살기 해방 문서는 정령 없이 다시 씀.
- 아이템 ID(`spirit`·`spirit_hi`·`spirit_drop`)는 그대로 두고 표시 이름만 바꾸기를 제안함(`spirit_removal.md`).
- **팀장이 수정해야 함 (docs_story 밖)**: `spirit_removal.md`의 「코드·데이터에서 바꿀 곳」 목록 참고.
- **목 베기 개념 삭제 (사장님 지시)**: 불사자는 보통의 죽음이면 기억을 잃고 다시 태어나고, 다른 불사자의 손에 죽으면 완전히 끝나며 죽인 쪽이 힘과 기억을 흡수한다. docs_story 전체에서 목 베기 표현을 「죽인다」로 바꿨다. A8 제목 「스승의 목」 → 「스승의 최후」(**팀장 수정 필요**: `data/towns.json`·`TOWNS.md`·`tools/design/towns_data.py`의 A8 제목).

## 숨은 검 이름 확정 · 세계 이름표 · 전체 스토리 (2026-10-17)

- **숨은 검 확정 (사장님)**: 탁검 → 탁블레이드, 규검 → 규블레이드, 찬검 → 찬블레이드. docs_story 전체에 적용했다. docs_story 밖의 ITEMS.md 등은 팀장이 수정해야 한다.
- `names_world.md`: 마을·지역·던전, 장비 전체, 소모품·재료, 능력 이름의 개편안이다. 숨은 검만 확정이고 나머지는 승인 대기다.
- `story_full.md`: 프롤로그부터 엔딩 4종까지 장·지역·마을 순으로 엮은 전체 스토리다. `main_story.md`를 기준으로 히로인 퀘스트, 필살기 해방, 반전, 칭호 분기, 숨은 검을 장마다 넣었다.
- `main_story.md`에 남아 있던 「목을 거두고」 표현 2곳을 「죽여 힘을 거두고」로 고쳤다.

## 은팔찌 삭제 · 숨은 검 해금 조건 변경 (2026-10-17, 사장님 지시)

- **은팔찌 삭제**: 은팔찌와 거기에 딸린 설정을 docs_story 전체에서 뺐다. 선악 표시는 손등 낙인 문양이 맡고, 유품 역할은 「요람의 장부 조각」과 잃은 기억이 맡는다.

| 빠진 것 | 대체 |
|---|---|
| `names_world.md` 「어머니의 은팔찌 → 은팔찌」(힘 없는 유품) 줄 | 줄 삭제. 업둥이의 과거를 알려 주는 물건은 「요람의 장부 조각」(A6)이 맡는다 |
| `spirit_removal.md`의 「팔찌 보석 색 선악 표시」와 「팔찌 오브젝트를 그림에서 지운다」 | 「보석 색 선악 표시」(HUD 보석 아이콘)로 적고, 대체는 그대로 손등 낙인 문양 |
| `main_story.md` 삭제 목록의 「은팔찌 포함」 | 문구 삭제 |

- **숨은 검 해금 조건 (사장님 확정)**: 탁블레이드는 3번째 보스, 규블레이드는 6번째 보스, 찬블레이드는 8번째 보스를 처치하면 얻는다. `main_story.md`, `story_full.md`, `names_world.md`의 동선을 고쳤다. A 연못 상자(`a_chest_tak`, `chests_A_area1.*`)와 이벤트 「여덟 개의 맹세」(`ev_a_takgeom`, `town_A_events_quests.*`)는 삭제했다.

## 스토리 개연성 개편 (2026-10-17, 사장님 지시 「단순하고 탄탄하게」)

- `main_story.md`, `story_full.md`를 다시 썼다. 전체 줄거리, 바뀐 점 표, 인과 체크리스트는 `story_full.md`에 있다.
  - 반전은 2개다. ① 억겁의 불사자(4장 세트라 → 귀향의 요람의 장부) ② 최종 보스 아스란은 옛 제자(9장 오르비스·그림 → 최종장). 「모든 낙인은 주인공의 조각」 반전은 삭제했다.
  - 카이렌을 삭제하고 아스란 한 명으로 합쳤다. 최종 형태는 아스란이 삼킨 불사자 서른일곱의 힘이 폭주한 「삼킨 자」다.
  - 적 세력은 「심판의 원탁」 하나다. 사도단은 오르비스 휘하 「원탁의 수확자」로 흡수했고, 왕가와 처형인 가문은 원탁의 손발이다.
  - 숨은 검은 스승이 제자를 죽이지 않으려고 직접 셋으로 나눈 칼이다. 3·6·8번째 보스는 그 칼을 지키다 타락한 수호자다.
  - 귀향은 4장 바로 뒤로 옮겼다.
  - 타락한 필멸자 엔딩 이름을 「미뤄진 날」로 바꿨다.
  - 유나의 문양은 물길 결박 동판의 각인으로 바꿨다.
- 함께 맞춘 문서
  - `names_world.md`: 5·6·10지역 이름, 마룡·카이렌·사도단 계열 아이템과 능력 이름.
  - `names_eldenring.md`: 카이렌 삭제 표시. 아스란, 오르비스, 하르빅, 더스턴, 모르반, 볼칸, 사바, 세트라, 바르, 토르투, 바렌, 이벨린의 소개.
  - `ult_unlock_event.md`: 세트라의 계약 상대와 귀향 시점.
  - `heroine_quests.md`/`.json`: 유나의 귀환 방법.
  - `town_A_events_quests.md`/`.json`: 사도단 첩자 → 원탁의 수확자, 낙인 목소리 → 아스란(존댓말), 원탁의 심연 조건.
- **추가 확정 (서른아홉의 명단)**
  - 스승이 사라진 해 남은 불사자는 39명이었다. 아스란은 폭풍지기의 첨탑 일지에서 그 명단을 찢어 갔고, 스승과 자신을 뺀 37명을 처형인의 칼로 끝냈다.
  - 8장에는 찢긴 일지를, 9장 그림의 증언에는 명단의 위치를 넣었다.
  - 숨은 장에서 이야기 아이템 「서른아홉 이름의 명단」(`k_list_39` 제안)을 얻는다. 37개 이름에 줄이 그어져 있고 맨 위 한 줄(스승)만 비어 있어, 장부의 지워진 이름과 짝을 이룬다.
  - 인과 체크리스트에 3문항을 추가했다.
- **추가 확정 (마왕 루트 인간 마을 습격)**
  - 3·6·8번째 보스 시점마다 마왕이 가장 가까운 사람 마을(G 사르칸드, F 그레이마우스, C 하르발트)을 습격해 산 어른의 혼을 삼킨다. 기존 마을 파괴 이벤트를 강제로 여는 형태다.
  - 아이는 모두 대피하며 흡수 대상이 아니다. 연출은 절제한다.
  - 습격으로 얻는 능력은 심연의 촉수, 마염 파동, 굶주림의 포효다.
  - (제안) 마왕 상태에서는 수호자가 칼을 거절한다. 이 안을 확정할지는 사장님 결정이 필요하다.

- **히로인 메인퀘스트 구조 (사장님 지시 2026-10-18)**
  - 지역마다 마을 → 히로인 등장 → 히로인 메인퀘스트 → 동료 합류 → 그 히로인과 함께 보스전 순서로 진행한다.
  - 히로인이 없는 지역(4장 능묘·6장 절벽·숨은 장·최종장)은 이미 동료가 된 히로인 중 1명을 플레이어가 고른다. 새 히로인은 넣지 않는다(사장님 확정).
  - 새 문서 `heroine_mainquests.md`: 매핑표, 히로인별 메인퀘스트, 보스전 협공과 대사(선택 보스전은 히로인마다), 리네트 전투안, 결정할 질문.
  - `novel.md`를 이 순서로 재정렬했다(각 장 머리에 메인퀘스트 상자). `heroine_quests.md/.json`에 `main_quest`·`main_quest_rules`, `story_full.md` 각 장에 동행 줄을 추가했다.
  - 채팅용 분할본: `quest_parts/`(보고용), `novel_parts/`(소설 본문).

- **토비 연령 변경 (팀장 지시 2026-10-18)**: 토비를 아이에서 15~16세 청소년(미성년자)으로 바꿨다. 역할(프롤로그 납치, A3, 대피 이벤트, 죽일 수 없음)은 그대로다. 「꼬마」 호칭과 아이 말투를 고쳤고, A3 보물지도는 「열 살 때 묻어 둔 것」으로 바꿨다. 마왕 루트에서 토비는 다른 아이들과 함께 여전히 행방불명이다. `town_A_npcs.json`의 `id: a_kid`·`is_child`는 코드 호환을 위해 그대로 두고 `age`·`is_minor`를 추가했다.
