# 1지역 시작의 숲 — 「초록 바람의 검」  A minor, 160 BPM, FM rock (Ys-era style, original melody)
A = ('~e5/6 a5/2 b5/4 c6/4 | b5/2 a5/2 f5/4 a5/8 | g5/6 d5/2 g5/4 b5/4 | ~b5/12 a5/2 g5/2 |'
     '~e5/6 a5/2 b5/4 c6/4 | d6/4 c6/2 b5/2 a5/4 c6/4 | d6/4 b5/2 d6/2 g6/4 f6/4 | ~e6/8 b5/2 g#5/2 e5/4')
B = ('a5/2 c6/2 f6/4 e6/2 c6/2 a5/4 | b5/2 d6/2 g6/4 f6/2 d6/2 b5/4 | g5/2 b5/2 e6/6 d6/2 b5/4 | c6/4 a5/4 e5/4 a5/4 |'
     'f5/4 a5/4 d6/6 c6/2 | b5/4 g5/4 d6/4 b5/4 | ~c6/6 b5/2 c6/4 e6/4 | ~e6/16')
C = ('d5/1 f5 a5 d6 a5 f5 d5 f5 a5 d6 f6 d6 a5 f5 d5 a4 | e5/1 g#5 b5 e6 b5 g#5 e5 g#5 b5 e6 g#6 e6 b5 g#5 e5 b4 |'
     '~a5/8 c6/4 a5/4 | ~g#5/8 b5/4 e6/4')
SONG = dict(
    id='area01_forest', title='초록 바람의 검', en='Blade of the Green Wind', bpm=160, key='A', mode='minor',
    rt60=1.4, intro=['I'], loop=['A', 'B', 'A2', 'C'],
    sections=dict(
        I=dict(bars=2, chords='Am | E', comp='power1', drums='none', fill='snare', bass='root1',
               perc=dict(s='............xxxx')),
        A=dict(bars=8, chords='Am F G Em Am F G E', lead=A, bass='slap', comp='power8', drums='drive', arp='up16'),
        B=dict(bars=8, chords='F G Em Am Dm G C E', lead=B, bass='drive8o', comp='powersync', drums='drive16', pad=True),
        A2=dict(bars=8, chords='Am F G Em Am F G E', lead=A, harm=True, bass='slap2', comp='power8', drums='drive', arp='up16'),
        C=dict(bars=4, chords='Dm E F E', lead=C, bass='gallop', comp='gallop', drums='gallop', fill='tom'),
    ))
