"""hero_v3_motion.py - hand-keyed poses for idle / walk / run / dodge in 4 directions, follow-through (cape + hair lag
1 frame), rendering to 1x RGBA frames + per-frame anchors.  Timings come from hero_v3_guides.json (60 fps ticks)."""
import sys, os, math, copy, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hero_v3_pix import *
T = G['timing']; MO = G['motions']
SIDE_IDLE = {'R': {'a': (1.2, 57.4)}, 'L': {'a': (-.6, 57.4)}}
FB_IDLE = {'R': {'a': (0, 57)}, 'L': {'a': (0, 57)}}
def sw(d):  # swap legs + arms
    o = copy.deepcopy(d); o['R'], o['L'] = d['L'], d['R']; o['armR'], o['armL'] = d.get('armL', 0), d.get('armR', 0); return o

# ---------------- WALK (contact, down, passing, up) x 2; R = near leg in side view, R forward at frame 0 ----------
WALK_SIDE = [dict(R={'a': (10.6, 56.5), 'fa': -18}, L={'a': (-10.5, 55.0), 'fa': 38}, armR=-1.0, armL=1.0),
             dict(R={'a': (4.6, 57.4), 'fa': 0}, L={'a': (-6.4, 52.4), 'fa': 52}, armR=-.7, armL=.7),
             dict(R={'a': (-1.6, 57.4), 'fa': 0}, L={'a': (1.0, 53.0), 'fa': 20}, armR=0.05, armL=-.05),
             dict(R={'a': (-8.0, 56.6), 'fa': 24}, L={'a': (7.2, 54.4), 'fa': -8}, armR=.7, armL=-.7)]
WALK_FB = [dict(R={'a': (0, 57.2)}, L={'a': (.3, 55.6), 'toe': 1, 'back': 1}, armR=-1.0, armL=1.0),
           dict(R={'a': (0, 57)}, L={'a': (.5, 53.6), 'toe': 1, 'back': 1, 'kf': .5}, armR=-.7, armL=.7),
           dict(R={'a': (0, 57)}, L={'a': (.6, 52.6), 'kf': 1}, armR=0.05, armL=-.05),
           dict(R={'a': (0, 56.4), 'toe': 1, 'back': 1}, L={'a': (.2, 55.8), 'kf': .4}, armR=.7, armL=-.7)]
# ---------------- RUN (contact, down, push-off, float) x 2 ----------
RUN_SIDE = [dict(R={'a': (11.4, 56.6), 'fa': -12}, L={'a': (-9.0, 50.4), 'fa': 62}, armR=-1.2, armL=1.1),
            dict(R={'a': (0.6, 57.4), 'fa': 0}, L={'a': (-4.6, 47.6), 'fa': 78}, armR=-.6, armL=.5),
            dict(R={'a': (-11.2, 56.0), 'fa': 34}, L={'a': (5.6, 49.6), 'fa': 8}, armR=.7, armL=-.8),
            dict(R={'a': (-12.0, 52.6), 'fa': 58}, L={'a': (10.2, 53.8), 'fa': -14}, armR=1.2, armL=-1.2)]
RUN_FB = [dict(R={'a': (0, 57.2)}, L={'a': (.6, 52.4), 'toe': 1, 'back': 1, 'kf': .3}, armR=-1.2, armL=1.2),
          dict(R={'a': (0, 57)}, L={'a': (.8, 50.4), 'kf': .9}, armR=-.6, armL=.6),
          dict(R={'a': (0, 56.0), 'toe': 1, 'back': 1}, L={'a': (.6, 51.0), 'kf': 1.3}, armR=.6, armL=-.6),
          dict(R={'a': (0, 53.6), 'toe': 1, 'back': 1, 'kf': .2}, L={'a': (.3, 55.4), 'kf': .6}, armR=1.2, armL=-1.2)]
# ---------------- DODGE (anticipation, launch, dash, glide, brake, recover) ----------
DODGE_SIDE = [dict(bob=3, lean=1, R={'a': (3.4, 57.4)}, L={'a': (-3.0, 57.4), 'fa': 8}, armR=-.8, armL=-.6, elbow=20),
              dict(bob=4, lean=6, R={'a': (8.8, 57.0), 'fa': -4}, L={'a': (-12.4, 55.6), 'fa': 48}, armR=-1.5, armL=-1.3),
              dict(bob=4, lean=7, R={'a': (10.4, 56.6), 'fa': -8}, L={'a': (-14.0, 55.0), 'fa': 58}, armR=-1.7, armL=-1.5),
              dict(bob=3, lean=5, R={'a': (7.4, 57.2), 'fa': -4}, L={'a': (-10.6, 56.2), 'fa': 40}, armR=-1.2, armL=-1.0),
              dict(bob=3, lean=-1, R={'a': (6.6, 56.8), 'fa': -16}, L={'a': (-5.0, 57.0), 'fa': 22}, armR=.6, armL=.3),
              dict(bob=1, lean=0, R={'a': (2.4, 57.4)}, L={'a': (-1.2, 57.4)}, armR=.2, armL=.1)]
