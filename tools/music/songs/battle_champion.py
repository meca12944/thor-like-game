# 챔피언 전투 (지역 챔피언 · 마을 강자 결투 공용) — 「강자의 심판」  E minor, 170 BPM.  Fast Ys-style battle rock, unison riff break.
A = ('e5/2 g5/2 b5/2 e6/6 d6/2 b5/2 | c6/2 b5/2 g5/4 e5/4 g5/4 | f#5/2 a5/2 d6/4 c6/2 b5/2 a5/4 | ~b5/12 a5/2 g5/2 |'
     'e6/2 f#6/2 g6/4 f#6/2 e6/2 b5/4 | c6/2 e6/2 g6/4 e6/4 c6/4 | b5/4 d#6/4 f#6/4 a6/4 | ~f#6/8 d#6/2 b5/2 a5/2 f#5/2')
B = ('a5/1 b5 c6 e6 a6/4 g6/2 e6/2 c6/4 | b5/1 c#6 d6 f#6 b6/4 a6/2 f#6/2 d6/4 | e6/6 d6/2 c6/4 g5/4 | ~a5/8 d6/4 f#6/4 |'
     'e6/4 c6/4 a5/4 e6/4 | f#6/4 d6/4 b5/4 f#6/4 | g6/6 f#6/2 e6/4 c6/4 | ~d#6/12 b5/4')
C = ('e5/2 e5/1 e5/1 g5/2 e5/2 a5/2 e5/2 bb5/2 a5/2 | e5/2 e5/1 e5/1 g5/2 e5/2 b5/2 a5/2 g5/2 f#5/2 |'
     'g5/2 g5/1 g5/1 c6/2 g5/2 d6/2 c6/2 b5/2 g5/2 | f#5/2 a5/2 d6/2 f#6/2 ~a6/8')
SONG = dict(
    id='battle_champion', title='강자의 심판', en='Judgement of the Strong', bpm=170, key='E', mode='minor', rt60=1.3,
    intro=['I'], loop=['A', 'B', 'A2', 'C'],
    sections=dict(
        I=dict(bars=2, chords='Em C:8 D:8', comp='chug16', bass='chug', drums='double', fill='tom'),
        A=dict(bars=8, chords='Em C D Em Em C B B', lead=A, bass='drive8o', comp='power8', drums='drive'),
        B=dict(bars=8, chords='Am Bm C D Am Bm C B', lead=B, bass='slap', comp='powersync', drums='drive16', arp='up16', brasspad='stab'),
        A2=dict(bars=8, chords='Em C D Em Em C B B', lead=A, harm=True, bass='gallop', comp='power8', drums='double', pad=True),
        C=dict(bars=4, chords='Em Em C D', lead=C, bass='chug', comp='chug16', drums='drive16', fill='tom'),
    ))
