# 비극 엔딩 「낙인의 끝」  A minor, 72 BPM.  Sparse and sad: flute over FM e-piano and strings; e-piano solo second half; one bell.
A = ('e5/8 a5/4 b5/4 | ~c6/12 b5/4 | a5/6 g5/2 f5/8 | ~e5/8 g#5/4 b5/4 |'
     'a5/6 f5/2 d6/8 | ~c6/8 b5/4 a5/4 | f5/4 a5/4 d6/4 c6/4 | ~b5/16')
B = ('c6/4 a5/4 f5/8 | d6/4 b5/4 g5/8 | e6/4 b5/4 g5/4 e5/4 | ~a5/16 |'
     'f6/6 e6/2 d6/8 | e6/6 d6/2 b5/8 | c6/4 a5/4 f5/4 a5/4 | ~g#5/16')
SONG = dict(
    id='ending_tragic', title='낙인의 끝', en='End of the Brand', bpm=72, key='A', mode='minor', rt60=2.8, lufs=-16,
    ch=dict(lead=dict(inst='flute', gain=0.28, lp=6000, hp=200, rev=0.42), counter=dict(inst='epiano', gain=0.24, pan=0.1, lp=6000, rev=0.4, hp=150),
            arp=dict(inst='epiano', gain=0.14, low=52, rev=0.4), bass=dict(inst='softbass', gain=0.36)),
    intro=[], loop=['A', 'B'],
    sections=dict(
        A=dict(bars=8, chords='Am Am/G F E Dm Am Dm E', lead=A, arp='up8', pad=True, bass='root1', drums='none', crash=False, fill=None),
        B=dict(bars=8, chords='F G Em Am Dm Em F E', counter=B, arp='up8', pad=True, bass='root1', toll='r/16 | r/16 | r/16 | r/16 | r/16 | r/16 | r/16 | a2/16', drums='none', crash=False, fill=None),
    ))
