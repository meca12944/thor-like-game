# 마왕 강림 컷신 (1회 재생) — 「강림」  E phrygian, 64 BPM (reference half-time pulse).  Heartbeat -> choir -> impact.
SONG = dict(
    id='demon_awaken', title='강림', en='The Descent', bpm=64, key='E', mode='phrygian', rt60=3.6, damp=4000,
    ch=dict(lead=dict(lp=3800, rev=0.5, dly=0.25, opt=dict(drive=4.0)), choir=dict(gain=0.45), comp=dict(gain=0.28, lp=2400)),
    intro=['S1', 'S2', 'S3'], loop=[],
    sections=dict(
        S1=dict(bars=3, chords='Em', drone='e1', drums='heart', toll='e3/16 | r/16 | f3/16', crash=False, fill=None),
        S2=dict(bars=4, chords='Em F G F', drone='e1', choirpad=True, choir='b4/16 | c5/16 | d5/16 | c5/8 b4/8', ost='0101010101010101',
                drums=dict(k='x..x............', T='x.......x.......'), crash=False, fill='taiko'),
        S3=dict(bars=2, chords='E Em', lead='~e6/16 | ~f6/8 e6/8', choirpad=True, comp='power1', bass='root1', drums=dict(b='x...............', T='x.....x.....x...'),
                toll='e3/16 | e3/16', fill=None),
    ))
