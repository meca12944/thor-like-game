"""hero_v3_build.py - builds every hero v3 deliverable from the hand-built rig:
turnaround check (+guides, x4), walk / run / dodge frames (1x strips + json), sheets (x4), GIFs (x2, true game speed),
60 fps MP4s (every game tick rendered), uniqueness + proportion checks, female silhouette comparison.
Run from style_sample/hero_v3:  python3 tools/hero_v3_build.py"""
import sys, os, json, math, subprocess, shutil, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hero_v3_motion import *
from PIL import Image, ImageDraw, ImageFont
FB = ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf', 14)
FS = ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf', 11)
FM = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 11)
OUTD = os.getcwd(); os.makedirs('frames', exist_ok=True)
BG = (64, 88, 64); ROWS = B['rows']
GUIDES = [('crown', 0), ('eye', 8), ('chin', 14), ('shoulder', 14), ('waist', 29), ('crotch', 37), ('knee', 48), ('sole', 60)]
DIRN = {'down': 'down (front)', 'right': 'right (side)', 'up': 'up (back)', 'left': 'left (side, native)'}

def measure(c, view):
    """rows measured from the final pixels / part map of one rendered frame (guide-row units)"""
    a = c.z > -99; ys = np.where(a.any(1))[0]; m = {}
    m['crown'] = int(ys.min() - TOP); m['sole'] = int(ys.max() + 1 - TOP); m['height'] = m['sole'] - m['crown']
    eye = np.all(c.rgb == EYE, -1); m['eye'] = int(np.where(eye.any(1))[0].mean() - TOP) if eye.any() else None
    face = c.meas['face']; m['chin'] = int(np.where(face.any(1))[0].max() + 1 - TOP)
    body = np.isin(c.grp, [GR['torso'], GR['arm'], GR['arm2'], GR['paul']]) & a
    wid = np.array([(np.ptp(np.where(r)[0]) + 1) if r.any() else 0 for r in body])
    arm = c.meas['armR' if view in ('down', 'up', 'right') else 'armL']; m['shoulder'] = int(np.where(arm.any(1))[0].min() - TOP); m['shoulderW'] = int(wid[:TOP + 25].max())   # shoulder line = top of the deltoid (near arm, its full drawn mask incl. the part under the pauldron)
    m['waist'] = int(c.meas['belt']); pel = c.meas['pelvis']; m['crotch'] = int(np.where(pel.any(1))[0].max() + 1 - TOP)
    ks = [v[1] for k, v in c.anch.items() if k.startswith('knee')]; m['knee'] = int(round(max(ks)))
    hw = face & True; m['headW'] = int(max((np.ptp(np.where(r)[0]) + 1) for r in (np.isin(c.grp, [GR['head'], GR['hair']]) & a)[TOP:TOP + 12] if r.any()))
    return m

def tile(rgba, k, bg=BG):
    im = Image.fromarray(rgba, 'RGBA'); b = Image.new('RGBA', im.size, bg + (255,)); b.alpha_composite(im)
    return b.convert('RGB').resize((im.width * k, im.height * k), Image.NEAREST)

