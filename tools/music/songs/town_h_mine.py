# H 서쪽 광산 마을 — 「등잔불 광부들」  D dorian, 120 BPM.  Shuffling workers' groove, pick bass walk, anvil/pick clinks.
A = ('d5/2 f5/2 a5/4 g5/2 f5/2 d5/4 | b5/4 a5/2 g5/2 d5/8 | f5/2 a5/2 c6/4 b5/2 a5/2 f5/4 | ~g5/16 |'
     'a5/4 c6/4 f6/6 e6/2 | ~e6/8 d6/2 c6/2 g5/4 | f5/4 a5/4 d6/4 c6/4 | ~a5/8 e5/4 c5/4')
B = ('d6/6 c6/2 bb5/4 f5/4 | e5/4 g5/4 c6/8 | ~d6/8 a5/4 f5/4 | d5/2 e5/2 f5/2 g5/2 a5/4 b5/4 |'
     'd6/6 bb5/2 f5/8 | g5/4 c6/4 e6/8 | ~c#6/8 e6/4 a5/4 | ~a5/16')
SONG = dict(
    id='town_h_mine', title='등잔불 광부들', en='Lamplight Miners', bpm=120, key='D', mode='dorian', rt60=1.5,
    ch=dict(lead=dict(inst='lead_soft', gain=0.27, lp=5000, hp=180), lead2=dict(inst='psg', gain=0.08, opt=dict(duty=0.25)),
            bass=dict(inst='pickbass', gain=0.42), comp=dict(inst='pluck', type='comp', gain=0.12, strum=0.012, center=60, lp=5000)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Dm G', bass='walk8', drums='shuffle', perc=dict(an='............x...'), fill=None),
        A=dict(bars=8, chords='Dm G Dm G F C Dm Am', lead=A, bass='walk8', comp='offbeat', drums='shuffle', perc=dict(an='............x...'), crash=False),
        B=dict(bars=8, chords='Bb C Dm Dm Bb C A A', lead=B, bass='bounce', comp='strum', drums='shuffle', pad=True, perc=dict(an='....x.......x...'), crash=False),
        A2=dict(bars=8, chords='Dm G Dm G F C Dm Am', lead=A, harm=True, bass='walk8', comp='offbeat', drums='shuffle', perc=dict(an='............x...'), crash=False),
    ))
