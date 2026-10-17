# G 사막 바자르 — 「사프란 바자르」  A phrygian dominant, 116 BPM.  Market bustle: hand-perc groove, camel bells, plucked strings, FM flute.
A = ('e5/2 f5/2 e5/2 c#5/2 a4/4 c#5/4 | d5/2 f5/2 bb5/4 a5/4 f5/4 | e5/4 c#5/4 e5/4 a5/4 | g5/6 f5/2 e5/8 |'
     'a5/2 bb5/2 a5/2 g5/2 f5/2 e5/2 c#5/4 | d5/4 f5/4 bb5/8 | bb5/2 a5/2 g5/2 f5/2 g5/4 bb5/4 | ~a5/16')
B = ('f5/4 a5/4 d6/6 e6/2 | f6/4 e6/2 d6/2 bb5/8 | ~c#6/8 a5/4 e5/4 | e6/1 f6 e6 d6 c#6 d6 c#6 bb5 a5/4 e5/4 |'
     'd6/4 f6/4 a6/8 | ~g6/8 f6/4 d6/4 | e6/4 c#6/4 bb5/4 g5/4 | ~a5/16')
SONG = dict(
    id='town_g_bazaar', title='사프란 바자르', en='Saffron Bazaar', bpm=116, key='A', mode='phrydom', rt60=1.5,
    ch=dict(lead=dict(inst='flute', gain=0.30, lp=7000, hp=200, rev=0.25), lead2=dict(inst='pluck', gain=0.16, opt=dict(decay=0.35)),
            arp=dict(inst='pluck', gain=0.16, low=57, opt=dict(decay=0.3)), bass=dict(inst='softbass', gain=0.38)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='A Bb', drums='bossa', perc=dict(cb='x...............'), bass='bounce', crash=False, fill=None),
        A=dict(bars=8, chords='A Bb A Gm A Bb Gm A', lead=A, bass='bounce', arp='alberti', drums='bossa', perc=dict(cb='x.......x.......', T='x.....x.........'), crash=False, fill=None),
        B=dict(bars=8, chords='Dm Gm A A Dm Bb A A', lead=B, bass='sync', arp='up16', drums='bossa', pad=True, perc=dict(cb='x...............'), crash=False, fill=None),
        A2=dict(bars=8, chords='A Bb A Gm A Bb Gm A', lead=A, harm=-7, bass='bounce', arp='alberti', drums='bossa', perc=dict(cb='x.......x.......', T='x.....x.........'), crash=False, fill=None),
    ))