# ------------------------------------------------------------------ STEP 1 turnaround
def turnaround():
    cs = {}; ms = {}
    for v in VIEWS:
        P, _, _ = build('idle', v); c = render(P[0], v); cs[v] = c; ms[v] = measure(c, v)
        Image.fromarray(c.rgba(), 'RGBA').save(f'frames/hero_v3_idle_{v}.png')
    keys = ['crown', 'eye', 'chin', 'shoulder', 'waist', 'crotch', 'knee', 'sole', 'height', 'headW', 'shoulderW']
    with open('hero_v3_turnaround_measure.csv', 'w') as f:
        f.write('direction,' + ','.join(keys) + '\n')
        for v in VIEWS: f.write(v + ',' + ','.join('' if ms[v][k] is None else str(ms[v][k]) for k in keys) + '\n')
    def sheet(K, name, table=True):
        W = max(150 + 4 * (CW * K + 30), 1180); H = 40 + CH * K + (200 if table else 30)
        img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img); y0 = 34
        d.text((10, 8), f'Hero v3 turnaround (hand-built rig, 1 guide grid for all directions)  60 px tall on 768x432,  x{K} nearest', font=FB, fill='white')
        for i, v in enumerate(VIEWS):
            x = 150 + i * (CW * K + 30); img.paste(tile(cs[v].rgba(), K), (x, y0)); d.text((x + 8, y0 + CH * K + 4), DIRN[v], font=FB, fill='white')
        rows = {}
        for nm, r in GUIDES: rows.setdefault(r, []).append(nm)
        for r, nms in rows.items():
            yy = y0 + (r + TOP) * K; col = (255, 230, 90) if r in (0, 60) else (255, 120, 120) if r in (14, 37) else (140, 220, 255)
            for x in range(140, W - 6, 6): d.line([(x, yy), (x + 3, yy)], fill=col)
            d.text((6, yy - 7), f'{r:>2} ' + ' / '.join(nms), font=FS, fill=col)
        if table:
            ty = y0 + CH * K + 26; d.text((10, ty), 'measured from the rendered pixels (row = guide row; shoulder = top of the deltoid; headW incl. hair; shoulderW incl. pauldron, side = profile depth):', font=FS, fill='white')
            hdr = f"{'direction':<20}" + ''.join(f'{k:>10}' for k in keys); d.text((10, ty + 18), hdr, font=FM, fill=(255, 240, 180))
            for i, v in enumerate(VIEWS):
                d.text((10, ty + 34 + i * 15), f'{DIRN[v]:<20}' + ''.join(f"{('-' if ms[v][k] is None else ms[v][k]):>10}" for k in keys), font=FM, fill='white')
            ok = all(max(ms[v][k] for v in VIEWS if ms[v][k] is not None) - min(ms[v][k] for v in VIEWS if ms[v][k] is not None) <= 1 for k in keys[:9])
            d.text((10, ty + 34 + 4 * 15 + 6), ('PASS' if ok else 'FAIL') + ': crown/eye/chin/shoulder/waist/crotch/knee/sole/height agree within 1 px across the 4 directions (eye hidden in back view; widths differ by design: profile vs front)', font=FS, fill=(140, 255, 140) if ok else (255, 100, 100))
        img.save(name); return img
    sheet(6, 'hero_v3_turnaround_check.png'); sheet(4, 'hero_v3_turnaround_check_4x.png')
    return ms

# ------------------------------------------------------------------ frames + checks
def motion_frames(mot):
    out = {}
    for v in VIEWS:
        P, ticks, loop = build(mot, v); cs = [render(p, v) for p in P]; out[v] = (cs, ticks, loop, P)
    return out
def uniq_check(mot, data):
    res = {}
    for v, (cs, ticks, loop, P) in data.items():
        fr = [c.rgba().astype(int) for c in cs]; n = len(fr); mind = 10 ** 9; pair = None
        for i in range(n):
            for j in range(i + 1, n):
                dd = int((np.abs(fr[i] - fr[j]).sum(-1) > 0).sum())
                if dd < mind: mind, pair = dd, (i, j)
        res[v] = dict(frames=n, allDistinct=mind > 0, minDiffPx=mind, closestPair=pair)
    return res
def prop_check(mot, data):
    """every frame: rows vs the guides after removing the frame's own intentional bob"""
    rows = []
    for v, (cs, ticks, loop, P) in data.items():
        for i, (c, p) in enumerate(zip(cs, P)):
            m = measure(c, v); b = p.get('bob', 0)
            rows.append(dict(dir=v, frame=i, bob=b, lean=p.get('lean', 0), crown=m['crown'], eye=m['eye'], chin=m['chin'], waist=m['waist'], crotch=m['crotch'], sole=m['sole'],
                             headDev=max(abs(m['crown'] - b), abs(m['chin'] - 14 - b), abs((m['eye'] if m['eye'] is not None else 8 + b) - 8 - b)), crotchDev=abs(m['crotch'] - 37 - b)))
    return rows
