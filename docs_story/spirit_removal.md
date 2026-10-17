# 정령 요소 제거안 — 「필멸자」(가제)

> 새 메인 스토리(`main_story.md`)에서는 정령 이슬/에스라와 주인공의 어머니가 모두 빠졌다. 그래서 게임 코드에서 빠질 정령 요소마다 대체안을 정리한다. **이 문서는 제안이고, 코드는 수정하지 않았다.** 아이템 ID(`spirit` 등)는 세이브 호환을 위해 그대로 두고, 표시 이름·대사·연출만 바꾸기를 권한다.

| 빠지는 요소 | 대체안 |
|---|---|
| **동행 정령 이슬** (마을 안 NPC `spirit`, 초상 `spirit_iseul`) | 정령 NPC와 초상을 삭제한다. 동행 칸은 히로인 7명만 쓴다(기존 동료 시스템 그대로). 정령이 하던 체력 회복은 회복약과 히로인 이벨린의 「눈꽃 축복」이 맡는다. |
| **이슬 대화** (「이슬과 대화」 상호작용, 힌트·잔소리 역할) | **추천: 사범 바렌.** 마을 안에서는 도장에서 직접 가르치고, 마을 밖에서는 「바렌의 가르침」이라는 회상 대사로 같은 힌트를 띄운다. 주인공 손등을 내려다보는 짧은 컷과 함께 바렌의 목소리가 나온다. 「발을 멈추지 마라. 막지 말고 굴러라.」 반전 1(몸이 3백 년 전 자세를 안다)의 복선도 겸한다. **대안**: ① 장로 오스왈드(저장·카르마·마을 시스템 안내 전담, 바렌과 나눠 맡기) ② 「낙인의 울림」(전생의 자신이 낮게 속삭이는 목소리). ②는 4지역 반전 1을 미리 드러내므로 4지역 이후 고급 안내(필살기·흡수 선택)에만 쓴다. |
| **팔찌 보석 색 선악 표시** (HUD, SYSTEMS.md 「팔찌의 이슬 보석 색」) | **손등 낙인 문양**이 대신한다. HUD에서 주인공 체력바 옆 손등 아이콘으로 보이고, 칭호 4단계와 연동된다. 영웅은 은백색 흉터로 가라앉은 문양이다. 필멸자는 검붉은 가는 선이며, 「악명」(-20~-39)이면 끝이 살짝 번진다. 타락한 필멸자는 붉은 실핏줄이 손목까지 번지고 맥박처럼 깜빡인다. 마왕은 팔뚝까지 검게 타서 갈라진 틈에서 붉은빛이 샌다. 숫자는 지금처럼 상태창에만 둔다. 팔찌 오브젝트는 그림에서 지운다(어머니 설정 삭제로 은팔찌도 없음). |
| **광역 마법 「정령 파동」** (Q, MP 30, 둘레 원형 · `?area=spirit`) | **「천생잔영(千生殘影)」**으로 바꾼다. 낙인이 한 번 울리면 주인공 둘레에 지난 생의 검사 잔영 여섯이 원을 그리며 나타나, 바깥쪽으로 동시에 베고 재처럼 흩어진다. 판정·수치는 기존 정령 파동과 같다(원형 반경 약 190, 적마다 20 피해 + 밀쳐내기). 4지역 이전에는 잔영의 얼굴이 그림자로 가려지고, 4지역 이후에는 얼굴이 보인다(반전 1 연출). 마왕 쪽 「마염 파동」은 그대로 둔다. |
| **아이템 「정령수」 / 「상급 정령수」** (`spirit` MP 30 회복 / `spirit_hi` MP 전부 회복) | **「요람의 샘물」 / 「짙은 요람의 샘물」**. 업둥이들이 떠오른 분수의 물로, 마시면 낙인의 열이 가라앉는다(MP 회복). 다른 이름 후보는 **「잿빛 밀랍」**(망자의 촛불에서 긁어낸 밀랍. 사막·피라미드 상점용 또는 다크 톤 대체 이름)이다. |
| **아이템 「정령의 이슬」 / 「정령의 물방울」** (`spirit_drop` 최대 MP +1칸 성장, 잠수 지점 8개) | **「가라앉은 기억」**. 물길 밑바닥에 가라앉은 지난 생의 기억 조각으로, 주워 쥐면 최대 MP가 오른다. 「불사자의 혼은 물길로 가라앉는다」는 세계의 법과 바로 이어진다. SYSTEMS.md의 「원한의 조각」 대체 규칙은 그대로 둔다. |

## 코드·데이터에서 바꿀 곳 (grep 결과, 파일명 수준, 수정하지 않음)

- 검색어: `이슬` `정령수` `정령 파동` `정령의 이슬` `정령의 물방울` `spirit` `spirit_drop` `spirit_hi` `spirit_iseul` `area=spirit` `보석`
- 게임·데이터:
  - `town/tools/game.template.html` → `town/index.html`(생성물): 이슬 NPC·대화·초상, Q 정령 파동, 아이템 이름
  - `town/world.js`: 아이템 이름표 `spirit_drop: '정령의 이슬'`
  - `data/towns.json`, `data/levels.json` 및 생성기 `tools/design/towns_data.py`, `story_data.py`, `level_data.py`
  - `town/maps/field01.json`, `town/tools/world_maps.py`
  - `town/assets/sprites.json`, `town/assets/portraits/index.json`, `town/assets/icons/icons.json`, `town/assets/icons/items_demo.json`, `art/icons/icons.json`, `art/npcs/portraits/index.json`, `town/tools/icon_prompts.py`, `town/tools/extract.py`
  - 테스트: `town/tools/test_controls.py`, `test_tachie.py`, `test_ui_translucent.py`
- 문서: `STORY.md`, `SYSTEMS.md`(팔찌 보석 HUD, -50 이슬 경고), `ITEMS.md`, `LEVELS.md`, `CONTROLS.md`, `DIVE_SPOTS.md`, `TOWNS.md`, `EQUIPMENT.md`, `STORY_GUIDE.md`(SPIRITS 블록), `town/TACHIE.md`, `art/icons/INDEX.md`
- 함께 정리할 어머니 관련 항목: A6 「분수 밑의 반짝임」의 보상 「어머니의 편지」 → 「요람의 장부 조각」 제안(`data/towns.json`, `TOWNS.md`, `tools/design/towns_data.py`)
