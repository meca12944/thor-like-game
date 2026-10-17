# B 강변 물레방아 마을 — 「물레방아는 돌고」  G major, 6/8 (12 sixteenths a bar), 132 BPM(=4분음표).  Lilting river dance.
A = ('d5/4 g5/2 b5/4 a5/2 | g5/4 e5/2 c6/6 | a5/4 f#5/2 d5/4 f#5/2 | ~g5/12 |'
     'b5/4 g5/2 e6/4 d6/2 | c6/4 b5/2 a5/4 g5/2 | f#5/4 a5/2 d6/4 c6/2 | ~a5/6 b5/2 c6/2 a5/2')
B = ('e6/6 d6/4 c6/2 | d6/6 a5/4 f#5/2 | b5/4 d6/2 f#6/4 e6/2 | ~e6/12 |'
     'c6/4 a5/2 e6/4 c6/2 | d6/4 c6/2 a5/4 f#5/2 | g5/4 b5/2 d6/4 b5/2 | ~g5/12')
SONG = dict(
    id='town_b_watermill', title='물레방아는 돌고', en='The Watermill Turns', bpm=132, bar=12, key='G', mode='major', rt60=1.6,
    ch=dict(lead=dict(inst='lead_soft', gain=0.26, lp=6000, hp=200, rev=0.25), lead2=dict(inst='flute', gain=0.14, lp=6000, shift=2),
            arp=dict(inst='pluck', gain=0.16, low=55, opt=dict(decay=0.45)), bass=dict(inst='softbass', gain=0.38)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='G D', arp='six8', bass='six8', drums='six8', crash=False, fill=None),
        A=dict(bars=8, chords='G C D G Em C D D', lead=A, bass='six8', arp='six8', drums='six8', crash=False, fill=None),
        B=dict(bars=8, chords='C D Bm Em Am D G G', lead=B, bass='six8', arp='six8', drums='six8', pad=True, crash=False, fill=None),
        A2=dict(bars=8, chords='G C D G Em C D D', lead=A, harm=True, bass='six8', arp='six8', drums='six8', pad=True, crash=False, fill=None),
    ))
