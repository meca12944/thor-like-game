# 빛의 엔딩 「빛의 계승」  D major, 96 BPM.  Bittersweet heroic rock ballad: clean-ish FM guitar, strings, half-time drums.
A = ('f#5/6 e5/2 d5/4 a5/4 | a5/6 b5/2 c#6/8 | d6/6 c#6/2 b5/4 f#5/4 | ~a5/12 c#6/4 |'
     'd6/6 b5/2 g5/4 b5/4 | ~a5/8 f#5/4 d5/4 | e5/4 g5/4 b5/4 e6/4 | ~c#6/12 a5/4')
B = ('f#6/6 e6/2 d6/4 b5/4 | d6/6 b5/2 g5/8 | a5/4 d6/4 f#6/6 e6/2 | ~e6/12 c#6/4 |'
     'b5/4 e6/4 g6/6 f#6/2 | ~e6/8 d6/4 b5/4 | c#6/4 e6/4 a6/8 | ~g6/8 e6/4 c#6/4')
SONG = dict(
    id='ending_light', title='빛의 계승', en='Inheritance of Light', bpm=96, key='D', mode='major', rt60=2.2, lufs=-15,
    ch=dict(lead=dict(opt=dict(drive=1.8, vib=0.3), gain=0.27, lp=4800, rev=0.35, dly=0.2), arp=dict(inst='pluck', gain=0.13, low=57),
            bass=dict(inst='pickbass', gain=0.4), comp=dict(gain=0.14)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='D A/C#', arp='up8', pad=True, drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='D A/C# Bm F#m/A G D/F# Em A', lead=A, arp='up8', pad=True, bass='root2', drums='half', crash=False, fill=None),
        B=dict(bars=8, chords='Bm G D A Em G A A', lead=B, comp='push', pad=True, bass='walk8', drums='rock', fill='snare'),
        A2=dict(bars=8, chords='D A/C# Bm F#m/A G D/F# Em A', lead=A, harm=True, arp='up16', pad=True, bass='town', drums='half', fill=None),
    ))
