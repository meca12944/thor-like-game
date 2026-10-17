# 대장간·상점 (모든 마을 공용) — 「불꽃 망치의 대장간」  G mixolydian, 116 BPM.  Cheerful shop loop, anvil groove, PSG lead.
A = ('g5/2 g5/2 b5/2 d6/2 c6/4 b5/4 | a5/2 a5/2 c6/2 f6/2 d6/4 c6/4 | e6/4 c6/4 g5/4 e5/4 | ~g5/8 f5/4 d5/4 |'
     'b5/2 b5/2 d6/2 g6/2 f6/4 d6/4 | c6/2 c6/2 a5/2 f5/2 a5/4 c6/4 | e6/4 g6/4 e6/4 c6/4 | ~d6/8 f#6/4 a6/4')
SONG = dict(
    id='forge_shop', title='불꽃 망치의 대장간', en='The Flame-hammer Smithy', bpm=116, key='G', mode='mixolydian', rt60=1.3,
    ch=dict(lead=dict(inst='psg', gain=0.16, lp=7000, hp=200, opt=dict(duty=0.25), rev=0.15, dly=0.12), lead2=dict(inst='psg', gain=0.09, opt=dict(duty=0.5)),
            bass=dict(inst='pickbass', gain=0.42), comp=dict(inst='pluck', type='comp', gain=0.12, strum=0.01, center=62, lp=5000)),
    intro=[], loop=['A', 'A2'],
    sections=dict(
        A=dict(bars=8, chords='G F C G G F C D', lead=A, bass='bounce', comp='offbeat', drums='town2', perc=dict(an='....x.......x...'), crash=False, fill=None),
        A2=dict(bars=8, chords='G F C G G F C D', lead=A, harm=True, bass='walk8', comp='offbeat', drums='town2', perc=dict(an='....x..x....x.x.'), crash=False, fill=None),
    ))
