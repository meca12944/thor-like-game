# 보스 2페이즈 (전 보스 공용) — 「굶주림의 각성」  E phrygian dominant, 184 BPM.  Blend: Ys speed rock + reference darkness (choir, taiko, half-time choir break).
A = ('e5/2 f5/2 g#5/2 b5/2 c6/4 b5/4 | a5/2 f5/2 c6/2 a5/2 f6/8 | ~e6/8 d6/2 c6/2 b5/2 g#5/2 | a5/4 f5/4 d5/4 f5/4 |'
     'e5/2 a5/2 c6/2 e6/2 a6/8 | f6/6 e6/2 c6/4 a5/4 | b5/2 d6/2 f6/2 g#6/2 b6/8 | ~b6/4 a6/2 g#6/2 f6/2 e6/2 d6/2 c6/2')
B = '~c6/12 b5/4 | a5/12 c6/4 | d6/8 f6/8 | ~e6/16 | e6/4 c6/4 a5/4 e6/4 | f6/4 c6/4 a5/4 f6/4 | g#6/4 f6/4 d6/4 b5/4 | ~e6/16'
CH = 'e4/16 | f4/16 | f4/16 | e4/8 g#4/8 | a4/16 | a4/16 | b4/8 d5/8 | e5/8 g#4/8'
SONG = dict(
    id='battle_boss_phase2', title='굶주림의 각성', en='Awakening of the Hunger', bpm=184, key='E', mode='phrydom', rt60=1.9, damp=5000,
    ch=dict(lead=dict(lp=4600), comp=dict(gain=0.27)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=4, chords='E F E F', drone='e1', choirpad=True, drums='taiko', comp='darkpow', bass='dark', fill='taiko'),
        A=dict(bars=8, chords='E F E Dm Am F G#dim E', lead=A, bass='darkchug', comp='chug16', drums='double', perc=dict(T='x.......x.......')),
        B=dict(bars=8, chords='Am F Dm E Am F G#dim E', lead=B, choir=CH, bass='dark', comp='darkpow', drums='darkhalf', ost='0123012301230123', fill='taiko'),
        A2=dict(bars=8, chords='E F E Dm Am F G#dim E', lead=A, harm=True, bass='darkchug', comp='chug16', drums='double', choirpad=True, perc=dict(T='x...x...x...x...'), fill='tom'),
    ))
