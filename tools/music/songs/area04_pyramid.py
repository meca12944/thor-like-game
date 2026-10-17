# 4지역 피라미드 — 「황금가면의 회랑」  E phrygian, 120 BPM half-time.  Dark (reference style): drone, choir, taiko, tolling bell.
A = ('e5/8 f5/4 g5/4 | ~a5/12 g5/2 f5/2 | g5/4 f5/4 e5/4 d5/4 | ~e5/16 |'
     'b5/8 c6/4 b5/4 | a5/6 g5/2 f5/4 a5/4 | ~b5/8 d6/4 b5/4 | ~c6/12 b5/4')
B = ('e6/4 b5/4 g5/4 b5/4 | a5/4 f5/4 d5/4 f5/4 | g5/4 e5/4 c5/4 e5/4 | f5/4 a5/4 g5/4 b5/4 |'
     '~c6/8 e6/4 a6/4 | ~a6/8 f6/4 c6/4 | ~b5/8 g5/4 e5/4 | f5/4 a5/4 c6/2 b5/2 a5/2 f5/2')
CH = 'e4/16 | f4/16 | g4/16 | a4/8 b4/8 | c5/16 | c5/16 | b4/16 | c5/8 b4/8'
SONG = dict(
    id='area04_pyramid', title='황금가면의 회랑', en='Corridor of the Golden Mask', bpm=120, key='E', mode='phrygian', rt60=2.8, damp=4500,
    ch=dict(lead=dict(lp=3400, rev=0.35, dly=0.2), choir=dict(gain=0.42), comp=dict(gain=0.2, lp=2600)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=4, chords='Em F Em F', drone='e2', choirpad=True, toll='e3/16 | r/16 | e3/16 | f3/16', drums='none', crash=False, fill=None,
               perc=dict(T='x.........x.....')),
        A=dict(bars=8, chords='Em F Em Dm Em F G F', lead=A, drone='e1', bass='dark', comp='darkpow', ost='0.00.00.0.00.0.0', drums='darkhalf', choirpad=True),
        B=dict(bars=8, chords='Em Dm C F:8 G:8 Am F Em F', lead=B, choir=CH, bass='darkchug', comp='chug16', drums='darkdrive', ost='0101010101010101', fill='taiko'),
        A2=dict(bars=8, chords='Em F Em Dm Em F G F', lead=A, harm=-5, drone='e1', bass='dark', comp='darkpow', ost='0.00.00.0.00.0.0', drums='darkhalf', toll='e3/16 | r/16 | r/16 | r/16 | e3/16 | r/16 | r/16 | r/16', fill='taiko'),
    ))
