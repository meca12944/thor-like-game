# 잠수 · 수중 (분수 아래, 잠수 지점, 산호 바다 해저) — 「심연의 물빛」  Eb lydian, 84 BPM.  Floating pads, bubbling bells, soft FM flute. No drums.
A = ('bb5/8 g5/4 d6/4 | ~c6/12 a5/4 | bb5/6 d6/2 g6/8 | ~f6/8 d6/4 a5/4 |'
     'g5/6 bb5/2 eb6/8 | ~d6/8 f6/4 bb5/4 | c6/6 bb5/2 g5/8 | ~a5/16')
B = ('eb6/8 c6/4 g5/4 | ~f6/12 d6/4 | d6/6 bb5/2 g5/8 | ~eb6/16 |'
     'c6/4 eb6/4 g6/8 | ~f6/8 d6/4 bb5/4 | g5/6 bb5/2 eb6/8 | ~c6/8 a5/8')
SONG = dict(
    id='underwater', title='심연의 물빛', en='Light of the Deep', bpm=84, key='Eb', mode='lydian', rt60=3.2, damp=3500, lufs=-15, delay=0.75, delay_fb=0.45,
    ch=dict(lead=dict(inst='flute', gain=0.26, lp=4500, hp=250, rev=0.5, dly=0.3), arp=dict(inst='bell', gain=0.08, low=67, rev=0.5, dly=0.35),
            bass=dict(inst='softbass', gain=0.36), pad=dict(gain=0.2, lp=3500)),
    intro=['I'], loop=['A', 'B'],
    sections=dict(
        I=dict(bars=2, chords='Ebmaj7 F', pad=True, arp='up8', drums='none', crash=False, fill=None),
        A=dict(bars=8, chords='Ebmaj7 F Gm Dm Cm7 Bb Abmaj7 F', lead=A, pad=True, arp='up8', bass='root2', drums='none', crash=False, fill=None),
        B=dict(bars=8, chords='Abmaj7 Bb Gm Cm7 Abmaj7 Bb Ebmaj7 F', lead=B, pad=True, arp='twinkle', bass='root1', choirpad=True, drums='none', crash=False, fill=None),
    ))
