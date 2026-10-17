# 3지역 모래 사막 — 「태양의 모래바다」  D phrygian dominant, 150 BPM.  Exotic scale, plucked strums, fast 16th runs.
A = ('a5/2 bb5/2 a5/2 f#5/2 d5/4 f#5/4 | g5/4 bb5/4 ~eb6/6 d6/2 | c6/2 bb5/2 a5/4 f#5/4 a5/4 | ~a5/12 g5/2 f#5/2 |'
     'g5/4 bb5/4 d6/6 c6/2 | bb5/4 g5/4 eb6/6 d6/2 | c6/2 eb6/2 c6/2 bb5/2 a5/4 g5/4 | ~f#5/8 a5/4 d6/4')
B = ('g5/1 a5 bb5 a5 g5 f#5 g5 a5 bb5/2 d6/2 g6/4 | f#6/2 g6/2 f#6/2 eb6/2 d6/4 bb5/4 | ~a5/8 f#5/4 a5/4 |'
     'd6/1 c6 bb5 a5 bb5 a5 g5 f#5 g5 f#5 eb5 d5 eb5/2 f#5/2 |'
     'eb6/4 d6/2 c6/2 g5/8 | g5/4 bb5/4 eb6/4 g6/4 | ~f#6/6 eb6/2 d6/4 c6/4 | ~d6/16')
SONG = dict(
    id='area03_desert', title='태양의 모래바다', en='Sea of Sun-baked Sand', bpm=150, key='D', mode='phrydom', rt60=1.5,
    ch=dict(arp=dict(inst='pluck', gain=0.13, low=57, pan=-0.3, opt=dict(decay=0.4))),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='D Eb', arp='six8', bass='sync', drums='none', perc=dict(T='x.....x.....x...', sh='x.xxx.xxx.xxx.xx'), fill=None),
        A=dict(bars=8, chords='D Eb D D Gm Eb Cm D', lead=A, bass='sync', comp='power8', drums='drive', arp='up16', perc=dict(sh='x.xxx.xxx.xxx.xx')),
        B=dict(bars=8, chords='Gm Eb D D Cm Eb D D', lead=B, bass='slap', comp='powersync', drums='drive16', pad=True),
        A2=dict(bars=8, chords='D Eb D D Gm Eb Cm D', lead=A, harm=True, bass='sync2', comp='power8', drums='drive', arp='up16', fill='tom'),
    ))
