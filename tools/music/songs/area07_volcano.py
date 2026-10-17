# 7지역 화산 성채 — 「업화의 성채」  C minor, 176 BPM.  Heavy chugging FM guitars, double kick, furious 16th arpeggio runs.
A = ('g5/2 c6/2 g5/2 eb6/4 d6/2 c6/2 bb5/2 | c6/4 ab5/4 eb5/4 ab5/4 | bb5/2 d6/2 f6/4 eb6/2 d6/2 bb5/4 | ~c6/16 |'
     'eb6/2 d6/2 c6/2 g5/2 c6/4 eb6/4 | f6/4 eb6/2 c6/2 ab5/8 | ab5/4 c6/4 f6/4 ab6/4 | ~g6/8 d6/4 b5/4')
B = ('c6/1 eb6 ab6 eb6 c6 eb6 ab6 eb6 c6/4 ab5/4 | d6/1 f6 bb6 f6 d6 f6 bb6 f6 d6/4 bb5/4 | g6/6 f6/2 d6/4 bb5/4 | ~c6/12 d6/2 eb6/2 |'
     'f6/4 eb6/2 c6/2 ab5/4 c6/4 | b5/4 d6/4 g6/8 | ~ab6/8 g6/4 f6/4 | ~g6/8 f6/2 eb6/2 d6/2 b5/2')
SONG = dict(
    id='area07_volcano', title='업화의 성채', en='Citadel of Hellfire', bpm=176, key='C', mode='harmonic', rt60=1.3,
    ch=dict(comp=dict(gain=0.28)),
    intro=['I'], loop=['A', 'B', 'A2'],
    sections=dict(
        I=dict(bars=2, chords='Cm Ab:8 G:8', comp='chug16', bass='chug', drums='double', fill='tom'),
        A=dict(bars=8, chords='Cm Ab Bb Cm Cm Ab Fm G', lead=A, bass='chug8', comp='chug16', drums='drive16'),
        B=dict(bars=8, chords='Ab Bb Gm Cm Fm G Ab G', lead=B, bass='drive8o', comp='powersync', drums='double', brasspad='stab'),
        A2=dict(bars=8, chords='Cm Ab Bb Cm Cm Ab Fm G', lead=A, harm=True, bass='gallop', comp='chug16', drums='drive16', pad=True, fill='tom'),
    ))
