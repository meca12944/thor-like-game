# 진엔딩 「받은 힘」  F major, 84 BPM.  Hopeful credits theme: FM e-piano, strings, flute; brass-lead climax with soft drums.
A = ('c6/8 a5/4 f5/4 | g5/6 e5/2 c5/8 | d5/4 f5/4 a5/4 d6/4 | ~c6/8 a5/4 e5/4 |'
     'f5/6 g5/2 bb5/4 d6/4 | ~c6/8 a5/4 f5/4 | g5/4 bb5/4 d6/4 f6/4 | e6/8 d6/4 bb5/4')
B = ('d6/4 f6/4 bb6/6 a6/2 | g6/6 e6/2 c6/8 | c6/4 e6/4 a6/6 g6/2 | ~f6/12 e6/2 d6/2 |'
     'd6/4 bb5/4 g6/6 f6/2 | e6/6 d6/2 c6/4 g5/4 | a5/4 c6/4 f6/8 | ~f6/16')
SONG = dict(
    id='ending_true', title='받은 힘', en='The Power Given', bpm=84, key='F', mode='major', rt60=2.6, lufs=-15,
    ch=dict(lead=dict(inst='flute', gain=0.28, lp=6500, hp=200, rev=0.4, dly=0.15), counter=dict(inst='lead_soft', gain=0.26, pan=0.0, lp=5000, rev=0.4),
            arp=dict(inst='epiano', gain=0.16, low=53, rev=0.35), bass=dict(inst='softbass', gain=0.4), lead2=dict(inst='strings', gain=0.12)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='F C/E', arp='up8', pad=True, drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='F C/E Dm Am/C Bb F/A Gm C', lead=A, arp='up8', pad=True, bass='root2', drums='none', crash=False, fill=None),
        B=dict(bars=8, chords='Bb C Am Dm Gm C F F', counter=B, arp='alberti', pad=True, bass='walk', drums='half', fill=None),
        A2=dict(bars=8, chords='F C/E Dm Am/C Bb F/A Gm C', lead=A, harm=True, arp='up8', pad=True, choirpad=True, bass='town', drums='half', crash=False, fill=None),
    ))
