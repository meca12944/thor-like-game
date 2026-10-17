# 정령의 팔찌 II – 데이터 편집 가이드

게임은 `index.html` 한 파일입니다. `<script>` 맨 위의 **「편집 가능한 데이터 블록」**(STORY → SWORDS → WEAPONS → SPIRITS → ITEMS → ENEMIES → 타일표 → TOWNS → MAPS → MUSIC → THEMES → START)만 고치면 됩니다.
`/* ===== 데이터 블록 끝 / 엔진 시작 ===== */` 아래의 엔진 코드는 건드릴 필요가 없습니다.
목록에 새 항목을 추가하면 메뉴, 상점, 상자, HUD에 자동으로 반영됩니다.

> 저장 데이터(localStorage)의 키는 지도·상자 배치로 만든 해시를 씁니다. 지도를 고치면 예전 세이브는 자동으로 무시됩니다(충돌 방지).

---

## 1. STORY – 이야기와 대사

```js
const STORY = {
  title: '게임 제목', subtitle: '부제', hero: '주인공 이름',
  intro: [ ['화자', '대사'], ... ],          // 새 게임 시작 시 오프닝
  events: {
    이벤트키: { lines:[['화자','대사'],...], give:{...}, win:true }
  }
};
```

- `lines`: 대화창에 순서대로 나옵니다. 화자를 `''`로 두면 이름표 없이 표시됩니다.
- `give`(선택): 대사가 끝난 뒤 지급할 보상입니다(아래 **give 형식** 참고).
- `win:true`(선택): 대사가 끝나면 엔딩(THE END) 화면으로 넘어갑니다.
- **이벤트를 부르는 곳**(각 이벤트는 한 번만 실행되며 저장됩니다)
  - 방의 `onEnter: '키'`: 그 방에 처음 들어갈 때
  - 상자의 `event: '키'`: 상자를 열 때
  - NPC의 `event: '키'`: 처음 말을 걸 때(그다음부터는 `lines`가 나옵니다)
  - 방의 `bossEvent: '키'`: 그 방의 보스를 쓰러뜨렸을 때

### give 형식 (상자·상점·이벤트 공통)

| 형식 | 의미 |
|---|---|
| `{sword:'id'}` | 검 획득(바로 장비) |
| `{sub:'id'}` / `{sub:'id', n:10}` | 보조무기 획득. 내구도는 WEAPONS의 `dur`만큼, `n`이 있으면 n만큼 늘어납니다 |
| `{spirit:'id'}` | 정령 각성(게이지 가득) |
| `{item:'potion', n:2}` | 소모품 |
| `{heartup:1}` | 최대 체력 +1칸(하트 1개) |
| `{gold:50}` | 골드 |

---

## 2. SWORDS – 검

```js
{ id:'flame', name:'홍련검', dmg:3, reach:18, speed:11, combo:4,
  color:'#ff9a50', glow:'#ff4400', hilt:'#702010', where:'이끼 동굴 보스방 상자' }
```

| 필드 | 설명 |
|---|---|
| `id` | 고유 영문 ID |
| `name` | 표시 이름 |
| `dmg` | 기본 공격력. 콤보 마지막 타·돌진베기·회전베기는 2배, 점프 내려찍기는 1.5배 |
| `reach` | 칼날 길이(px) = 사거리 |
| `speed` | 한 번 휘두르는 데 걸리는 프레임(작을수록 빠름) |
| `combo` | 연타 최대 횟수. 마지막 타는 강한 찌르기가 됩니다 |
| `color` / `glow` / `hilt` | 칼날색 / 빛 번짐 색(`null`이면 없음) / 손잡이색 |
| `where` | 획득처 메모(메뉴 설명에 표시). **실제 지급은 상자·상점·이벤트의 `give:{sword:'id'}`로 정합니다** |

- 플레이어는 메뉴의 **검** 탭이나 **E 키**로 검을 바꿀 수 있습니다.

## 3. WEAPONS – 보조무기 (내구도)

