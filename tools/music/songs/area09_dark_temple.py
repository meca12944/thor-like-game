# 9지역 어둠 신전 — 「멈춘 시간의 신전」  F harmonic minor, 112 BPM.  Dark (reference style): organ, choir, clock-tick hats, toll, Neapolitan Gb.
A = ('c5/8 ab5/4 g5/4 | ~f5/12 eb5/2 db5/2 | bb4/4 db5/4 f5/4 bb5/4 | ~e5/8 g5/4 bb5/4 |'
     'ab5/6 g5/2 f5/4 c6/4 | ~db6/8 bb5/4 gb5/4 | f5/4 ab5/4 db6/4 c6/4 | ~c6/8 bb5/2 g5/2 e5/4')
B = ('db6/4 c6/4 bb5/4 f5/4 | ab5/4 g5/4 f5/4 c5/4 | db5/4 f5/4 ab5/4 db6/4 | ~c6/8 e6/4 g6/4 |'
     '~f6/8 db6/4 bb5/4 | c6/6 ab5/2 f5/8 | gb5/4 bb5/4 db6/4 gb6/4 | ~e6/8 c6/4 g5/4')
CH = 'f4/16 | f4/16 | f4/16 | e4/16 | f4/16 | ab4/16 | bb4/16 | g4/16'
TICK = dict(h='x...x...x...x...')
SONG = dict(
    id='area09_dark_temple', title='멈춘 시간의 신전', en='Temple of Stopped Time', bpm=112, key='F', mode='harmonic', rt60=3.0, damp=4200,
    ch=dict(lead=dict(lp=3300, rev=0.38, dly=0.22, opt=dict(drive=2.6)), comp=dict(gain=0.18, lp=2400)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=4, chords='Fm Db Gb C', organ=True, drone='f1', toll='f3/16 | r/16 | f3/16 | c3/16', drums=TICK, crash=False, fill=None),
        A=dict(bars=8, chords='Fm Db Bbm C Fm Gb Db C', lead=A, organ=True, drone='f1', bass='dark', drums='darkhalf', ost='0.0.0.0.0.0.0.0.'),
        B=dict(bars=8, chords='Bbm Fm Db C Bbm Fm Gb C', lead=B, choir=CH, bass='darkchug', comp='darkpow', drums='darkdrive', ost='0101010101010101', fill='taiko'),
        A2=dict(bars=8, chords='Fm Db Bbm C Fm Gb Db C', lead=A, harm=-5, organ=True, choirpad=True, bass='dark', comp='darkpow', drums='darkhalf', toll='f3/16 | r/16 | r/16 | r/16 | f3/16 | r/16 | r/16 | c3/16', fill='taiko'),
    ))
