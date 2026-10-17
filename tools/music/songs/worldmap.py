# 월드맵 — 「바람이 가르는 대지」  E minor, 150 BPM.  Adventurous field theme, open fifths, lifting B section.
A = ('b4/4 e5/2 f#5/2 g5/4 b5/4 | ~c6/8 b5/2 a5/2 g5/4 | a5/4 f#5/2 d5/2 a5/6 g5/2 | ~g5/8 d5/4 g5/2 a5/2 |'
     'b5/4 e6/2 d6/2 b5/4 g5/4 | c6/2 b5/2 a5/4 e5/4 a5/4 | f#5/4 a5/4 d6/4 c6/2 a5/2 | ~b5/8 d#6/4 f#6/4')
B = ('g6/6 e6/2 c6/4 e6/4 | f#6/6 d6/2 a5/4 d6/4 | ~d6/8 b5/4 f#5/4 | g5/6 a5/2 b5/8 |'
     'c6/6 b5/2 a5/4 e6/4 | d6/6 c6/2 a5/4 f#5/4 | g5/4 b5/4 d6/4 g6/4 | ~f#6/12 d#6/4')
SONG = dict(
    id='worldmap', title='바람이 가르는 대지', en='Across the Wind-cut Land', bpm=150, key='E', mode='minor', rt60=1.6,
    intro=['I'], loop=['A', 'B', 'A2', 'B2'],
    sections=dict(
        I=dict(bars=2, chords='Em D', comp='powersync', bass='sync', drums='rock', fill='snare'),
        A=dict(bars=8, chords='Em C D G Em C D B', lead=A, bass='drive8o', comp='power8', drums='drive', arp='up8'),
        B=dict(bars=8, chords='C D Bm Em Am D G B7', lead=B, bass='sync2', comp='powersync', drums='drive16', pad=True),
        A2=dict(bars=8, chords='Em C D G Em C D B', lead=A, harm=True, bass='slap', comp='power8', drums='drive', arp='up16'),
        B2=dict(bars=8, chords='C D Bm Em Am D G B7', lead=B, harm=True, bass='drive8o', comp='powersync', drums='drive16', pad=True, fill='tom'),
    ))
