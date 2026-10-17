# 폐허가 된 마을 (마왕의 길, 모든 마을 공용) — 「잿더미의 종」  E phrygian, 70 BPM.  Reference-style dark: sub drone, choir, funeral bell, sparse taiko.
A = ('b4/8 e5/4 f5/4 | ~g5/12 f5/4 | e5/6 d5/2 b4/8 | d5/8 c5/4 a4/4 |'
     'b4/4 e5/4 g5/4 b5/4 | ~c6/8 b5/4 g5/4 | a5/6 g5/2 f5/8 | ~e5/16')
B = ('e5/4 a5/4 c6/6 b5/2 | a5/8 f5/4 a5/4 | ~b5/8 d6/4 g5/4 | b5/6 a5/2 g5/8 |'
     'c6/4 e6/4 a6/8 | ~f6/8 e6/4 c6/4 | d6/6 c6/2 a5/8 | ~b5/16')
SONG = dict(
    id='town_ruin', title='잿더미의 종', en='Bell over the Ashes', bpm=70, key='E', mode='phrygian', rt60=3.4, damp=3800, lufs=-15,
    ch=dict(lead=dict(inst='lead_soft', gain=0.26, lp=3000, hp=150, rev=0.45, dly=0.2), comp=dict(gain=0.14, lp=2000)),
    intro=['I'], loop=['A', 'B'],
    sections=dict(
        I=dict(bars=2, chords='Em F', drone='e1', toll='e3/16 | r/16', drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='Em F Em Dm Em C F Em', lead=A, drone='e1', choirpad=True, toll='e3/16 | r/16 | r/16 | r/16 | e3/16 | r/16 | r/16 | r/16',
               drums=dict(T='x...............'), crash=False, fill=None),
        B=dict(bars=8, chords='Am F G Em Am F Dm Em', lead=B, choirpad=True, bass='half2', comp='darkpow', ost='0.0.0.0.0.0.0.0.',
               drums='darkhalf', crash=False, fill='taiko'),
    ))
