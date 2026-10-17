# 보스 전투 1페이즈 (지역 보스 1~9 공용) — 「낙인의 먹이」  A harmonic minor, 178 BPM.  Intense Ys-style boss rock with a hint of choir.
A = ('a5/2 e5/2 a5/2 c6/2 b5/2 a5/2 g#5/2 a5/2 | f5/2 a5/2 c6/4 f6/4 e6/4 | d6/2 c6/2 a5/2 f5/2 d5/4 f5/4 | ~e5/8 g#5/4 b5/4 |'
     'c6/2 b5/2 c6/2 e6/2 a6/6 g#6/2 | f6/4 e6/2 c6/2 a5/8 | b5/4 d6/4 f6/4 g#6/4 | ~g#6/8 f6/2 e6/2 d6/2 b5/2')
B = ('f6/6 e6/2 d6/4 a5/4 | g#5/6 a5/2 b5/8 | c6/4 e6/4 a6/6 g6/2 | ~f6/12 e6/4 |'
     'd6/4 f6/4 a6/4 f6/4 | e6/4 g#6/4 b6/8 | a6/4 f6/4 c6/4 a5/4 | ~b5/8 g#5/4 e5/4')
SONG = dict(
    id='battle_boss', title='낙인의 먹이', en='Prey of the Brand', bpm=178, key='A', mode='harmonic', rt60=1.5,
    ch=dict(choirpad=dict(gain=0.16)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Am E', comp='chug16', choirpad=True, bass='chug', drums='double', fill='tom'),
        A=dict(bars=8, chords='Am F Dm E Am F G#dim E', lead=A, bass='gallop', comp='chug16', drums='drive16', brasspad='stab2'),
        B=dict(bars=8, chords='Dm E Am F Dm E F E', lead=B, bass='drive8o', comp='powersync', drums='double', choirpad=True, arp='cascade'),
        A2=dict(bars=8, chords='Am F Dm E Am F G#dim E', lead=A, harm=True, bass='slap2', comp='chug16', drums='drive16', pad=True, fill='tom'),
    ))
