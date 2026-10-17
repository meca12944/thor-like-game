# tools/music — BGM 신스 · 작곡 데이터

numpy/scipy only FM · chip synth (YM2612/PSG 시대 소리 흉내) + 작은 악보 형식. 모든 곡은 오리지널입니다.

```
pip install numpy scipy soundfile pyloudnorm      # + ffmpeg (libvorbis)
python3 tools/music/render.py [id ...] [--wav] [--out=DIR]   # songs/*.py → audio/bgm/<id>.ogg + bgm.json
python3 tools/music/check.py audio/bgm [id ...]               # 디코드해서 루프 이음새 · 클리핑 · LUFS 확인
python3 tools/music/gen_doc.py                                # BGM.md 재생성
```

| 파일 | 내용 |
|---|---|
| `synth.py` | 악기: `guitar`(오버드라이브 3-op FM 리드) `lead_soft` `flute` `psg` `pluck` `epiano` `bell` `toll` `brass` `strings` `stacc_str` `choir` `organ` `slap` `pickbass` `synbass` `softbass` `drone` `timpani`, 파워코드 `power`, 드럼(k s h H c r t1-3 T p b sh cb an), 리버브 · 핑퐁 딜레이 |
| `score.py` | 악보 파서(선율 · 화음 · 패턴) → 이벤트, 패턴 라이브러리(BASS / COMP / ARP / DRUMS / FILLS), 기본 채널 믹스(DEFAULT_CH) |
| `render.py` | 채널 렌더 → 믹스 → 루프 꼬리 원형 접기 → -14 LUFS 정규화 + 리미터(-1.2 dBFS) → ffmpeg Vorbis. 루프 정보는 bgm.json + Vorbis 주석 `LOOPSTART`/`LOOPLENGTH`(샘플) |
| `songs/<id>.py` | 곡 하나 = `SONG` dict |

## SONG 형식

```python
SONG = dict(id='area01_forest', title='초록 바람의 검', bpm=160, key='A', mode='minor',   # mode: minor major harmonic dorian phrygian phrydom mixolydian lydian
            bar=16,                 # 한 마디 16분음표 칸 수 (6/8·3/4 는 12)
            rt60=1.4, damp=6500,    # 리버브 길이 · 어두움, delay=0.75 (박자 단위), lufs=-14
            ch=dict(lead=dict(inst='flute', gain=0.3, lp=7000, opt=dict(vib=0.3))),   # 채널 덮어쓰기
            intro=['I'], loop=['A', 'B', 'A2'],      # 인트로는 1회, loop 는 끝없이 반복 (loop=[] 이면 1회 재생 곡)
            sections=dict(A=dict(bars=8, chords='Am F G Em Am F G E', lead=MEL, harm=True,
                                 bass='slap', comp='power8', arp='up16', pad=True, drums='drive', fill='tom')))
```

- **선율** (`lead` `counter` `choir` `bell` `toll` …): `음이름+옥타브/길이` (길이는 16분음표 단위, 앞 값 유지). `r` 쉼표, `-` 붙임줄, `|` 는 보기용. 앞 기호: `~` 2음 아래에서 벤딩, `` ` `` 반음 벤딩, `!` 강세, `*` 스타카토, `^` 앞 음에서 글라이드. 섹션 길이와 다르면 렌더가 오류를 냅니다.
- **화음**: 공백으로 마디 구분, `Am:8` 처럼 길이 지정, `C/E` 베이스 지정, `N` 무화음. 종류: `m 7 m7 maj7 dim dim7 aug sus4 sus2 5 m7b5 add9 madd9 7sus4 m9 9 mmaj7 6 m6`.
- **하모니**: `harm=True` (채널 lead2 가 리드를 음계 3도 아래로), `harm=-5` (6도 아래), `harm=-7` (옥타브 아래) 등.
- **패턴**: 이름(`score.py` 라이브러리) 또는 16칸 문자열. 베이스 `R`근음 `O`옥타브 `5` `3` `7` `x`고스트 `A`반음 접근 `-`늘임 `.`쉼. 반주 `x` 울림 `m` 뮤트. 아르페지오 숫자 = 화음 구성음 순번. 드럼은 dict(k='x...', s='....X...', h='x.x.')`, `X` 강 `x` 보통 `o` 약.
- `drone='e1'` 섹션 내내 페달, `drone=True` 화음 근음, `perc=dict(T='x...')` 추가 타악, `vol=dict(lead=0.5)`, `crash=False`, `fill=None|'fill'|'tom'|'snare'|'roll'|'taiko'`.
