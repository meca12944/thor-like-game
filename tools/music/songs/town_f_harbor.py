# F 남쪽 항구 마을 — 「등대와 갈매기」  D major, 128 BPM.  Bouncy harbour tune: FM brass-flute lead, plucked offbeats, sea breeze pads.
A = ('a4/2 d5/2 f#5/4 a5/4 f#5/4 | g5/4 b5/4 d6/6 b5/2 | a5/4 f#5/2 a5/2 d6/4 a5/4 | ~e5/12 f#5/2 g5/2 |'
     'a5/2 b5/2 a5/4 f#5/4 d5/4 | b4/4 d5/2 g5/2 b5/8 | a5/4 g5/4 e5/4 c#5/4 | ~d5/12 r/4')
B = ('f#5/4 b5/4 d6/6 c#6/2 | c#6/4 a5/4 f#5/8 | g5/4 b5/4 d6/4 g6/4 | ~f#6/12 e6/2 d6/2 |'
     'e6/6 d6/2 b5/4 g5/4 | a5/6 b5/2 c#6/4 e6/4 | d6/4 a5/4 f#5/4 a5/4 | ~e5/16')
SONG = dict(
    id='town_f_harbor', title='등대와 갈매기', en='Lighthouse and Gulls', bpm=128, key='D', mode='major', rt60=1.7,
    ch=dict(lead=dict(inst='lead_soft', gain=0.27, lp=6000, hp=200, rev=0.25, dly=0.15), lead2=dict(inst='flute', gain=0.13),
            comp=dict(inst='pluck', type='comp', gain=0.13, strum=0.01, center=64, lp=6000), bass=dict(inst='pickbass', gain=0.40)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='D A', comp='offbeat', bass='bounce', drums='town2', crash=False, fill=None),
        A=dict(bars=8, chords='D G D A D G A D', lead=A, bass='bounce', comp='offbeat', drums='town2', crash=False, fill=None),
        B=dict(bars=8, chords='Bm F#m G D Em A D A', lead=B, bass='town', comp='strum', drums='town', pad=True, crash=False, fill=None),
        A2=dict(bars=8, chords='D G D A D G A D', lead=A, harm=True, bass='bounce', comp='offbeat', drums='town2', pad=True, crash=False, fill=None),
    ))
