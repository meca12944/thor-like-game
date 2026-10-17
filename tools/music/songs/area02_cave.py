# 2지역 수정 동굴 — 「수정 속의 자장가」  C# minor, 132 BPM.  Echoing crystal bells, syncopated slap bass, a little lullaby (돌님).
LULL = 'g#5/4 e5/4 c#5/4 e5/4 | f#5/4 a5/4 g#5/8 | f#5/4 d#5/4 b4/4 d#5/4 | e5/8 d#5/8'
A = ('c#5/6 e5/2 g#5/4 c#6/4 | b5/2 a5/2 e5/4 c#5/8 | d#5/4 f#5/4 b5/6 a5/2 | ~g#5/16 |'
     'e5/4 g#5/4 c#6/4 e6/4 | ~e6/8 c#6/4 a5/4 | f#5/4 a5/4 c#6/4 b5/2 a5/2 | ~g#5/8 c6/4 d#6/4')
B = ('e6/6 c#6/2 b5/4 a5/4 | f#6/6 d#6/2 b5/8 | g#5/4 c#6/4 e6/4 g#6/4 | ~g#6/12 f#6/2 e6/2 |'
     'f#6/4 e6/4 c#6/4 a5/4 | b5/4 g#5/4 d#6/8 | c#6/4 e6/4 a6/6 g#6/2 | ~g#6/16')
SONG = dict(
    id='area02_cave', title='수정 속의 자장가', en='Lullaby in the Crystal', bpm=132, key='C#', mode='minor', rt60=2.4, delay=0.75,
    ch=dict(lead=dict(lp=4800, rev=0.3, dly=0.25, opt=dict(drive=2.4)), arp=dict(inst='bell', gain=0.07, low=68, rev=0.45),
            bell=dict(gain=0.16)),
    intro=['I'], loop=['A', 'B', 'C'],
    sections=dict(
        I=dict(bars=4, chords='C#m A B G#m', bell=LULL, pad=True, drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='C#m A B G#m C#m A F#m G#', lead=A, bass='slap3', drums='rock', arp='alberti', pad=True),
        B=dict(bars=8, chords='A B C#m C#m F#m G#m A G#', lead=B, harm=True, bass='slap', comp='powersync', drums='drive16', arp='up16'),
        C=dict(bars=4, chords='C#m A B G#m', bell=LULL, bass='half', drums='half', pad=True, arp='alberti', fill='tom'),
    ))