DODGE_FB = [dict(bob=3, R={'a': (-.8, 57), 'kx': -1.4}, L={'a': (.8, 57), 'kx': 1.4}, armR=-.6, armL=-.6, armOut=.8),
            dict(bob=3, R={'a': (0, 58.2), 'kf': .6}, L={'a': (.4, 54.2), 'toe': 1, 'back': 1}, armR=-1.2, armL=-1.2, armOut=1.6),
            dict(bob=3, R={'a': (0, 58.6), 'kf': .8}, L={'a': (.4, 53.4), 'toe': 1, 'back': 1}, armR=-1.4, armL=-1.4, armOut=2.0),
            dict(bob=2, R={'a': (0, 58.0), 'kf': .5}, L={'a': (.3, 54.8), 'toe': 1, 'back': 1}, armR=-1.0, armL=-1.0, armOut=1.4),
            dict(bob=2, R={'a': (-.6, 57.2), 'kx': -.8}, L={'a': (.6, 56.4), 'kx': .8}, armR=.4, armL=.4, armOut=.4),
            dict(bob=1, R={'a': (0, 57)}, L={'a': (0, 57)}, armR=.1, armL=.1)]

def cycle(key4):
    return [copy.deepcopy(f) for f in key4] + [sw(f) for f in key4]
def phase(i, n): return 2 * math.pi * i / n

def build(motion, view):
    """returns list of pose dicts (with lagged cape/hair) and per-frame ticks"""
    side = view in ('right', 'left')
    if motion == 'idle':
        P = [dict(copy.deepcopy(SIDE_IDLE if side else FB_IDLE), armR=0, armL=0)]; ticks = [60]; loop = True
    elif motion in ('walk', 'run'):
        P = cycle({'walk': WALK_SIDE if side else WALK_FB, 'run': RUN_SIDE if side else RUN_FB}[motion]); ticks = T[motion]['ticks']; loop = True
        for i, p in enumerate(P): p['bob'] = MO[motion]['bob'][i]; p['lean'] = MO[motion]['lean'] if side else 0
        if motion == 'run':
            for p in P: p['pump'] = 1.0; p['armBase'] = 8
    else:
        P = copy.deepcopy(DODGE_SIDE if side else DODGE_FB); ticks = G['timing']['dodge']['ticks']; loop = False
    n = len(P)
    # follow-through drivers (body state of THIS frame) -> applied to cape / hair of the NEXT frame
    drv = []
    for i, p in enumerate(P):
        ph = phase(i, n) if loop else i
        b = p.get('bob', 0); ln = p.get('lean', 0); s2 = math.sin(2 * ph) if loop else 0
        if motion == 'idle': d = dict(trail=1.0, lift=0, flut=0, sway=0, flare=0, hdx=-.3, stream=0)
        elif motion == 'walk': d = dict(trail=1.2 + .7 * s2, lift=.4 * (b < 0), flut=2 * ph, sway=.5 * math.cos(ph), flare=.3 * abs(s2), hdx=-.6 - .5 * s2, stream=.4)
        elif motion == 'run': d = dict(trail=4.2 + 1.0 * s2, lift=4.5 + 1.4 * s2, flut=2 * ph, sway=1.4 * math.cos(ph), flare=1.6 + .6 * s2, hdx=-1.4 - .6 * s2, stream=2.6 + .6 * s2)
        else:
            k = [.4, 1.0, 1.0, .8, .4, .1][i]
            d = dict(trail=1.2 + 6.0 * k, lift=7.0 * k, flut=i * 1.7, sway=0, flare=3.6 * k, hdx=-.4 - 2 * k, stream=3.5 * k)
        d['bob'] = b; drv.append(d)
    rest = dict(trail=1.0, lift=0, flut=0, sway=0, flare=0, hdx=-.3, stream=0, bob=0)
    for i, p in enumerate(P):
        d = drv[i - 1] if (loop or i > 0) else rest     # 1-frame lag
        if motion == 'idle': d = drv[0]
        p['cape'] = dict(trail=d['trail'], lift=d['lift'], flut=d['flut'], sway=d['sway'], flare=d['flare'])
        p['hair'] = dict(dx=d['hdx'], dy=(d['bob'] - p.get('bob', 0)) * .9)
        p['hairStream'] = d['stream']
        if view == 'back':   # moving away: the cape billows toward the viewer, legs: stepping leg is the FAR one
            for s in ('R', 'L'):
                if 'back' in p[s]: p[s]['back'] = 0; p[s]['_near'] = 1
                else: p[s]['back'] = 1 if p[s]['a'][1] < 57 or p[s].get('kf', 0) > .2 else 0
    return P, list(ticks), loop

def render(p, view):
    if view in ('right', 'left'): return render_side(p, view)
    return render_fb(p, 'front' if view == 'down' else 'back')
VIEWS = ('down', 'right', 'up', 'left')
def frames(motion, view):
    P, ticks, loop = build(motion, view); return [render(p, view).rgba() for p in P], ticks, loop, P