def save_strip(mot, data):
    meta = {'motion': mot, 'grid': '768x432 (x0.5 for the 384x216 live view)', 'canvas': [CW, CH], 'anchorPx': [CX, TOP + 60], 'anchorDoc': 'feet anchor = (canvasCenterX, sole row) in canvas px', 'tickHz': 60, 'dirs': {}}
    for v, (cs, ticks, loop, P) in data.items():
        strip = np.concatenate([c.rgba() for c in cs], 1); Image.fromarray(strip, 'RGBA').save(f'frames/hero_v3_{mot}_{v}.png')
        parts = np.concatenate([np.where(c.z > -99, c.grp, 0).astype(np.uint8) for c in cs], 1); Image.fromarray(parts, 'L').save(f'frames/hero_v3_{mot}_{v}_parts.png')
        meta['dirs'][v] = dict(file=f'hero_v3_{mot}_{v}.png', parts=f'hero_v3_{mot}_{v}_parts.png', n=len(cs), ticks=ticks, loop=loop,
                               frames=[dict(bob=p.get('bob', 0), lean=p.get('lean', 0), anchors={k: [round(x + CX, 2), round(y + TOP, 2)] for k, (x, y) in c.anch.items()}) for c, p in zip(cs, P)])
    json.dump(meta, open(f'frames/hero_v3_{mot}.json', 'w'), indent=1)
