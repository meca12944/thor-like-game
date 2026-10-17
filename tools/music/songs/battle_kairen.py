# 최종전 검은 왕 카이렌 (그림자 마룡) — 「검은 왕 카이렌」  E phrygian / harmonic, 129 BPM.  Closest to the user's reference:
# half-time weight, sub drone, choir + organ, tolling bell, taiko; then a Ys-style lead and a double-kick climax.
CHA = 'b4/16 | c5/16 | b4/16 | a4/8 c5/8 | e5/16 | d5/16 | c5/16 | b4/16'
B = ('e5/2 a5/2 b5/2 c6/6 b5/2 a5/2 | b5/2 a5/2 g5/2 e5/2 b5/8 | a5/2 c6/2 f6/4 e6/2 c6/2 a5/4 | ~g#5/8 b5/4 e6/4 |'
     'c6/2 e6/2 a6/6 g6/2 e6/4 | g6/6 f6/2 e6/4 b5/4 | a6/4 f6/4 c6/4 a5/4 | ~b5/8 g#5/4 e5/4')
C = ('~b5/8 e6/4 g6/4 | ~a6/8 g6/4 f6/4 | ~g6/8 d6/4 b5/4 | ~c6/12 a5/4 |'
     'e6/4 b5/4 g6/4 e6/4 | f6/4 c6/4 a6/4 f6/4 | d6/2 f6/2 a6/4 g6/2 f6/2 d6/4 | ~e6/8 g#6/4 b6/4')
SONG = dict(
    id='battle_kairen', title='검은 왕 카이렌', en='Kairen, the Black King', bpm=129, key='E', mode='phrygian', rt60=2.6, damp=4800,
    ch=dict(lead=dict(lp=4400, rev=0.3), comp=dict(gain=0.26, lp=2800), choir=dict(gain=0.42)),
    intro=['I'], loop=['A', 'B', 'C'],
    sections=dict(
        I=dict(bars=4, chords='Em F Em F', drone='e1', toll='e3/16 | r/16 | e3/16 | r/16', drums='none', perc=dict(b='x...............'), crash=False, fill='taiko'),
        A=dict(bars=8, chords='Em F Em F G Am F E', choir=CHA, organ=True, drone='e1', bass='dark', comp='darkpow', drums='darkhalf',
               ost='0.00.00.0.00.0.0', toll='e3/16 | r/16 | r/16 | r/16 | e3/16 | r/16 | r/16 | r/16', fill='taiko'),
        B=dict(bars=8, chords='Am Em F E Am Em F E', lead=B, bass='darkchug', comp='chug16', drums='darkdrive', choirpad=True, ost='0123012301230123'),
        C=dict(bars=8, chords='Em F G F Em F Dm E', lead=C, harm=True, choir=CHA, bass='chug8', comp='chug16', drums='double', perc=dict(T='x...x...x...x...'), fill='taiko'),
    ))
