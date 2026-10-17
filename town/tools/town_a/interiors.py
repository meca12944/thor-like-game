# [town_a] procedural interiors (art px, A=0.6). Each room: back wall (front-facing), side wall tops, floor, furniture.
import numpy as np, math
from px import *
from bld import stone_courses, planks, wall_plaster, draw_window, blotch
import props as PR

BW, SW, FW = 96, 22, 18   # back wall height, side wall width, front wall strip height
GAP = 54                  # exit gap width (art px)

class Room:
    def __init__(s, rw, rh, wall='plaster', floor='wood', seed=1):
        s.c = Canvas(rw, rh); s.rw, s.rh = rw, rh; s.blocks = []; s.spots = {}; s.seed = seed; c = s.c
        # floor
        fx0, fy0, fx1, fy1 = SW, BW, rw - SW, rh - FW
        if floor == 'wood':
            planks(c, fx0, fy0, fx1, fy1, P['wood'], seed, pw=8, vertical=False)
            R = rng(seed)
            y = fy0
            while y < fy1:  # board joints
                for k in range(3): c.vline(R.randint(fx0, fx1), y + 1, min(fy1, y + 8), P['wood'][1])
                y += 8
        elif floor == 'stone':
            stone_courses(c, fx0, fy0, fx1, fy1, P['stone_w'], seed, rowh=(12, 15), sw=(16, 26))
        elif floor == 'dirt':
            n = blotch(fy1 - fy0, fx1 - fx0, seed, 6, 1.6)
            for y in range(fy0, fy1):
                for x in range(fx0, fx1):
                    v = n[y - fy0, x - fx0]; c.a[y, x] = P['dirt'][2 + (v > .3) - (v < -.3)]
        elif floor == 'dojo':
            planks(c, fx0, fy0, fx1, fy1, P['wood'], seed, pw=10, vertical=True)
        # back wall
        if wall == 'plaster': wall_plaster(c, 0, 0, rw, BW, P['plaster'], seed, True, posts=tuple(range(90, rw - 60, 110)), braces=False, beam_mid=None)
        elif wall == 'stone': stone_courses(c, 0, 0, rw, BW, P['stone'], seed, rowh=(10, 13), sw=(14, 22))
        elif wall == 'wood': planks(c, 0, 0, rw, BW, P['wood_d'], seed, pw=9)
        elif wall == 'cellar': stone_courses(c, 0, 0, rw, BW, ramp('#262420', '#34302a', '#423d35', '#504a40', '#5e574b', '#6c6455'), seed, rowh=(10, 13), sw=(14, 22))
        # skirting + floor shadow under the wall
        c.rect(0, BW - 6, rw, BW, P['wood_d'][2]); c.hline(0, rw, BW - 6, P['wood_d'][4])
        m = np.zeros((rh, rw), bool); m[BW:BW + 8, :] = True; c.shade(m, .72)
        # side walls (seen from above: thick dark band) + front strip with the door gap
        top = P['wood_d'] if wall != 'stone' and wall != 'cellar' else P['stone']
        for x0 in (0, rw - SW):
            c.rect(x0, 0, x0 + SW, rh, top[2]); c.vline(x0 + (SW - 1 if x0 == 0 else 0), 0, rh, top[4])
        g0, g1 = rw // 2 - GAP // 2, rw // 2 + GAP // 2
        c.rect(0, rh - FW, g0, rh, top[2]); c.rect(g1, rh - FW, rw, rh, top[2]); c.hline(0, g0, rh - FW, top[4]); c.hline(g1, rw, rh - FW, top[4])
        c.rect(g0, rh - FW, g1, rh, P['stone'][3]); c.hline(g0, g1, rh - FW, P['stone'][5])   # threshold
        m[:] = False; m[BW:rh - FW, SW:SW + 6] = True; c.shade(m, .8); m[:] = False; m[BW:rh - FW, rw - SW - 6:rw - SW] = True; c.shade(m, .85)
        s.blocks += [(0, 0, rw, BW + 4), (0, 0, SW + 2, rh), (rw - SW - 2, 0, rw, rh), (0, rh - FW + 4, g0, rh), (g1, rh - FW + 4, rw, rh)]
        s.door = (rw // 2, rh - FW)
    def put(s, item, x, y, block=True, pad=0):
        """item = (Canvas, anchor(foot), ellipse) from props; x,y foot in room art px"""
        cv, (ax, ay) = item[0], item[1]
        s.c.blit(cv, x - ax, y - ay)
        if block:
            w, h = cv.w, cv.h
            if item[2]:
                ex, ey, rx, ry = item[2]
                s.blocks.append((x - rx - pad, y - (ay - ey) - ry - 4, x + rx + pad, y - (ay - ey) + ry))
            else: s.blocks.append((x - ax, y - 10, x - ax + w, y))
    def rect_block(s, x0, y0, x1, y1): s.blocks.append((x0, y0, x1, y1))
    def window(s, x, w=30, h=34): draw_window(s.c, x, 26, w, h, s.seed + x, box=False, shutters=None)

def counter(w=120, h=34, top=None):
    c = Canvas(w, h + 14); top = top or P['wood']
    c.rect(0, 0, w, 12, top[4]); c.hline(0, w, 0, top[5]); c.hline(0, w, 11, top[1])
    planks(c, 0, 12, w, h + 12, P['wood_d'], 3, pw=7); c.hline(0, w, h + 11, P['wood_d'][0])
    c.outline(); return c, (w // 2, h + 12), None

def shelf(w=90, h=80, goods='bottles', seed=1):
    c = Canvas(w, h); wd = P['wood']; R = rng(seed)
    c.rect(0, 0, w, h, wd[1]); c.rect(3, 3, w - 3, h - 2, wd[0])
    for y in range(4, h - 4, 19):
        c.rect(3, y + 15, w - 3, y + 18, wd[4]); c.hline(3, w - 3, y + 15, wd[5])
        x = 6
        while x < w - 10:
            if goods == 'bottles':
                col = R.choice([hexc('#d84a5a'), hexc('#4a90d8'), hexc('#5ac060'), hexc('#c890e0'), hexc('#f0c040')])
                c.rect(x, y + 6, x + 6, y + 15, col); c.rect(x + 2, y + 3, x + 4, y + 6, hexc('#c8b890')); c.put(x + 1, y + 7, hexc('#ffffff')); x += 9
            elif goods == 'cloth':
                pal = R.choice([P['cloth_red'], P['cloth_blue'], P['cloth_green'], P['cloth_purple'], P['cloth_cream']])
                c.rect(x, y + 4, x + 14, y + 15, pal[3]); c.hline(x, x + 14, y + 4, pal[5]); c.hline(x, x + 14, y + 9, pal[2]); x += 16
            elif goods == 'books':
                ww = R.randint(3, 5); col = R.choice([P['cloth_red'], P['cloth_blue'], P['cloth_green'], P['wood']])
                hh = R.randint(10, 13); c.rect(x, y + 15 - hh, x + ww, y + 15, col[3]); c.vline(x, y + 15 - hh, y + 15, col[5]); x += ww + 1
            elif goods == 'jars':
                c.ellipse(x + 5, y + 10, 5, 5, P['stone'][4]); c.rect(x + 2, y + 3, x + 8, y + 6, P['wood'][3]); x += 13
            else:
                col = P['iron']; c.rect(x, y + 2, x + 2, y + 15, col[4]); c.rect(x - 2, y + 11, x + 4, y + 13, P['gold'][3]); x += 8
    c.outline(); return c, (w // 2, h), (w // 2, h - 6, w // 2, 7)

def bed(seed=1, pal='cloth_blue'):
    c = Canvas(44, 70); wd = P['wood']; cl = P[pal]
    c.rect(0, 0, 44, 70, wd[2]); c.rect(0, 0, 44, 8, wd[4])
    c.rect(4, 8, 40, 22, P['cloth_cream'][4]); c.hline(4, 40, 21, P['cloth_cream'][2])
    c.rect(3, 24, 41, 66, cl[3]); c.hline(3, 41, 24, cl[5])
    for y in range(30, 66, 8): c.hline(3, 41, y, cl[2])
    c.outline(); return c, (22, 69), None

def table(w=56, seed=1, items=True):
    c = Canvas(w, 40); wd = P['wood']; R = rng(seed)
    c.rect(2, 4, w - 2, 22, wd[4]); c.hline(2, w - 2, 4, wd[5]); c.rect(2, 22, w - 2, 25, wd[1])
    for x in (4, w - 8): c.rect(x, 25, x + 4, 38, wd[2])
    if items:
        c.ellipse(14, 12, 6, 3, P['stone_w'][5]); c.rect(w - 20, 6, w - 14, 14, P['cloth_cream'][4]); c.rect(w // 2 - 2, 4, w // 2 + 2, 12, hexc('#f0e0a0')); c.put(w // 2, 3, hexc('#ffb040'))
    c.outline(); return c, (w // 2, 38), (w // 2, 30, w // 2 - 2, 9)

def chair():
    c = Canvas(18, 30); wd = P['wood']
    c.rect(2, 0, 16, 14, wd[3]); c.rect(1, 14, 17, 19, wd[4]); c.rect(2, 19, 4, 29, wd[2]); c.rect(14, 19, 16, 29, wd[2])
    c.outline(); return c, (9, 29), (9, 25, 8, 4)

def fireplace(w=70):
    c = Canvas(w, 80)
    stone_courses(c, 0, 0, w, 80, P['stone'], 5, rowh=(7, 9), sw=(9, 14))
    c.rect(14, 34, w - 14, 78, hexc('#1a1008'))
    for i in range(60):
        R = rng(i); x = R.randint(18, w - 18); y = R.randint(54, 76); c.put(x, y, R.choice([hexc('#ff9a2a'), hexc('#ffd24a'), hexc('#e0501a')]))
    c.ellipse(w // 2, 70, 14, 6, hexc('#ff8a20')); c.ellipse(w // 2, 68, 8, 4, hexc('#ffe070'))
    c.rect(-2, 28, w + 2, 34, P['wood'][3]); c.hline(0, w, 28, P['wood'][5])
    c.outline(); return c, (w // 2, 79), None

def rug(w=100, h=50, pal='cloth_red'):
    c = Canvas(w, h); cl = P[pal]
    c.rect(0, 0, w, h, cl[2]); c.rect(4, 4, w - 4, h - 4, cl[3]); c.rect(10, 10, w - 10, h - 10, cl[2])
    for x in range(0, w, 4): c.put(x, 0, P['cloth_cream'][4]); c.put(x, h - 1, P['cloth_cream'][4])
    c.ellipse(w // 2, h // 2, w // 6, h // 6, P['gold'][3])
    return c, (w // 2, h), None

def forge(w=90):
    c = Canvas(w, 100)
    stone_courses(c, 6, 0, w - 6, 60, P['stone'], 9, rowh=(6, 8), sw=(8, 12))
    stone_courses(c, 0, 56, w, 98, P['stone'], 10, rowh=(6, 8), sw=(8, 12))
    c.rect(18, 62, w - 18, 84, hexc('#2a1006'))
    for i in range(140):
        R = rng(i + 7); c.put(R.randint(20, w - 20), R.randint(66, 83), R.choice([hexc('#ff6a10'), hexc('#ffb02a'), hexc('#ffe46a'), hexc('#c02a08')]))
    c.rect(-2, 52, w + 2, 58, P['stone'][4])
    c.outline(); return c, (w // 2, 98), None

def mannequin(pal='cloth_purple'):
    c = Canvas(26, 62); cl = P[pal]
    c.rect(12, 44, 14, 58, P['wood'][2]); c.rect(6, 57, 20, 61, P['wood'][3])
    c.ellipse(13, 6, 5, 5, P['cloth_cream'][4])
    c.poly([(5, 12), (21, 12), (19, 30), (24, 46), (2, 46), (7, 30)], cl[3]); c.vline(13, 12, 46, cl[2]); c.hline(5, 21, 12, cl[5])
    c.outline(); return c, (13, 61), (13, 58, 9, 4)

def mirror():
    c = Canvas(30, 56); c.rect(0, 0, 30, 56, P['gold'][2]); c.rect(3, 3, 27, 50, P['glass'][3])
    for k in range(18): c.put(6 + k, 44 - k * 2, P['glass'][5]) if 44 - k * 2 > 4 else None
    c.rect(8, 50, 22, 56, P['wood'][2]); c.outline(); return c, (15, 55), (15, 52, 13, 4)

def scroll_banner(text_col='cloth_cream'):
    c = Canvas(22, 60); cl = P[text_col]
    c.rect(0, 0, 22, 4, P['wood'][2]); c.rect(2, 4, 20, 54, cl[4]); c.rect(0, 54, 22, 58, P['wood'][2])
    for y in range(10, 50, 6): c.rect(9, y, 13, y + 4, OUT)
    c.outline(); return c, (11, 58), None

def trapdoor(open_=False):
    c = Canvas(40, 30); wd = P['wood_d']
    c.rect(0, 0, 40, 30, P['iron'][1])
    if open_: c.rect(3, 3, 37, 27, hexc('#0a0806')); [c.hline(10, 30, y, wd[3]) for y in range(6, 27, 5)]
    else: planks(c, 3, 3, 37, 27, wd, 4, pw=6); c.rect(17, 12, 23, 16, P['iron'][4])
    return c, (20, 30), None

def ladder():
    c = Canvas(30, 70); wd = P['wood']
    c.rect(3, 0, 7, 70, wd[3]); c.rect(23, 0, 27, 70, wd[3])
    for y in range(6, 70, 10): c.rect(7, y, 23, y + 3, wd[4])
    c.outline(); return c, (15, 69), None

def strongbox():
    c = Canvas(40, 30); ir = P['iron']
    c.rect(0, 4, 40, 28, ir[2]); c.rect(0, 2, 40, 9, ir[3]); c.hline(0, 40, 2, ir[5])
    for x in (5, 33): c.rect(x, 2, x + 3, 28, P['gold'][3])
    c.rect(17, 12, 23, 20, P['gold'][4]); c.put(20, 16, OUT)
    c.outline(); return c, (20, 29), (20, 24, 19, 6)

def cracked_wall_patch(w=60, h=70):
    c = Canvas(w, h); R = rng(5)
    for k in range(4):
        x, y = w // 2 + R.randint(-6, 6), 6
        while y < h - 4:
            c.put(x, y, hexc('#0c0a08')); c.put(x + 1, y, hexc('#2a2620')); x += R.choice([-1, 0, 1]); y += 1
    return c, (w // 2, h), None

def cradle():
    c = Canvas(44, 34); hy = P['hay']
    c.ellipse(22, 14, 21, 8, hy[1])
    for y in range(14, 32):
        for x in range(2, 42):
            if ((x - 22) / 20) ** 2 + ((y - 14) / 18) ** 2 < 1: c.put(x, y, hy[3 if (x + y) % 4 < 2 else 2])
    c.ellipse(22, 14, 18, 6, P['cloth_blue'][4]); c.ellipse(16, 12, 6, 3, P['cloth_cream'][5])
    c.outline(); return c, (22, 33), (22, 28, 20, 6)

def mat(w=120, h=80):
    c = Canvas(w, h); cl = ramp('#6a7a3c', '#7d8c48', '#909e54', '#a2ae62', '#b4be72', '#c6ce86')
    c.rect(0, 0, w, h, P['cloth_blue'][1]); c.rect(3, 3, w - 3, h - 3, cl[3])
    for x in range(6, w - 4, 4): c.vline(x, 3, h - 3, cl[2])
    return c, (w // 2, h), None
