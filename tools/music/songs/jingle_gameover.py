# 게임 오버 (1회) — 「꺼진 등불」  A minor, 72 BPM.  Borrowed F minor, funeral bell.
SONG = dict(
    id='jingle_gameover', title='꺼진 등불', en='The Lamp Goes Out', bpm=72, key='A', mode='minor', rt60=3.0, lufs=-15,
    ch=dict(lead=dict(inst='lead_soft', gain=0.3, lp=4000, rev=0.45)),
    intro=['A'], loop=[],
    sections=dict(A=dict(bars=3, chords='Am Fm Am', lead='e5/6 d5/2 c5/4 b4/4 | ab4/8 c5/4 f5/4 | ~e5/16', pad=True, toll='r/16 | r/16 | a2/16', drums='none', crash=False, fill=None)),
)
