# 마왕 필드 (강림 이후 월드맵 · 검은 성채) — 「멸계의 행진」  D phrygian, 129 BPM.  Dark march (reference style): taiko, chant choir, chugging FM guitars.
A = ('d5/4 a5/4 bb5/6 a5/2 | g5/4 eb5/4 bb4/8 | d5/4 f5/4 a5/4 d6/4 | c6/8 bb5/4 g5/4 |'
     'f5/4 bb5/4 d6/6 c6/2 | bb5/4 g5/4 eb6/8 | d6/4 bb5/4 g5/4 bb5/4 | ~a5/8 c#6/4 e6/4')
B = '~d6/16 | ~eb6/16 | f6/8 d6/8 | ~e6/16 | ~g6/8 f6/4 d6/4 | ~f6/8 d6/4 bb5/4 | ~bb5/8 g5/4 eb5/4 | ~e5/8 a5/4 c#6/4'
CH = 'g4/16 | g4/16 | f4/16 | e4/16 | g4/16 | f4/16 | g4/16 | e4/8 c#5/8'
SONG = dict(
    id='demon_field', title='멸계의 행진', en='March of World\'s End', bpm=129, key='D', mode='phrygian', rt60=2.6, damp=4500,
    ch=dict(lead=dict(lp=3800, rev=0.32), comp=dict(gain=0.26, lp=2600), choir=dict(gain=0.42)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Dm Eb', drone='d1', drums='heart', toll='d3/16 | r/16', crash=False, fill=None),
        A=dict(bars=8, chords='Dm Eb Dm C Bb Eb Gm A', lead=A, drone='d1', bass='dark', comp='darkpow', drums='taiko', ost='0.00.00.0.00.0.0'),
        B=dict(bars=8, chords='Gm Eb Dm A Gm Bb Eb A', lead=B, choir=CH, organ=True, bass='darkchug', comp='chug16', drums='darkdrive', fill='taiko'),
        A2=dict(bars=8, chords='Dm Eb Dm C Bb Eb Gm A', lead=A, harm=-7, choirpad=True, bass='dark', comp='darkpow', drums='taiko2', toll='d3/16 | r/16 | r/16 | r/16 | d3/16 | r/16 | r/16 | r/16', fill='taiko'),
    ))
