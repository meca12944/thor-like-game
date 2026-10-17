# D 성벽 왕도 — 「푸른 지붕의 왕도」  C major, 120 BPM.  Regal march: FM brass lead, snare march, strings, flute counter.
A = ('g4/4 c5/2 e5/2 g5/6 e5/2 | d5/4 g5/2 b5/2 d6/8 | c6/6 b5/2 a5/4 e5/4 | ~g5/12 g5/2 a5/2 |'
     'a5/4 c6/4 f6/6 e6/2 | e6/4 d6/2 c6/2 g5/8 | f5/4 a5/4 d6/4 c6/4 | ~b5/8 d6/4 g5/4')
B = ('e6/6 d6/2 c6/4 a5/4 | b5/6 a5/2 g5/8 | a5/4 c6/4 f6/4 a6/4 | ~g6/8 e6/4 c6/4 |'
     'd6/6 e6/2 f6/4 a5/4 | g5/6 a5/2 b5/4 e6/4 | ~f6/8 e6/4 d6/4 | ~d6/8 b5/4 g5/4')
SONG = dict(
    id='town_d_capital', title='푸른 지붕의 왕도', en='Royal City of Blue Roofs', bpm=120, key='C', mode='major', rt60=2.0,
    ch=dict(lead=dict(inst='brass', gain=0.36, lp=5000, hp=150, rev=0.3), lead2=dict(inst='flute', gain=0.14, shift=2),
            bass=dict(inst='pickbass', gain=0.40), brasspad=dict(gain=0.12)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='C G', brasspad='stab', bass='march', drums='march', fill='roll'),
        A=dict(bars=8, chords='C G/B Am Em/G F C/E Dm G', lead=A, bass='march', drums='march', pad=True, fill=None),
        B=dict(bars=8, chords='Am Em F C Dm Em F G', lead=B, bass='walk', drums='march', brasspad='push', arp='up8', fill='roll'),
        A2=dict(bars=8, chords='C G/B Am Em/G F C/E Dm G', lead=A, harm=True, bass='march', drums='march', pad=True, perc=dict(c='x.......'), fill='roll'),
    ))