```js
{ id:'bomb', name:'폭탄', dmg:6, dur:5, type:'bomb', speed:2.6, life:50, radius:30, breaks:true, icon:'bomb', color:'#333' }
```

| 필드 | 설명 |
|---|---|
| `type` | `'straight'`(직선 투척/발사), `'bomb'`(포물선으로 날아가 `life` 프레임 뒤 폭발), `'boomerang'`(날아갔다가 되돌아옴) |
| `dmg`, `speed`, `life` | 위력, 속도, 비행 시간(프레임) |
| `dur` | 획득할 때마다 늘어나는 사용 횟수. 0이 되면 **부서져서** 목록에서 사라집니다 |
| `pierce` | `true`면 적을 관통합니다 |
| `radius`, `breaks` | 폭발 반경, `true`면 금 간 벽(`K`)을 부숩니다 |
| `icon` | `'knife'` `'bolt'` `'bomb'` `'ring'`(그 밖의 값은 원 모양) |
| `color` | 아이콘·탄환 색 |

- 무기 버튼(V)으로 사용합니다. 메뉴의 **보조무기** 탭에서 바꿉니다.

## 4. SPIRITS – 정령

```js
{ id:'water', name:'물의 정령 미르', color:'#4ab0ff', cost:20, drain:.07, dmg:1, abilities:['heal','extinguish','attack'] }
```

- `abilities`: `heal`(곁에 있으면 체력 회복), `extinguish`(불길 `F` 끄기), `ignite`(횃불 `t` 켜기), `switch`(벽 속 `S`나 바닥 `s` 스위치 누르기, 벽 통과), `vine`(구렁 `v`에 덩굴다리 `=` 놓기), `devour`(최대 체력이 5 이하인 적을 삼키고 체력 회복), `attack`(적 공격).
- `cost`: 소환할 때 쓰는 게이지, `drain`: 머무는 동안 프레임마다 줄어드는 게이지.
- 정령은 **`give:{spirit:'id'}`를 받는 시점에 각성**합니다. 각성 순서는 상자·이벤트를 어디에 두느냐로 정합니다.
- 정령 버튼(X)으로 소환하고, 다시 누르면 돌려보냅니다. Q 키나 메뉴로 정령을 바꿉니다.

## 5. ITEMS – 소모품

```js
potion: { name:'회복약', heal:6, color:'#ff5070', desc:'체력 6 회복' }
```

- `heal`(체력 회복량)이나 `spirit`(게이지 회복량)을 지정합니다. 메뉴의 **도구** 탭에서 사용합니다.

## 6. ENEMIES – 적

```js
slime: { name:'슬라임', hp:2, spd:.5, dmg:1, ai:'hop', look:'slime', color:'#5cc84a', size:6, gold:2 }
```

- `ai`: `hop` `fly` `chase` `shoot` `boss_golem` `boss_wyvern` `boss_priest`
- `look`: `slime` `bat` `skel` `knight` `mage` `wisp` `snapper` `golem` `wyvern` `priest`. 이미 있는 모양에 `color`만 바꿔서 새 적을 만들 수 있습니다.
- `boss:true`: 처치하면 저장되고 다시 나오지 않으며, 방의 `bossEvent`가 실행됩니다. `drop:'heartup'`이면 최대 체력 아이템을 떨어뜨립니다.

---

## 7. 지도 문자열 (TOWNS / MAPS 공통)

지도는 **가로 20 × 세로 15** 문자열 배열입니다(한 칸 = 16px). 모자란 부분은 `#`로 채워집니다.