def mot_sheet(mot, data, K=4, title=''):
    n = max(len(d[0]) for d in data.values()); W = 170 + n * (CW * K + 8); H = 40 + 4 * (CH * K + 24)
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img); d.text((10, 8), title, font=FB, fill='white')
    names = MO[mot]['poses']
    for r, v in enumerate(VIEWS):
        cs, ticks, loop, P = data[v]; y = 36 + r * (CH * K + 24); d.text((8, y + CH * K // 2), DIRN[v], font=FB, fill='white')
        for i, c in enumerate(cs):
            x = 170 + i * (CW * K + 8); img.paste(tile(c.rgba(), K), (x, y))
            d.text((x + 4, y + CH * K + 3), f'{i} {names[i]}  {ticks[i]}t  bob{P[i].get("bob", 0):+d}', font=FS, fill=(230, 230, 230))
        for g in (0, 60):
            yy = y + (g + TOP) * K; d.line([(170, yy), (W - 6, yy)], fill=(255, 230, 90))
    img.save(f'hero_v3_{mot}_sheet.png')

# ------------------------------------------------------------------ playback at true game speed
WS = T['walkSpeedWorldPxPerS'] * G['grid']['worldToGrid']          # grid px / s at walk
def anim_rate(mot): return 1.0 if mot == 'walk' else T['runMul'] * T['runStride']   # anim ticks per real tick
def speed(mot): return WS * (1 if mot == 'walk' else T['runMul'])
def gif_delays(mot, n_ticks):
    """real hold (ticks) of each frame at the gait's own speed -> ms, rounded to 10 ms with error diffusion (exact cycle)"""
    r = anim_rate(mot); hold = [t / r * 1000 / 60 for t in n_ticks]; out = []; acc = 0.0; done = 0
    for h in hold: acc += h; ms = int(round(acc / 10.0) * 10) - done; ms = max(ms, 20); out.append(ms); done += ms
    return out, sum(hold)
def dodge_real_ticks():
    tt = G['timing']['dodge']['ticks']; dash = G['timing'].get('dashTicks', 13); rec = G['timing'].get('dashRecTicks', 6)
    ends = np.cumsum(tt[:-1]) * dash / sum(tt[:-1]); hold = list(np.diff(np.concatenate([[0], ends]))) + [rec]; return hold
def dodge_dist(t):   # grid px travelled after t real ticks (FEEL.dashSpeed 820, eased)
    T13 = 13 / 60.; s = 0; n = 200
    for k in range(n):
        tt = min(t / 60., T13) * (k + .5) / n; p = tt / T13; s += (820 * (1 - p) ** 2 * 1.5 + 90) * min(t / 60., T13) / n
    return s * G['grid']['worldToGrid']

PW, PH = 76, 80   # preview panel (1x)
def ground(off, view, k=1):
    """scrolling ground under the panel: tile lines every 32 grid px (= 16 live px tile) + small marks every 8"""
    im = np.zeros((PH, PW, 3), np.uint8); im[:] = (64, 88, 64); gy = 60 + TOP + 6
    im[gy - 8:, :] = (74, 98, 70)
    if view in ('right', 'left'):
        sg = -1 if view == 'right' else 1
        for x in range(-40, PW + 40):
            wx = x - sg * off
            if int(math.floor(wx)) % 32 == 0: im[gy - 8:, x if 0 <= x < PW else 0] = (54, 76, 54) if 0 <= x < PW else im[gy - 8:, 0]
            elif int(math.floor(wx)) % 8 == 0 and 0 <= x < PW: im[gy - 5:gy - 3, x] = (88, 112, 82)
    else:
        sg = -1 if view == 'down' else 1
        for y in range(PH):
            wy = y - sg * off
            if int(math.floor(wy)) % 32 == 0: im[y, :8] = (54, 76, 54); im[y, -8:] = (54, 76, 54)
            elif int(math.floor(wy)) % 8 == 0: im[y, 2:5] = (88, 112, 82); im[y, -5:-2] = (88, 112, 82)
    return im
def blit(dst, rgba, x, y, alpha=1.0, tint=None):
    h, w = rgba.shape[:2]; x0, y0 = max(0, x), max(0, y); x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0: return
    s = rgba[y0 - y:y1 - y, x0 - x:x1 - x].astype(float); a = s[..., 3:4] / 255 * alpha; col = s[..., :3]
    if tint is not None: col = col * .35 + np.array(tint) * .65
    dst[y0:y1, x0:x1] = (dst[y0:y1, x0:x1] * (1 - a) + col * a).astype(np.uint8)
DIRV = {'down': (0, 1), 'up': (0, -1), 'right': (1, 0), 'left': (-1, 0)}
def panel(view, sprite, dist, ghosts=()):
    im = ground(dist, view); ox = (PW - CW) // 2; oy = PH - CH - 4
    for gs, gd, ga in ghosts:   # afterimages (sky-blue, fading), placed where the body was gd px ago
        dx, dy = DIRV[view]; blit(im, gs, int(round(ox - dx * gd)), int(round(oy - dy * gd * .8)), ga, tint=(120, 200, 255))
    blit(im, sprite, ox, oy); return im
def write_mp4(frames, name, k=2):
    h, w = frames[0].shape[:2]
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', '60', '-i', '-',
                          '-vf', f'scale={w * k}:{h * k}:flags=neighbor', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', '-r', '60', name], stdin=subprocess.PIPE)
    for f in frames: p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close(); p.wait()
def label_row(img_np, texts, k):
    im = Image.fromarray(img_np).resize((img_np.shape[1] * k, img_np.shape[0] * k), Image.NEAREST); d = ImageDraw.Draw(im)
    for i, t in enumerate(texts): d.text((i * PW * k + 4, 3), t, font=FS, fill='white')
    return im

class Sim:
    """per-tick simulation exactly like the game: anim ticks advance by speed/walkSpeed (x runStride when running)"""
    def __init__(s, data): s.data = data; s.at = 0.0; s.dist = 0.0; s.hist = []
    def gait_frame(s, mot, ph_frames):
        cs = {v: s.data[mot][v][0] for v in VIEWS}; return {v: cs[v][int(ph_frames) % 8].rgba() for v in VIEWS}

def gait_preview(mot, data):
    r = anim_rate(mot); tpf = T[mot]['ticks'][0]; v = speed(mot)
    cyc_real = T[mot]['cycleTicks'] / r; nt = int(round(cyc_real * 4))   # 4 cycles of real ticks
    frames = []; at = 0.0; dist = 0.0
    for t in range(nt):
        fi = int(at // tpf) % 8
        row = np.concatenate([panel(vw, data[vw][0][fi].rgba(), dist) for vw in VIEWS], 1); frames.append(row)
        at += r; dist += v / 60
    write_mp4(frames, f'hero_v3_{mot}_60fps.mp4')
    # GIF: one cycle, per-frame delays at true speed
    delays, total = gif_delays(mot, T[mot]['ticks']); g = []; dist = 0
    for i in range(8):
        row = np.concatenate([panel(vw, data[vw][0][i].rgba(), dist) for vw in VIEWS], 1)
        g.append(label_row(row, [DIRN[vw] for vw in VIEWS], 2)); dist += v * delays[i] / 1000
    g[0].save(f'hero_v3_{mot}.gif', save_all=True, append_images=g[1:], duration=delays, loop=0, disposal=1)
    return delays, total
def ghost_list(hist, t):
    """game-like trail: a ghost every 2 ticks during the dash, fading over 0.24 s (14 ticks); keep the 3 newest"""
    out = []
    for (tt, spr, d) in hist:
        age = t - tt
        if 0 < age <= 14 and tt % 2 == 0: out.append((spr, d, .55 * (1 - age / 14)))
    return out[-3:]
def dodge_preview(data):
    hold = dodge_real_ticks(); ends = np.cumsum(hold); N = int(round(ends[-1])) + 14
    frames = []; hist = {vw: [] for vw in VIEWS}; gifs = []
    for t in range(N):
        fi = int(np.searchsorted(ends, t + .5)) if t < ends[-1] else 5; fi = min(fi, 5)
        d = dodge_dist(min(t, 13)); row = []
        for vw in VIEWS:
            spr = data[vw][0][fi].rgba()
            if t < 13: hist[vw].append((t, spr, d))
            gh = [(s, d - dd, a) for (s, dd, a) in ghost_list(hist[vw], t)]
            row.append(panel(vw, spr, d, gh))
        frames.append(np.concatenate(row, 1))
    write_mp4(frames, 'hero_v3_dodge_60fps.mp4')
    # GIF: each tick-frame merged into holds of >=20 ms (pairs of ticks), exact total
    g = []; dl = []
    for i in range(0, len(frames), 2):
        g.append(label_row(frames[i], [DIRN[vw] for vw in VIEWS], 2)); dl.append(30 if (i // 2) % 3 == 0 else 40)
    # 2 ticks = 33.3 ms -> alternate 30/40/30 (exact 100 ms per 6 ticks)
    dl = [30 if k % 3 != 2 else 40 for k in range(len(g))]; dl[-1] += 400
    g[0].save('hero_v3_dodge.gif', save_all=True, append_images=g[1:], duration=dl, loop=0, disposal=1)
    return hold, frames
def combined(data):
    """walk 2 s -> run start (10 ticks accel) -> run 2 s -> back to walk 0.5 s -> dodge -> idle; phase-continuous gait"""
    seq = []; ph = 0.0; dist = 0.0; t = 0
    def emit(sprs, gh=None):
        seq.append(np.concatenate([panel(vw, sprs[vw], dist, (gh or {}).get(vw, ())) for vw in VIEWS], 1))
    plan = [('walk', 120), ('w2r', 10), ('run', 120), ('r2w', 12), ('walk', 30)]
    for mode, n in plan:
        for k in range(n):
            if mode == 'walk': v = WS; mot = 'walk'
            elif mode == 'run': v = WS * T['runMul']; mot = 'run'
            elif mode == 'w2r': v = WS * (1 + (T['runMul'] - 1) * (k + 1) / n); mot = 'run'
            else: v = WS * (T['runMul'] - (T['runMul'] - 1) * (k + 1) / n); mot = 'walk'
            # ph = cycle phase in frames (0..8); advances by distance / (cycle distance of the current gait) * 8
            cycd = speed(mot) * (T[mot]['cycleTicks'] / anim_rate(mot)) / 60
            emit({vw: data[mot][vw][0][int(ph) % 8].rgba() for vw in VIEWS})
            ph += v / 60 / cycd * 8; dist += v / 60
    hold = dodge_real_ticks(); ends = np.cumsum(hold); hist = {vw: [] for vw in VIEWS}; d0 = dist
    for tt in range(int(round(ends[-1]))):
        fi = min(5, int(np.searchsorted(ends, tt + .5))); dist = d0 + dodge_dist(min(tt, 13)); gh = {}
        for vw in VIEWS:
            spr = data['dodge'][vw][0][fi].rgba()
            if tt < 13: hist[vw].append((tt, spr, dist))
            gh[vw] = [(s, dist - dd, a) for (s, dd, a) in ghost_list(hist[vw], tt)]
        emit({vw: data['dodge'][vw][0][fi].rgba() for vw in VIEWS}, gh)
    idle = {vw: render(build('idle', vw)[0][0], vw).rgba() for vw in VIEWS}
    for k in range(40): emit(idle)
    write_mp4(seq, 'hero_v3_walk_run_60fps.mp4'); return len(seq)

# ------------------------------------------------------------------ female silhouette on the same grid
def female_cmp(ms):
    fb = G['bodies']['female']; r = fb['rows']; hw = fb['halfWidths']; K = 6
    def fem(view):
        c = Canvas(); F1 = ((200, 110, 170),) * 2 + ((150, 70, 125),); F2 = ((150, 70, 125),) * 2 + ((120, 50, 100),); HR = ((90, 40, 80),) * 3
        if view == 'side':
            c.paint(c.poly([(-4.8, 3), (-.6, 2), (-1.0, 26), (-5.6, 27)]), HR, 5, 7)
            c.paint(c.seg((-.2, 35), (-.6, 48), 2.6, 2.1) | c.seg((-.6, 48), (-.8, 57.4), 2.0, 1.7) | c.poly([(-2.6, 57), (2.8, 58.4), (2.8, 59.4), (-2.8, 59.4)]), F2, 10, 2)
            c.paint(c.seg((.4, 35), (.8, 48), 2.7, 2.2) | c.seg((.8, 48), (.8, 57.4), 2.1, 1.8) | c.poly([(-1.4, 57), (4.4, 58.4), (4.4, 59.4), (-1.6, 59.4)]), F1, 20, 1)
            c.paint(c.poly([(-2.6, 14), (3.0, 14), (4.6, 18), (4.8, 21.5), (3.0, 25.5), (2.4, 29), (3.6, 33), (3.0, 36.6), (-3.4, 36.6), (-4.4, 33), (-3.0, 29), (-3.4, 22), (-3.2, 16)]), F1, 30, 3)
            c.paint(c.seg((-.2, 17), (.2, 26), 1.9, 1.7) | c.seg((.2, 26), (.8, 33), 1.7, 1.5), F1, 40, 4)
            c.paint(c.ell(-4.6, r['crown'], 4.6, r['chin'] + 1), F1, 45, 6)
            c.paint(c.poly([(-4.8, r['crown'] + .5), (2.4, r['crown']), (4.4, 4.5), (1, 5), (-.2, 13), (-4.8, 12)]), HR, 46, 7)
        else:
            c.paint(c.poly([(-5.6, 5), (5.6, 5), (6.4, 25), (-6.4, 25)]), HR, 5, 7)
            for k, sg in enumerate((-1, 1)):
                c.paint(c.seg((sg * 3.4, 35), (sg * 3.1, 48), 2.6, 2.1) | c.seg((sg * 3.1, 48), (sg * 3.0, 57.4), 2.0, 1.7) | c.ell(sg * 3.0 - 2.1, 56.8, sg * 3.0 + 2.1, 60), F1, 10 + k, 1 + k)
                c.paint(c.seg((sg * 6.2, 17), (sg * 7.4, 26), 1.9, 1.7) | c.seg((sg * 7.4, 26), (sg * 7.8, 33), 1.7, 1.5) | c.ell(sg * 7.8 - 1.4, 32.4, sg * 7.8 + 1.4, 36), F1, 40, 4 + k)
            c.paint(c.poly([(-hw['shoulder'], 15.5), (hw['shoulder'], 15.5), (hw['chest'], 21), (hw['waist'], r['waist']), (hw['hip'], 33), (hw['hip'] - .4, 36.6), (-hw['hip'] + .4, 36.6), (-hw['hip'], 33), (-hw['waist'], r['waist']), (-hw['chest'], 21)]), F1, 30, 3)
            c.paint(c.poly([(-1.6, 12.5), (1.6, 12.5), (1.6, 15.5), (-1.6, 15.5)]), F1, 31, 3)
            c.paint(c.ell(-hw['head'], r['crown'], hw['head'], r['chin'] + .5), F1, 45, 6)
            c.paint(c.ell(-hw['head'] - .6, r['crown'] - .2, hw['head'] + .6, r['crown'] + 7) & (np.arange(CH)[:, None] < TOP + r['crown'] + 5), HR, 46, 7)
        c.outline(sep_groups=(1, 2, 3, 4, 5, 6, 7)); return c.rgba(), None
    ref = Image.open(os.path.join(REPO_DOCS, 'outfits_v3', 'a_tailor.png')).convert('RGBA'); bb = ref.getbbox(); ref = ref.crop(bb)
    # the reference body (crown->sole, hair bunches excluded) scaled to the female grid height (58 px) x K
    hpx = (60 - r['crown']) * K; ref = ref.resize((int(ref.width * hpx / ref.height), hpx), Image.LANCZOS)
    items = [('hero down', cs_idle['down'].rgba()), ('hero right', cs_idle['right'].rgba()), ('female front (silhouette)', fem('front')[0]), ('female side (silhouette)', fem('side')[0])]
    W = 150 + 4 * (CW * K + 24) + ref.width + 40; H = 40 + CH * K + 120; img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img); y0 = 34
    d.text((10, 8), 'Shared guide grid: hero (male) vs heroine (female) - same crotch / knee / sole, female 2 px shorter at the crown, narrower shoulders + waist', font=FB, fill='white')
    for i, (nm, rg) in enumerate(items):
        x = 150 + i * (CW * K + 24); img.paste(tile(rg, K), (x, y0)); d.text((x + 4, y0 + CH * K + 4), nm, font=FB, fill='white')
    xr = 150 + 4 * (CW * K + 24) + 10; img.paste(ref, (xr, y0 + (r['crown'] + TOP) * K), ref); d.text((xr, y0 + CH * K + 4), 'a_tailor.png ref (scaled)', font=FB, fill='white')
    for nm, rr in GUIDES:
        yy = y0 + (rr + TOP) * K; col = (255, 230, 90) if nm in ('crown', 'sole') else (255, 120, 120) if nm in ('chin', 'crotch') else (140, 220, 255)
        for x in range(140, W - 6, 6): d.line([(x, yy), (x + 3, yy)], fill=col)
        d.text((6, yy - 7), f'{rr:>2} {nm} (M)', font=FS, fill=col)
    yy = y0 + (r['crown'] + TOP) * K
    for x in range(140, W - 6, 4): d.point((x, yy), fill=(255, 140, 220))
    d.text((6, yy + 2), f' {r["crown"]} crown (F)', font=FS, fill=(255, 140, 220))
    ty = y0 + CH * K + 30
    d.text((10, ty), 'male:   ' + json.dumps(B['rows']) + '   shoulderW 19-20', font=FM, fill='white')
    d.text((10, ty + 16), 'female: ' + json.dumps(r) + f'   shoulderW {int(hw["shoulder"] * 2)}', font=FM, fill='white')
    d.text((10, ty + 34), 'source of truth: hero_v3_guides.json  bodies.male / bodies.female (every heroine reuses the rig + timing; only these rows/widths differ)', font=FS, fill=(255, 240, 180))
    img.save('hero_v3_vs_female_silhouette.png')

REPO_DOCS = os.environ.get('DOCS_ART', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'docs_art'))
if __name__ == '__main__':
    ms = turnaround()
    cs_idle = {v: render(build('idle', v)[0][0], v) for v in VIEWS}
    data = {m: motion_frames(m) for m in ('walk', 'run', 'dodge')}
    report = {'turnaround': ms, 'uniq': {}, 'prop': {}, 'timing': {}}
    for m in ('walk', 'run', 'dodge'):
        save_strip(m, data[m]); report['uniq'][m] = uniq_check(m, data[m]); pr = prop_check(m, data[m])
        report['prop'][m] = dict(maxHeadDev=max(r['headDev'] for r in pr), maxCrotchDev=max(r['crotchDev'] for r in pr), rows=pr)
    mot_sheet('walk', data['walk'], title='hero v3 WALK - 8 frames x 4 dirs, x4.  contact / down / passing / up (R) then (L).  3 ticks each @60fps = 24-tick cycle')
    mot_sheet('run', data['run'], title='hero v3 RUN - 8 frames x 4 dirs, x4.  contact / down / push / float.  3 anim ticks each (distance-synced, 1.045 anim tick per game tick at full run)')
    mot_sheet('dodge', data['dodge'], title='hero v3 DODGE (회피 잔상 대시) - 6 frames x 4 dirs, x4.  ticks 2,3,3,3,4,6 as dash_* in hero_anim.src.json')
    for m in ('walk', 'run'):
        dl, tot = gait_preview(m, data[m]); report['timing'][m] = dict(animTicks=T[m]['ticks'], animRatePerGameTick=anim_rate(m), realHoldTicks=[round(t / anim_rate(m), 3) for t in T[m]['ticks']], gifDelaysMs=dl, cycleMsExact=round(tot, 2), cycleMsGif=sum(dl), speedGridPxPerS=round(speed(m), 2), cycleDistGridPx=round(speed(m) * tot / 1000, 2))
    hold, _ = dodge_preview(data['dodge']); report['timing']['dodge'] = dict(animTicks=G['timing']['dodge']['ticks'], realHoldTicks=[round(h, 3) for h in hold], totalRealTicks=round(sum(hold), 2), travelGridPx=round(dodge_dist(13), 1))
    slide = {}
    for m, tab, n in (('walk', WALK_SIDE, 4), ('run', RUN_SIDE, 3)):
        xs = [tab[i]['R']['a'][0] for i in range(n)]; drawn = (xs[0] - xs[-1]) / (n - 1)
        need = speed(m) * (T[m]['ticks'][0] / anim_rate(m)) / 60
        slide[m] = dict(stanceFootPxPerFrameDrawn=round(drawn, 2), groundPxPerFrame=round(need, 2), slipPct=round(100 * (need - drawn) / need, 1))
    report['footSlide'] = slide
    report['combinedTicks'] = combined(data)
    female_cmp(ms)
    json.dump(report, open('hero_v3_report.json', 'w'), indent=1, default=str)
    print(json.dumps({k: report[k] for k in ('turnaround', 'uniq', 'timing')}, indent=0, default=str)[:4000])
    print('slide', report['footSlide']); print('propdev', {m: (report['prop'][m]['maxHeadDev'], report['prop'][m]['maxCrotchDev']) for m in report['prop']})
