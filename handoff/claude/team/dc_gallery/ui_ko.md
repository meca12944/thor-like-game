# DC 「AI 게임 개발 마이너 갤러리」(id=aidevelop) — UI·조작·카메라 팁 (2번방, 2026-10-27)

> 사장님 「정보 싹 긁어와」. 디시는 봇이 열면 빈 페이지라 **원문을 열지 않고 검색엔진 요약만** 모았다 (막힌 것은 뚫지 않음).
> 그래서 글 본문 전체가 아니라 요약에 나온 내용만 있다. 갤러리 이름은 「AI 게임 개발」(생성형 AI로 게임 만드는 정보 나누는 곳).
> 이 갤러리에 UI·카메라 글은 많지 않다. 비슷한 내용이 있는 옆 갤러리(인디 게임 개발 game_dev, 고도엔진 godot) 글은 「옆」이라고 적었다.

## TOP 3 (우리 게임에 바로 쓸 것)

1. **처음부터 끝까지 직접 해 보는 점검표** (aidevelop 2062)
   - 조작이 어색하거나 아예 안 먹는 곳이 없는지, 글자가 화면 밖으로 나가지 않는지, UI가 읽기 쉬운지 하나하나 본다.
   - 우리 것: test_openworld 는 「돌아가나」만 본다 → **「PC 1280×720 한 바퀴 점검표」**(메뉴·가방·상점·대화·전망 장면에서 글자 잘림·겹침)를 시험에 넣자.
2. **잘된 게임과 나란히 놓고 비교** (aidevelop 2498)
   - AI 느낌을 없애려면 내가 재밌게 한 게임 화면과 나란히 보며 「만든 사람이 왜 이렇게 했나」를 생각한다.
   - 우리 것: 주인공 동작 비교표(옛 vs 새)처럼, **UI도 같은 장면을 참고 게임과 나란히 찍은 비교판**으로 고르면 사장님이 고르기 쉽다.
3. **「이상해, 고쳐줘」 말고 숫자·그림으로 말하기** (aidevelop 2062, 옆 game_dev 151358)
   - 「움직임이 이상해 고쳐줘」를 되풀이하면 코드가 점점 꼬인다. 원하는 느낌의 참고 그림·스크린샷을 같이 주면 UI가 훨씬 낫게 나온다.
   - 우리 것: 이미 하는 방식(숫자 표·전후 영상)을 계속. 사장님 지시가 「느낌」일 때는 **참고 화면 1장**을 같이 받자고 추천.

## 팁 표

| 팁 | 글 번호 | 우리 게임에 쓸 수 있나 | 왜 |
|---|---|---|---|
| 오른쪽·아래에 따로 있던 UI 칸을 게임 화면 위에 겹쳐(오버레이) 정리했다 | aidevelop 98 | ✔ 이미 그렇게 함 | 우리 HUD 도 게임 화면 위에 그림. PC 와이드에서 칸을 따로 떼면 게임 화면이 작아짐 |
| 아이콘 없는 메뉴는 허전해 보인다 (기능은 돼도) | aidevelop 98 | ✔ | 그록 아이템 아이콘 131개를 넣은 이유와 같음. 남은 곳: 왼쪽 위 물약 동그라미, 스킬 칸 |
| 끝까지 직접 플레이하며 조작 먹통·글자 화면 밖·읽기 어려운 UI 를 본다 | aidevelop 2062 | ✔ TOP1 | 자동 시험이 못 잡는 「보기 불편함」 |
| 「움직임 이상해 고쳐줘」 반복 → 코드가 꼬임 | aidevelop 2062 | ✔ TOP3 | 숫자 기준(hero_check·mob_check)으로 말하는 우리 방식이 맞음 |
| 내가 재밌게 한 게임과 비교해 만든 사람 의도를 생각 | aidevelop 2498 | ✔ TOP2 | UI·카메라 고를 때 비교판 |
| 타격감: 물리 조금 + 피 튀김 + 이펙트 추가, 카메라 방식(TPS) 바꾸기 버튼 | aidevelop 5351 | △ 일부 | 우리는 탑다운이라 TPS 는 안 맞음. 타격 효과는 이미 코드(멈춤·흔들림·불꽃) → 피는 연령 등급 생각해서 |
| 플레이 영상 올려 피드백 받기 | aidevelop 4477 | ✔ | 우리도 MP4 로 보고 |
| AI 로 만든 움직임 그림은 장마다 캐릭터가 달라지고 배경이 붙어 나옴 → 투명 배경 정리에 손이 많이 감 | 옆 game_dev 151358 | ✔ 알고 있음 | 그록 아이콘 자를 때도 바탕 빼기·칸 맞추기가 일의 대부분이었음 |
| 원하는 분위기를 말로 길게 설명해 메뉴 UI 를 뽑음 | 옆 game_dev 151358 | △ | 그림은 그록/PixelLab 담당. UI 틀은 코드라 참고 그림 1장이 더 빠름 |
| 픽셀 게임 화면 크기는 320×180·480×270·640×360 처럼 잡고 **정수배**로 키워야 안 깨짐 | 옆 game_dev 213451 | ✔ 이미 함 | 우리 PC 화면 맞춤(screenFit): 정수배 켜기/끄기 있음 |
| 글자 많은 게임은 960×540 창 + 정수배만 늘리기 (FHD = 딱 2배) | 옆 godot 3756 | ✔ | 우리 글자는 화면 해상도로 따로 그림(textOut) → 도트 글씨가 안 뭉개짐. 유지 |
| 글자까지 도트면 읽기 어렵다 | (나무위키 요약) | ✔ | 대화·메뉴 글씨는 지금처럼 매끈한 글꼴 유지 |
| 클로드는 큰 일·추론에 강하지만 토큰을 많이 씀, 처음엔 클로드·익숙해지면 코덱스 | aidevelop 1833·2300 | ✘ (도구 이야기) | 게임 UI 와 상관없음 |
| 갤러리 규정: 제작 과정 없이 유료 툴·강의 홍보 금지 | aidevelop 4071 | ✘ | 참고만 |

## 못 찾은 것 (솔직히)
- 이 갤러리에서 **카메라** 를 다룬 글은 검색 요약에 거의 없었다. 카메라 질문은 옆 game_dev(시네머신 시야 돌릴 때 버벅임, 117590)에만 있었고 답은 안 보였다.
- 인벤토리·HUD 배치 같은 자세한 UI 글도 요약에 안 나왔다. 원문을 사람이 직접 보면 더 있을 수 있다.

## 출처 (검색 요약으로 확인한 글)
- 갤러리: https://gall.dcinside.com/mgallery/board/lists/?id=aidevelop
- AI로 게임 개발 일지 -4-: https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=98
- AI를 활용해서 게임 개발을 하면서 느낀점: https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=2062
- ai느낌은 자기가 재밌게 했던 겜이랑 비교하는 것도 좋은방법인듯: https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=2498
- 퇴근 후 AI로 게임 개발하기 10~11일차 (타격감개선, TPS모드): https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=5351
- 플레이 영상: https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=4477
- 클로드 vs 코덱스: https://m.dcinside.com/board/aidevelop/1833 · 코덱스 vs 클로드 차이: https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=2300
- 갤러리 규정 v2026.10.11: https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=4071
- (옆) AI로 만든 UI들: https://m.dcinside.com/board/game_dev/151358
- (옆) 픽셀 비교판: https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=213451
- (옆) 픽셀 그래픽 게임 해상도 설정: https://gall.dcinside.com/mgallery/board/view/?id=godot&no=3756
- (옆) 유니티 시네머신 질문: https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=117590
