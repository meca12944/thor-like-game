# 타이틀 — 「낙인의 서곡」  D minor, 138 BPM.  Dark choir/bell intro (reference style) -> heroic FM rock theme.
A = ('a4/4 d5/4 e5/2 f5/6 | f5/2 e5/2 d5/4 ~f5/8 | e5/4 g5/4 c6/6 bb5/2 | ~a5/12 g5/2 f5/2 |'
     'g5/4 bb5/4 d6/6 c6/2 | c#6/4 e6/4 ~a6/8 | ~f6/6 e6/2 d6/4 bb5/4 | ~a5/8 c#6/4 e6/4')
B = ('d6/6 c6/2 bb5/4 f5/4 | g5/6 a5/2 bb5/4 c6/4 | ~c6/8 a5/4 e5/4 | f5/6 e5/2 d5/8 |'
     'bb5/6 a5/2 g5/4 d6/4 | c6/6 bb5/2 a5/4 g5/4 | a5/4 c6/4 ~f6/8 | ~e6/8 c#6/4 a5/4')
TOLL = 'd3/16 | r/16 | d3/16 | a2/16'
SONG = dict(
    id='title', title='낙인의 서곡', en='Overture of the Brand', bpm=138, key='D', mode='harmonic', rt60=2.0,
    intro=['I1', 'I2'], loop=['A', 'B', 'A2', 'B2'],
    sections=dict(
        I1=dict(bars=4, chords='Dm Bb Gm A', choirpad=True, drone='d2', toll=TOLL, drums='none', crash=False, fill=None,
                perc=dict(T='x...............')),
        I2=dict(bars=2, chords='Bb A', comp='push', bass='root2', drums='none', fill='roll', perc=dict(T='x...x...x.x.xxxx')),
        A=dict(bars=8, chords='Dm Bb C Dm Gm A Bb A', lead=A, bass='drive8o', comp='power8', drums='drive', pad=True),
        B=dict(bars=8, chords='Bb C Am Dm Gm C F A', lead=B, bass='slap', comp='powersync', drums='drive16', arp='up16'),
        A2=dict(bars=8, chords='Dm Bb C Dm Gm A Bb A', lead=A, harm=True, bass='slap2', comp='power8', drums='drive', choirpad=True),
        B2=dict(bars=8, chords='Bb C Am Dm Gm C F A', lead=B, harm=True, bass='drive8o', comp='powersync', drums='drive16', pad=True, arp='up16', fill='tom'),
    ))
