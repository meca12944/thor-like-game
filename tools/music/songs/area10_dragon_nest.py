# 10지역 마룡의 둥지 — 「세 머리의 둥지」  F# harmonic minor (+ Phrygian bII = G), 136 BPM.  Blend: dark choir/taiko + Ys rock drive.
A = ('c#5/4 f#5/4 a5/6 g#5/2 | f#5/4 a5/4 d6/8 | e6/6 d6/2 b5/4 g#5/4 | ~c#6/8 g#5/4 f5/4 |'
     'f#5/4 a5/4 c#6/4 f#6/4 | ~g6/8 f#6/4 d6/4 | e6/4 b5/4 g#5/4 b5/4 | ~c#6/12 b5/2 a5/2')
B = ('d6/6 c#6/2 b5/4 f#5/4 | e6/6 c#6/2 g#5/8 | a5/4 d6/4 f#6/4 a6/4 | ~g#6/8 e6/4 b5/4 |'
     'b5/4 d6/4 f#6/6 e6/2 | d6/6 b5/2 g5/8 | a5/4 c#6/4 f#6/4 e6/4 | ~f6/8 c#6/4 g#5/4')
CH = 'f#4/16 | g#4/16 | a4/16 | b4/16 | b4/16 | b4/16 | a4/16 | g#4/16'
SONG = dict(
    id='area10_dragon_nest', title='세 머리의 둥지', en='Nest of Three Heads', bpm=136, key='F#', mode='harmonic', rt60=2.4, damp=5000,
    ch=dict(lead=dict(lp=4200, rev=0.3)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=4, chords='F#m G F#m C#', choirpad=True, drone='f#1', drums='none', perc=dict(T='X.....x.....x...'), crash=False, fill='taiko'),
        A=dict(bars=8, chords='F#m D E C# F#m G E C#', lead=A, bass='darkchug', comp='chug16', drums='darkdrive', choirpad=True),
        B=dict(bars=8, chords='Bm C#m D E Bm G F#m C#', lead=B, choir=CH, bass='drive8o', comp='powersync', drums='drive16', ost='0123012301230123', perc=dict(T='x.......x.......')),
        A2=dict(bars=8, chords='F#m D E C# F#m G E C#', lead=A, harm=True, bass='darkchug', comp='chug16', drums='double', choirpad=True, perc=dict(T='x...x...x...x...'), fill='taiko'),
    ))
