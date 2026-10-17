# 8지역 설산 뇌전 탑 — 「뇌광의 탑」  B minor, 172 BPM.  Heroic speed rock, sparkling PSG arps, climbing lines.
A = ('f#5/2 b5/2 d6/2 c#6/2 b5/4 f#5/4 | g5/2 b5/2 d6/4 e6/4 d6/4 | c#6/2 e6/2 a6/4 g6/2 f#6/2 e6/4 | ~f#6/12 e6/2 c#6/2 |'
     'd6/4 b5/4 f#6/6 e6/2 | d6/2 e6/2 d6/2 b5/2 g5/8 | e5/4 g5/4 b5/4 e6/4 | ~a#5/8 c#6/4 f#6/4')
B = ('b6/6 a6/2 g6/4 d6/4 | e6/4 f#6/2 e6/2 c#6/8 | d6/2 f#6/2 ~b6/12 | a6/2 g6/2 f#6/4 d6/8 |'
     'g6/6 f#6/2 e6/4 b5/4 | c#6/6 d6/2 e6/4 a6/4 | ~b6/8 g6/4 d6/4 | ~e6/8 c#6/4 a5/4')
SONG = dict(
    id='area08_thunder_tower', title='뇌광의 탑', en='Tower of Lightning', bpm=172, key='B', mode='minor', rt60=1.7,
    ch=dict(arp=dict(gain=0.11, opt=dict(duty=0.25))),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Bm F#', arp='rise', bass='octs', drums='none', perc=dict(c='x...............', b='x...............'), fill='snare'),
        A=dict(bars=8, chords='Bm G A F# Bm G Em F#', lead=A, bass='slap', comp='power8', drums='drive', arp='up16'),
        B=dict(bars=8, chords='G A Bm Bm Em F#m G A', lead=B, bass='drive8o', comp='powersync', drums='drive16', arp='cascade', pad=True),
        A2=dict(bars=8, chords='Bm G A F# Bm G Em F#', lead=A, harm=True, bass='slap2', comp='power8', drums='double', arp='up16', fill='tom'),
    ))
