# PixelLab 배경 (사장님 11-12 「전부 게임에 올려」)

PixelLab(11-11~12)으로 뽑은 1~8장 배경 중 쓸 만한 것을 모았다. 섞는 방식은 펠트와 같다. 바닥·건물·소품은 PixelLab 도트로, 하늘·먼 성은 손그림으로 둔다.

- `chN/index.json`: 그림 하나마다 id, type, zone(`docs_maps/chN/chN_map.json` 구역), file, size, verdict, prompt 요약을 적었다.
- 고른 방법
  - OK만 넣었다.
  - 다시 찍은 것이 OK면 원래 것 대신 그것을 넣었다.
  - 그 자리에 OK가 하나도 없을 때만 보통을 넣었다. 이런 것은 `verdict: soso`, `flag: soso_no_ok_for_slot`이다.
  - 버림은 넣지 않았다.
- 폴더: `tiles/`(바닥 타일셋, wang 모서리 `tiles.json`), `props/`, `buildings/`, `rooms/`(방 그림과 48px 키트), `decals/`(바닥 장식 16장), `kits/`(건물 키트 조각)
- 게임에 넣은 곳: `test128/maps/px_*.json`. `tools/pixellab/build_px_zones.py`가 만든다. 입구는 `test128/?go=px_hub`이다.
  - 구역 하나가 맵 하나다. 동쪽 출구로 다음 구역에 가고, 장 끝에서는 다음 장으로 넘어간다.
  - 방은 `px_chN_int_*`이다.
  - `px_zones.json`에 구역 목록이 있다.
- 다시 만들기: `python3 tools/pixellab/import_assets.py` (박스 원본 폴더) 후 `python3 tools/pixellab/build_px_zones.py`
- 아직 게임에 안 붙인 것
  - 건물 키트(`kits/`)와 16px 벽·절벽 타일셋(transition)은 index에만 있다.
  - 정식 구역 지도(`docs_maps`)를 실제 크기로 만들 때 쓴다.
