# 마왕 엔딩 「새로운 검은 왕」 (특별판 「잿더미의 왕」 공용)  E phrygian, 129 BPM half-time.  Grand and dark, closest to the reference:
# sub drone, organ + choir, funeral bell, taiko and chugging low guitars, slow-burning lead.
CH = 'b4/16 | c5/16 | b4/16 | a4/16 | b4/16 | c5/16 | a4/16 | g#4/16'
B = '~e6/16 | ~f6/8 e6/4 c6/4 | ~b5/16 | a5/4 c6/4 f6/8 | ~d6/8 b5/4 g5/4 | ~c6/8 e6/4 a6/4 | ~a6/8 f6/4 c6/4 | ~b5/8 g#5/4 e5/4'
SONG = dict(
    id='ending_demon', title='새로운 검은 왕', en='The New Black King', bpm=129, key='E', mode='phrygian', rt60=3.2, damp=4200, lufs=-15,
    ch=dict(lead=dict(lp=3600, rev=0.4, dly=0.2), choir=dict(gain=0.42), comp=dict(gain=0.24, lp=2400)),
    intro=['I'], loop=['A', 'B', 'C'],
    sections=dict(
        I=dict(bars=4, chords='Em F Em F', drone='e1', toll='e3/16 | r/16 | e3/16 | r/16', drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='Em F Em F G Am F E', choir=CH, organ=True, drone='e1', drums='darkhalf', bass='half2', crash=False, fill='taiko'),
        B=dict(bars=8, chords='Em F Em F G Am F E', lead=B, choir=CH, choirpad=True, bass='darkchug', comp='darkpow', drums='darkdrive', ost='0101010101010101', fill='taiko'),
        C=dict(bars=4, chords='Em F Em F', drone='e1', organ=True, toll='e3/16 | r/16 | e3/16 | f3/16', drums=dict(T='x...........x...'), crash=False, fill=None),
    ))
