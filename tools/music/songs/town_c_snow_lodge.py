# C 설산 산장 마을 — 「벽난로 곁에서」  Eb major, 3/4 waltz (12 sixteenths a bar), 96 BPM.  Fireside warmth: FM e-piano, flute, sleigh-bell shaker, celesta.
A = ('g5/8 bb5/4 | ~f5/8 d5/4 | eb5/4 g5/4 c6/4 | ~c6/8 bb5/2 ab5/2 |'
     'g5/4 bb5/4 eb6/4 | d6/8 bb5/4 | c6/4 ab5/4 f5/4 | ~bb5/12')
B = ('eb6/8 c6/4 | d6/8 bb5/4 | bb5/4 g5/4 d6/4 | ~c6/12 |'
     'ab5/4 c6/4 f6/4 | ~d6/8 bb5/4 | g5/4 bb5/4 g5/4 | ~eb5/12')
SONG = dict(
    id='town_c_snow_lodge', title='벽난로 곁에서', en='By the Fireside', bpm=96, bar=12, key='Eb', mode='major', rt60=2.0,
    ch=dict(lead=dict(inst='flute', gain=0.30, lp=7000, hp=200, rev=0.32), arp=dict(inst='epiano', gain=0.15, low=55, rev=0.3, dly=0.1),
            bell=dict(gain=0.10), bass=dict(inst='softbass', gain=0.42), lead2=dict(inst='bell', gain=0.07, shift=7, rev=0.45)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Eb Bb', arp='waltz', bass='waltz', drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='Eb Bb/D Cm Ab Eb Bb Ab Bb', lead=A, bass='waltz', arp='waltz', drums='waltz', crash=False, fill=None),
        B=dict(bars=8, chords='Ab Bb Gm Cm Fm Bb Eb Eb', lead=B, bass='waltz', arp='waltz', drums='waltz', pad=True, crash=False, fill=None),
        A2=dict(bars=8, chords='Eb Bb/D Cm Ab Eb Bb Ab Bb', lead=A, harm=True, bass='waltz2', arp='waltz', drums='waltz', pad=True, crash=False, fill=None),
    ))