| 문자 | 의미 | 문자 | 의미 |
|---|---|---|---|
| `.` | 바닥 | `,` | 풀밭 |
| `w` | 돌길 | `f` | 꽃 |
| `#` | 벽(3/4 시점 앞면 자동 표시) | `T` | 나무 |
| `H` | 집. 아래가 H/n이면 지붕, 아니면 창문 벽 | `n` | 집 문(장식) |
| `~` | 물(통과 불가) | `_` | 낭떠러지(점프로 건넘, 빠지면 피해) |
| `v` | 깊은 구렁(풀 정령 덩굴 필요) | `=` | 덩굴 다리 |
| `o` | 낮은 바위(점프로 넘음) | `D` | 잠긴 문 |
| `F` | 불길(물 정령) | `t` / `L` | 꺼진 / 켜진 횃불 |
| `s` | 바닥 스위치(밟기) | `S` | 벽 스위치(그림자 정령 전용) |
| `B` | 밀 수 있는 돌(발판에 오르면 `X`로 고정) | `P` | 발판 |
| `K` | 금 간 벽(폭탄으로 파괴) | `A` | 제단 |
| `>` | 출입구(방의 `warps`로 연결) | `' '` | 빈 공간 |

상자는 지도에 쓰지 않고 `chests`의 좌표로 배치합니다(엔진이 자동으로 `C`를 그립니다).

### 방 공통 필드

```js
{ id:'d1a', name:'이끼 동굴', theme:'cave', music:'dungeon',
  map:[ ...15줄... ],
  exits:{ up:'d1b', left:'plain' },                // 화면 가장자리로 이동
  warps:[ {x:10, y:13, to:'plain', tx:9, ty:1} ],  // '>' 칸 → 다른 방 (tx,ty)
  chests:[ {x:17, y:12, give:{spirit:'fire'}, event:'got_fire'} ],
  en:[ ['bat',5,4], ['skel',17,9] ],               // [적id, x, y]
  puzzle:['torches','plates'],                     // 조건을 모두 만족하면 이 방의 D가 열림
  onEnter:'cave_enter', bossEvent:'boss1' }
```

- `exits`로 이어지는 두 방은 **맞닿는 가장자리의 열린 칸 위치가 같아야** 자연스럽게 이동됩니다. 예: 오른쪽 출구가 6~8행이면 상대 방의 왼쪽도 6~8행을 비워 둡니다. 이 연결은 양쪽 방에 모두 적어야 합니다.
- `warps`의 도착 좌표 `tx,ty`는 상대 방 `>` **바로 옆의 바닥 칸**으로 지정합니다.
- `puzzle` 조건: `torches`(꺼진 횃불 없음), `switches`(s/S 모두 눌림), `plates`(빈 발판 없음), `fire`(불길 없음), `enemies`(적 전멸).
- `theme`: THEMES 키(`town` `sand` `field` `canyon` `cave` `tower` `temple`). `cave`와 `temple`은 어둡게 표시됩니다. 새 테마는 THEMES에 색만 추가하면 됩니다.

## 8. TOWNS – 마을

마을은 위의 방 필드에 `npcs`가 더해진 형태입니다.

```js
{ id:'town2', name:'모래항구 마을', theme:'sand', music:'town', map:[...], exits:{left:'canyon'},
  npcs:[
    { x:4, y:5, name:'무기상 카심', look:{body:'#c08030', hair:'#111', skin:'#f0c090'},
      lines:['바다 건너 온 귀한 무기들이오.'],
      shop:[ {give:{sword:'twin'}, price:60}, {give:{sub:'bomb'}, price:25}, {give:{heartup:1}, price:120} ] },
    { x:12, y:5, name:'여관 주인', lines:['어서 오세요'], inn:10 },
    { x:7, y:12, name:'선원', lines:['대사1','대사2'], event:'처음_한번만_실행할_이벤트키' }
  ] }
```

- `lines`: 말을 걸면 순서대로 나오는 대사입니다.
- `shop`: 대사가 끝나면 상점이 열립니다. `give`는 위의 give 형식이고 `price`는 골드입니다. 이미 가진 검은 '보유'로 표시됩니다.
- `inn`: 숙박비입니다. 쉬면 체력과 정령 게이지가 회복되고 **저장**됩니다.
- `look`: 몸·머리·피부 색입니다(생략하면 기본색). 상인은 금띠, 여관 주인은 흰 표식이 자동으로 붙습니다.
- 새 마을을 만들려면 TOWNS에 항목을 추가하고, 기존 방의 `exits`나 `warps`에서 그 마을의 `id`로 연결하면 됩니다.

