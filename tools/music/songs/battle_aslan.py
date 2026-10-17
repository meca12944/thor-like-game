# 숨은 최종 인간 보스 아스란 (원탁의 심연) — 「영겁의 심판자」  D minor, 156 BPM.  Tragic-heroic: bell prologue, Neapolitan Eb, strings + choir + FM rock.
INTRO = 'a5/8 f5/8 | g5/8 e5/8 | d5/8 bb4/8 | c#5/16'
A = ('d5/4 a5/4 g5/2 f5/2 e5/2 f5/2 | g5/4 e5/4 c6/8 | bb5/2 a5/2 bb5/2 d6/2 f6/4 d6/4 | ~c#6/8 e6/4 a5/4 |'
     'g5/2 bb5/2 d6/2 g6/2 f6/4 d6/4 | ~f6/8 e6/2 d6/2 a5/4 | g5/4 bb5/4 eb6/6 d6/2 | ~c#6/12 e6/4')
B = ('f6/6 d6/2 bb5/4 d6/4 | e6/6 c6/2 g5/4 c6/4 | ~a5/8 c6/4 e6/4 | d6/6 e6/2 f6/8 |'
     'g6/4 f6/4 d6/4 bb5/4 | c6/4 e6/4 g6/8 | ~a6/8 f6/4 c6/4 | ~e6/8 c#6/4 a5/4')
SONG = dict(
    id='battle_aslan', title='영겁의 심판자', en='Judge of Eternity', bpm=156, key='D', mode='harmonic', rt60=2.0,
    ch=dict(bell=dict(gain=0.17), choirpad=dict(gain=0.17)),
    intro=['I', 'I2'], loop=['A', 'B', 'A2', 'B2'],
    sections=dict(
        I=dict(bars=4, chords='Dm C Bb A', bell=INTRO, pad=True, drone='d2', drums='none', crash=False, fill=None),
        I2=dict(bars=2, chords='Gm A', comp='chug16', bass='chug', drums='double', fill='tom'),
        A=dict(bars=8, chords='Dm C Bb A Gm Dm Eb A', lead=A, bass='drive8o', comp='power8', drums='drive', pad=True),
        B=dict(bars=8, chords='Bb C Am Dm Gm C F A', lead=B, bass='slap', comp='powersync', drums='drive16', choirpad=True, arp='up16'),
        A2=dict(bars=8, chords='Dm C Bb A Gm Dm Eb A', lead=A, harm=True, bass='gallop', comp='power8', drums='double', choirpad=True, ost='0101010101010101'),
        B2=dict(bars=8, chords='Bb C Am Dm Gm C F A', lead=B, harm=True, bass='drive8o', comp='powersync', drums='drive16', pad=True, brasspad='stab', fill='tom'),
    ))
