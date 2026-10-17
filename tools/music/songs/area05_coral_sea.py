# 5지역 산호 바다 — 「푸른 해류의 노래」  B dorian, 144 BPM.  Flowing, bright arps, ride cymbal, singing lead.
A = ('f#5/6 b5/2 c#6/4 d6/4 | e6/6 c#6/2 a5/8 | b5/4 d6/4 g6/6 f#6/2 | ~e6/12 c#6/4 |'
     'd6/4 f#6/4 b5/6 a5/2 | g#5/4 b5/4 e6/6 d6/2 | d6/4 b5/4 g5/4 b5/4 | ~a#5/8 c#6/4 f#6/4')
B = ('g6/6 f#6/2 d6/4 b5/4 | c#6/4 e6/4 ~a6/8 | ~a6/6 f#6/2 c#6/8 | d6/4 c#6/2 b5/2 f#5/8 |'
     'g5/4 b5/4 e6/6 d6/2 | c#6/6 b5/2 a5/4 e6/4 | ~f#6/8 d6/4 a5/4 | ~a#5/8 c#6/4 e6/4')
SONG = dict(
    id='area05_coral_sea', title='푸른 해류의 노래', en='Song of the Blue Current', bpm=144, key='B', mode='dorian', rt60=2.0, delay=0.75,
    ch=dict(lead=dict(opt=dict(drive=2.2, vib=0.32), rev=0.3, dly=0.22), arp=dict(inst='bell', gain=0.07, low=71, rev=0.4)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Bm A', arp='up16', pad=True, bass='root2', drums='none', fill='snare'),
        A=dict(bars=8, chords='Bm A G A Bm E G F#', lead=A, bass='slap', drums='ride', arp='up16', pad=True),
        B=dict(bars=8, chords='G A F#m Bm Em A D F#', lead=B, bass='drive8o', comp='powersync', drums='drive16', arp='cascade'),
        A2=dict(bars=8, chords='Bm A G A Bm E G F#', lead=A, harm=True, bass='slap2', comp='power8', drums='drive', arp='up16', fill='tom'),
    ))
