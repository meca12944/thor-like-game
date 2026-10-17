# A 시작 마을 분수 마을 — 「분수가 있는 광장」  F major, 112 BPM.  Warm, peaceful home theme: FM flute, plucked arps, soft bass.
A = ('a5/6 g5/2 f5/4 c5/4 | e5/4 g5/4 c6/8 | d6/6 c6/2 a5/4 f5/4 | g5/6 f5/2 d5/8 |'
     'c5/4 f5/4 a5/4 c6/4 | ~e6/8 d6/2 c6/2 g5/4 | d6/6 c6/2 bb5/4 a5/4 | ~g5/16')
B = ('f6/6 d6/2 bb5/8 | e6/6 c6/2 g5/8 | a5/4 c6/4 e6/4 c6/4 | d6/8 c6/4 a5/4 |'
     'bb5/6 a5/2 g5/4 d6/4 | c6/6 bb5/2 g5/4 e5/4 | f5/4 a5/4 c6/4 a5/4 | ~f5/16')
SONG = dict(
    id='town_a_fountain', title='분수가 있는 광장', en='The Fountain Square', bpm=112, key='F', mode='major', rt60=1.8,
    ch=dict(lead=dict(inst='flute', gain=0.30, lp=7000, hp=200, rev=0.3, dly=0.15),
            lead2=dict(inst='flute', gain=0.14, lp=6000), arp=dict(inst='pluck', gain=0.16, low=60, opt=dict(decay=0.5)),
            bass=dict(inst='softbass', gain=0.38)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='F C', arp='up8', bass='town', drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='F C/E Dm Bb F C Bb C', lead=A, bass='town', arp='up8', drums='town', pad=True, crash=False, fill=None),
        B=dict(bars=8, chords='Bb C Am Dm Gm C F F', lead=B, bass='bounce', arp='alberti', drums='town2', pad=True, crash=False, fill=None),
        A2=dict(bars=8, chords='F C/E Dm Bb F C Bb C', lead=A, harm=True, bass='town', arp='up8', drums='town', bell='c6/16 | r/16 | a5/16 | r/16 | c6/16 | r/16 | bb5/16 | r/16', crash=False, fill=None),
    ))
