# 6지역 해안 절벽 — 「유령 선장의 절벽」  G minor, 168 BPM.  Galloping pirate-rock, brass stabs, cannon-like toms.
A = ('d5/2 g5/2 a5/2 bb5/6 a5/2 g5/2 | f5/2 a5/2 c6/4 a5/4 f5/4 | g5/2 bb5/2 eb6/6 d6/2 c6/4 | ~d6/8 a5/4 f#5/4 |'
     'g5/2 c6/2 d6/2 eb6/6 d6/2 c6/2 | bb5/2 a5/2 g5/4 d5/4 g5/4 | a5/4 c#6/4 e6/4 g6/4 | ~f#6/8 d6/4 a5/4')
B = ('g6/6 f6/2 eb6/4 bb5/4 | a5/6 bb5/2 c6/8 | d6/4 f6/4 a6/6 g6/2 | ~g6/12 d6/4 |'
     'eb6/4 c6/4 g5/4 c6/4 | ~f6/8 c6/4 a5/4 | bb5/4 d6/4 f6/4 bb6/4 | ~a6/8 f#6/4 d6/4')
SONG = dict(
    id='area06_cliff', title='유령 선장의 절벽', en='Cliffs of the Ghost Captain', bpm=168, key='G', mode='minor', rt60=1.6,
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Gm D', brasspad='stab2', comp='gallop', bass='gallop', drums='gallop', fill='tom'),
        A=dict(bars=8, chords='Gm F Eb D Cm Gm A D', lead=A, bass='gallop', comp='gallop', drums='gallop', brasspad='stab'),
        B=dict(bars=8, chords='Eb F Dm Gm Cm F Bb D', lead=B, bass='drive8o', comp='power8', drums='drive', pad=True, arp='up16'),
        A2=dict(bars=8, chords='Gm F Eb D Cm Gm A D', lead=A, harm=True, bass='slap2', comp='gallop', drums='gallop', brasspad='stab2', fill='tom'),
    ))