## 9. MUSIC – 칩튠

```js
field: { bpm:132, lead:'A4 C5 E5 - D5 ...', bass:'A2 A3 ...', drum:true }
```

- 8분음표 단위로 씁니다. `C5`, `D#4`처럼 음이름+옥타브로 적고, `-`는 앞 음을 늘이고, `.`은 쉼표입니다. 멜로디와 베이스는 길이가 달라도 각각 반복됩니다.
- 방의 `music`에는 MUSIC의 키를 적습니다. `title` 곡은 타이틀과 엔딩에서 나옵니다.

## 10. START

`{ room:'town1', x:9, y:8, hp:6, sword:'wood' }`: 시작 방, 좌표, 체력(2 = 하트 1칸), 처음 가진 검입니다.

---

## 조작

| | 키보드 | 터치 |
|---|---|---|
| 이동 | 방향키 / WASD | 왼쪽 화면 가상 조이스틱 |
| 공격·대화·상자 | Z / J / Enter | 공격 |
| 점프 | C / L / Space | 점프 |
| 정령 소환·해제 | X / K | 정령 |
| 보조무기 | V / I | 무기 |
| 메뉴 | Tab / M / Esc | 메뉴(오른쪽 위) |
| 정령 교체 / 검 교체 | Q / E | 메뉴에서 |
| 소리 켜기·끄기 | N | ♪ |

- 연속 베기: 공격 버튼 연타(검의 `combo`만큼, 마지막 타는 강한 찌르기)
- 돌진 베기: 같은 방향을 두 번 빠르게 입력한 뒤 공격
- 회전 베기: 공격 버튼을 꾹 눌렀다가 떼기
- 점프 내려찍기: 공중에서 공격

## 그래픽 (v4) — 무료 공개 라이선스 그림 팩

이제 기본 그래픽은 **Liberated Pixel Cup(LPC)** 계열의 무료 공개 라이선스 그림 팩(OpenGameArt.org)을 씁니다. 작가와 라이선스는 `CREDITS.md`, `assets/LICENSES/` 폴더, 게임 타이틀 화면의 **크레딧** 메뉴에 있습니다.

- 배경은 **방의 글자 지도(`MAPS`/`TOWNS`)를 타일로 그려서** 만듭니다. 그래서 그림과 충돌(벽·물·구덩이)이 항상 맞습니다. 지도를 고치면 그림도 저절로 바뀝니다.
- 잔디·흙길·물·구덩이의 경계는 자동 타일(autotile)로 이어 붙입니다.
- 주인공·NPC·해골·기사·마법사·사제는 LPC 캐릭터 시트(64x64 칸, 위·왼·아래·오른쪽 방향, 걷기 9프레임, 베기 6프레임)를 씁니다.
- 그림을 불러오지 못하면 예전처럼 코드로 그린 그래픽이 자동으로 쓰입니다.
  - 주소 뒤에 `?noassets` 를 붙이면 코드 그래픽으로 볼 수 있습니다.
  - `?assets=폴더/` 를 붙이면 다른 그림 폴더를 시험할 수 있습니다.
- 동굴(cave), 신전(temple), 탑(tower)에는 조명 효과가 있습니다.
- 내부 좌표는 320x240(한 칸 16)이고, 그림을 쓸 때는 4배로 출력합니다. 32px 타일 한 장이 한 칸에 딱 맞습니다.

## 그림 바꾸기 — ASSETS 블록

`index.html` 데이터 블록의 `ASSETS` 에서 지정합니다. `enabled:false` 로 두면 코드 그래픽을 씁니다.

