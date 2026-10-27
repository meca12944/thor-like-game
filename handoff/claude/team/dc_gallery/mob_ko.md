# 디시 갤러리 팁 — 몹·보스·AI 행동·타격감 (4번방, 2026-10-27)
> 사장님 「DC AI개발갤러리 정보 싹 긁어와」 → 팀장. 갤러리: AI 게임 개발 갤(`aidevelop`) + 인디 게임 개발 갤(`game_dev`).
> **원문은 열지 않음**(디시는 봇에게 빈 페이지 · 봇 막기 우회 금지) → **검색엔진 요약만** 보고 정리. 그래서 글 속 숫자·그림은 직접 확인 못 함, 링크로 사람이 확인.
> 판정: ○ 바로 씀 · △ 일부만 / 이미 비슷한 것 있음 · × 안 맞음

## 1. 타격감 (때릴 때 손맛)
| 팁 | 글 | 우리 게임에 쓸 수 있나 | 왜 |
|---|---|---|---|
| 맞는 쪽을 크게, 때리는 쪽은 작게 흔든다. 판정 상자는 흔들지 않는다 (사쿠라이 강의 요약) | [game_dev 186591](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=186591) | △ | 우리도 맞은 몹 눌림·기울기(world.js `drawFeltHi`)와 히트스톱이 있음. 주인공 쪽 흔들림은 0이라 「작게 흔들기」 1~2px 더해 볼 만함 |
| 히트스톱 길이 = 공격력 × 계수, 땅·공중에서 흔드는 방향 다르게 | 같은 글 | ○ | 지금 히트스톱은 콤보 단계로만 달라짐 → 「피해 크기」에 맞추면 큰 칼질이 더 묵직 |
| 몹이 흔들리는 세기 = 피해 ÷ 몹 최대 체력 (보스는 살짝, 큰 공격엔 크게) | [game_dev 139106](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=139106) (쉐잎오브드림 타격감) | ○ | 우리 `hitK`는 마무리타만 1.5배. 체력 비율로 바꾸면 아라크네(1500)는 덜, 솜뭉치(8)는 크게 → 「보스는 무겁다」가 저절로 |
| 맞는 순간 멈춤·느려짐 + 적 떨림 + 화면 밝기·흔들림 (Hit Stop / Screen Kill Effect) | 같은 글 | △ | 거의 다 있음. **처치 순간**만 화면 번쩍·짧은 멈춤을 더 크게 하는 건 아직 약함 |
| 슬로모션은 「렉」으로 오해받고 패링 박자를 망칠 수 있다 → 끌 수 있게 | 같은 글 | ○ | 우리 저스트 회피 느려짐(`S.slowmo .3`)도 같은 위험. 옵션에 「느려짐 끄기」 추천 |

