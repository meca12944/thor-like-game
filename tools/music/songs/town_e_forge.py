# E 화산 기슭 대장장이 마을 — 「잿빛 망치 소리」  E minor, 100 BPM.  Mid-tempo heavy groove, anvils on 2 and 4, hammer-rhythm lead.
A = ('e5/3 e5/3 g5/2 b5/4 a5/4 | f#5/3 f#5/3 a5/2 d6/8 | e6/3 d6/3 c6/2 g5/4 e5/4 | ~f#5/12 d#5/4 |'
     'b5/3 b5/3 d6/2 e6/4 d6/4 | c6/3 b5/3 a5/2 f#5/8 | g5/4 c6/4 e6/4 g6/4 | ~f#6/8 d#6/4 b5/4')
B = ('c6/6 b5/2 a5/4 e5/4 | g5/6 f#5/2 e5/8 | e5/4 g5/4 c6/4 e6/4 | ~d6/8 a5/4 f#5/4 |'
     'a5/4 c6/4 e6/6 d6/2 | b5/6 g5/2 e5/8 | f#5/4 a5/4 b5/4 d#6/4 | ~f#6/16')
SONG = dict(
    id='town_e_forge', title='잿빛 망치 소리', en='Ash-grey Hammerfall', bpm=100, key='E', mode='minor', rt60=1.6,
    ch=dict(lead=dict(opt=dict(drive=2.4), gain=0.27, lp=4800), bass=dict(inst='pickbass', gain=0.44), comp=dict(gain=0.2)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Em D', drums='rock', perc=dict(an='....x.......x...'), bass='sync', comp='push', fill=None),
        A=dict(bars=8, chords='Em D C B Em D C B', lead=A, bass='sync', comp='push', drums='rock', perc=dict(an='....x.......x...'), brasspad='stab'),
        B=dict(bars=8, chords='Am Em C D Am Em B B', lead=B, bass='drive8', comp='powersync', drums='rock', pad=True, perc=dict(an='....x.......x...')),
        A2=dict(bars=8, chords='Em D C B Em D C B', lead=A, harm=True, bass='sync', comp='push', drums='rock', perc=dict(an='....x..x....x...'), brasspad='stab2'),
    ))