| 항목 | 뜻 |
|---|---|
| `hero:{src, lpc:true, slash}` | 주인공 LPC 시트와 베기 시트(192x192 칸) |
| `npcs:{'이름':'파일.png', _default}` | NPC `name` 으로 찾는 LPC 시트 |
| `enemies:{키:{...}}` | `ENEMIES` 키(보스 포함)마다 스프라이트 |
| `spirits:{id:{...}}` | 정령 스프라이트 |
| `props:{글자:이름}` | 지도 글자 → `props.png` 안 소품 이름. `T` 처럼 배열이면 칸마다 골고루 섞어 씁니다. |
| `propScale:{이름:배율}` | 나무·집 같은 큰 소품의 크기 |
| `tileset:{테마:{...}}` | 테마별 바닥 타일 |
| `credits:[...]` | 게임 안 크레딧 화면에 보이는 줄 |

스프라이트 항목의 형식은 두 가지입니다.

- LPC 시트: `{src:'enemy_skel.png', lpc:true, scale:.95}`
- 일반 격자 시트: `{src:'enemy_slime.png', fw:32, fh:32, cols:3, rows:{u:0,l:1,d:2,r:3}, fps:6, foot:28, scale:.5}`
  - `fw/fh`: 한 프레임 크기(px)
  - `cols`: 가로 프레임 수
  - `rows`: 방향별 줄 번호. 한 방향만 있으면 `flip:true` 로 좌우 반전합니다.
  - `foot`: 프레임 안 발밑의 y 좌표
  - `scale`: 게임 안 배율(.5 이면 32px 그림이 한 칸 크기)
  - 색을 바꾼 강화판(보스, 정령 등)은 `tools/build_art.py` 에서 색을 입혀 따로 PNG로 만듭니다.

`tileset` 테마 항목은 다음과 같습니다.

- `base`: 바닥 타일 이름(배열이면 무작위로 섞음)
- `auto:[[타일, '지도글자들'], ...]`: 해당 글자 칸을 자동 경계 타일로 그립니다(예: `['water','~']`).
- `fill:{글자:타일}`: 그 칸을 한 장짜리 타일로 그립니다.
- `wall`: 벽 앞면 타일, `top`/`rim`: 벽 윗면 색

타일과 소품 이름은 `assets_src/atlas_meta.json` 에 모두 나와 있습니다.

### 그림 다시 만들기 (`tools/build_art.py`, Python + Pillow)

```
python3 tools/build_art.py
```

- 원본 팩을 OpenGameArt.org와 GitHub에서 직접 내려받습니다(`assets_src/packs/` 에 캐시되고, 저장소에는 올리지 않습니다).
- 내려받은 팩을 잘라 `assets/` 의 PNG(타일 아틀라스, 소품 아틀라스, 캐릭터 시트)로 합칩니다.
- `CREDITS.md` 와 `assets/LICENSES/` 를 새로 쓰고, `index.html` 의 `PROP_RECTS`·`TILE_POS` 줄을 갱신합니다.
- 캐릭터 옷차림은 파일 안의 `HERO`, `CHARS` 목록에서 LPC 레이어(몸, 머리, 옷, 무기)를 바꿔 정합니다. 사용한 레이어의 작가는 크레딧에 자동으로 들어갑니다.

### 직접 그린 그림이나 다른 팩으로 바꾸려면

1. `assets/` 에 PNG를 넣습니다.
2. `ASSETS` 의 해당 항목 `src` 와 프레임 정보를 맞춥니다.
3. 라이선스가 공개 게임에서 **재배포를 허용하는지** 꼭 확인합니다.
   - 사용할 수 있는 것: CC0, CC-BY, CC-BY-SA, OGA-BY, GPL
   - 쓰면 안 되는 것: NC(비영리 전용), ND(변경 금지), 재배포 금지 팩
4. `CREDITS.md` 와 `ASSETS.credits` 에 작가, 출처 주소, 라이선스를 적습니다.

> 주의: LPC 그림은 CC-BY-SA 3.0 / GPL 3.0 입니다. 이 그림을 고쳐 만든 그림도 같은 라이선스로 공개해야 하며, 작가 표기를 지우면 안 됩니다.