## 2. 몹·보스 패턴
| 팁 | 글 | 우리 게임에 쓸 수 있나 | 왜 |
|---|---|---|---|
| 「평타 → 평타 → 강타」 반복은 지루 → 강타에 쿨타임·횟수 제한 | [game_dev 139106](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=139106) | △ | 우리는 이미 「같은 기술 3번 연속 금지」 + 쿨타임(교본 1-5, 1-10). 맞는 방향 확인 |
| 보스가 기다리는 동안 붉은 테두리 → 그때 때리면 반격 / 2페이즈엔 같이 공격해 「위험 감수할지」 고르게 | [game_dev 51789](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=51789) (보스 2페이즈) | ○ | 아라크네 「막는 자세」가 없음. **빈틈이 아닐 때 베면 반격**(붉은 테두리 0.6초 경고)을 넣으면 「빈틈에 베기」가 더 분명해짐 — 게임 핵심 2번 |
| 1페이즈 = 기본기 가르치기 → 다음 = 이동 요구 → 마지막 = 간격 줄여 시험 | [wikidocs 보스 설계](https://wikidocs.net/371309) (갤 밖 자료, 같이 찾힘) | ○ | 아라크네도 1페이즈 찍기·덮치기 → 2페이즈 실 감옥·붉은 실(이동). 3번째 단계(체력 20% 「간격 줄이기」)는 아직 없음 |
| 강한 공격·약한 공격, 공격·쉬는 시간을 번갈아 | [wikidocs 보스 타임라인](https://wikidocs.net/362126) | △ | 우리 빈틈 기준(교본 1-1·1-8)과 같은 말 |
| 주 패턴 1개 + 보조 압박 1개, 동시에 둘 다 세게 하지 않는다 | [wikidocs 템플릿](https://wikidocs.net/362176) | ○ | 아라크네 2페이즈에 솜뭉치 + 붉은 실 + 실 감옥이 겹치는 순간이 있음 → 실 감옥 중엔 솜뭉치 안 부르기 검토 |

## 3. AI 행동
| 팁 | 글 | 우리 게임에 쓸 수 있나 | 왜 |
|---|---|---|---|
| 추적·탐색 두 상태로 시작했다가 예외(점프·놓침)가 늘면 상태 기계만으로 힘듦 → 행동 트리 | [game_dev 106233](https://m.dcinside.com/board/game_dev/106233) | × (지금은) | 우리 몹은 역할 1개 + 기술 2~3개라 `felt()` 상태 기계로 충분. 보스가 더 복잡해지면 그때 |
| 어그로 = 가까이서 눈에 띄는 행동일수록 오름, 맞으면 줄어듦, 연계 중 대상이 바뀔 수 있음 (몬헌) | [monsterhunter 6151074](https://gall.dcinside.com/board/view/?id=monsterhunter&no=6151074) | △ | 우리는 주인공 1명 + 리네트(동료). 리네트가 몹을 너무 빨리 잡는 문제(교본 0부 10)에 「리네트 쪽 어그로」 값이 해결책이 될 수 있음 |
| 시야에서 벗어나야 추적이 풀림 (발견 → 추적 → 놓침) | [repo 93](https://gall.dcinside.com/mgallery/board/view/?id=repo&no=93) | △ | 우리 `W.los`(벽 뒤 안 보임)와 같음. 「놓친 뒤 마지막 본 자리까지 가 보기」는 아직 없음 — 던전에서 숨기 재미 |
| 몹 체력이 너무 높고 주인공이 약하면 「불합리」 (뱀서류 리뷰) | [aidevelop 1604](https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=1604) | ○ | 일반 몹 3~4번 베기(교본 1-8) 지키기. 봇 처치 시간으로 계속 확인 |

## 4. 회피·패링
| 팁 | 글 | 우리 게임에 쓸 수 있나 | 왜 |
|---|---|---|---|
| 알맞은 순간에 구르면 패링 판정 (루비나이트) | [indiegame 397937](https://gall.dcinside.com/mgallery/board/view/?id=indiegame&no=397937) | ○ (이미 있음) | 우리 저스트 회피와 같음 → 맞음 확인 |
| 엘든링 구르기 무적 약 24~26프레임(커뮤니티 측정) | [fromsoftware 3098952](https://m.dcinside.com/board/fromsoftware/3098952) | △ | 우리 회피대시 무적 13틱(0.22초) — 엘든링(0.4초)보다 짧음. 엘든링식이 기본이면 15~18틱 시험해 볼 만함(주인공 몫, 모션·2번방과 상의) |
| 패링 실패 위험·후딜이 너무 크면 지루 | [indiegame 215181](https://gall.dcinside.com/mgallery/board/view/?id=indiegame&no=215181) | △ | 저스트 회피 실패 = 그냥 맞음(+5 게이지)이라 지금은 괜찮음 |

## 5. AI로 몹 그림 만들기 (참고)
| 팁 | 글 | 우리 게임에 쓸 수 있나 | 왜 |
|---|---|---|---|
| 원화 → 도트화 → 동작 영상(그록 등) → 프레임 골라 배경 빼기 | [game_dev 204012](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=204012), [game_dev 177413](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=177413) | △ | 우리는 그록 핵심 자세 + PixelLab 걷기 8장(18 크레딧). 「영상에서 프레임 뽑기」는 크레딧 0 대안 — 사람이 아닌 몹(거미·솜뭉치)에 시험해 볼 만함 |
| PixelLab: 사람형은 잘 됨, 괴물형은 손이 더 감 | 같은 글들, [aidevelop 2549](https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=2549) | ○ (이미 겪음) | 우리도 구운 하늘색 얼룩·칼 빛줄기를 지움(교본 1-10, 2부) |
| 배경을 흰색·검은색으로 두면 외곽선과 구분이 어려움 | [rayquaza 204656](https://gall.dcinside.com/mgallery/board/view/?id=rayquaza&no=204656) | ○ | 투명 배경(no_background) 그대로 쓰기 |
| 「캐릭터 몬스터 만드는 게 진짜 난관」 (본문 확인 못 함) | aidevelop 목록 | — | 모두 같은 고민 → 우리 교본 0부 순서가 맞는 방향 |

## 바로 해 볼 것 TOP 3 (크레딧 0, 모두 코드)
1. **몹 흔들림 = 피해 ÷ 최대 체력** — 보스는 덜, 작은 몹은 크게 흔들려 「무게」가 저절로 생김. `hitMob`의 `hitK` 한 줄. 전·후 영상으로 비교.
2. **아라크네 「빈틈 아닐 때 베면 반격」** — 붉은 테두리 0.6초 경고 → 짧은 반격(저스트 회피 가능). 「빈틈에 달려가 베기」가 더 분명해짐(게임 핵심 2). mob_check·봇 처치 시간 전·후.
3. **처치 순간 손맛 키우기** — 마지막 한 방에만 히트스톱을 2배 + 작은 화면 번쩍. 저스트 회피 느려짐은 옵션에서 끌 수 있게(「렉」 오해 방지) — UI·2번방과 상의.

## 출처 (검색엔진 요약으로만 확인)
- AI 게임 개발 갤: [목록](https://gall.dcinside.com/mgallery/board/lists/?id=aidevelop), [1604](https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=1604), [2549](https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=2549), [858](https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=858), [2300](https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=2300), [428](https://gall.dcinside.com/mgallery/board/view/?id=aidevelop&no=428)
- 인디 게임 개발 갤: [186591](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=186591), [187136](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=187136), [139106](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=139106), [51789](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=51789), [106233](https://m.dcinside.com/board/game_dev/106233), [204012](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=204012), [177413](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=177413), [212068](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=212068)
- 다른 갤(같이 찾힘): [monsterhunter 6151074](https://gall.dcinside.com/board/view/?id=monsterhunter&no=6151074), [repo 93](https://gall.dcinside.com/mgallery/board/view/?id=repo&no=93), [indiegame 397937](https://gall.dcinside.com/mgallery/board/view/?id=indiegame&no=397937), [indiegame 215181](https://gall.dcinside.com/mgallery/board/view/?id=indiegame&no=215181), [fromsoftware 3098952](https://m.dcinside.com/board/fromsoftware/3098952), [rayquaza 204656](https://gall.dcinside.com/mgallery/board/view/?id=rayquaza&no=204656)
- 갤 밖: [wikidocs 362126](https://wikidocs.net/362126), [wikidocs 371309](https://wikidocs.net/371309), [wikidocs 362176](https://wikidocs.net/362176)
