#!/usr/bin/env python3
"""v2 renderer: same song data (songs/*.py) -> per-channel MIDI -> sampled instruments (FluidSynth + GeneralUser GS,
VSCO-2 CE one-shots) + a few synth layers (sub drone, kick/snare/taiko reinforcement) -> production mix
(amp-sim guitars, double tracking, EQ, saturation, compression, kick ducking, hall reverb, M/S width)
-> mastering (glue comp, soft clip, look-ahead limiter) to the target loudness.  Seamless loops as in render.py.

usage: python3 tools/music/render2.py id [id ...] [--out=DIR] [--stems]
needs: fluidsynth, samples from fetch_samples.sh (SAMPLES env, default /workspace/samples)
"""
import os, sys, json, subprocess, tempfile, glob, time, hashlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np, soundfile as sf, mido, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve
from scipy.ndimage import minimum_filter1d, uniform_filter1d, maximum_filter1d
import pedalboard as pb

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import synth as S, score as SC
from render import load_song

SR = 44100
SAMPLES = os.environ.get('SAMPLES', '/workspace/samples')
GU = os.path.join(SAMPLES, 'GeneralUser-GS.sf2')
VSCO = os.path.join(SAMPLES, 'VSCO')
TAIL = 4.0
DARK_MODES = ('phrygian', 'phrydom')
CALM = ('town_', 'ending_', 'forge_shop', 'worldmap', 'underwater', 'jingle_')
REF_METRICS = os.path.join(HERE, 'ref_metrics.json')   # analysis of the user's reference (dark-track target)
def is_calm(song): return song['id'].startswith(CALM)

# ---------------------------------------------------------------- instrument map (GeneralUser GS programs)
# inst -> list of layers (bank, program, gain, transpose)  + processing preset
PATCH = {
    'guitar':   ([(0, 27, 1.0, 0)], 'gtr_lead'),
    'power':    ([(0, 27, 1.0, 0)], 'gtr_rhythm'),
    'flute':    ([(0, 73, 1.0, 0)], 'wind'),
    'lead_soft': ([(0, 40, 1.0, 0)], 'violin'),
    'psg':      ([(0, 80, 0.55, 0), (0, 11, 0.6, 0)], 'synth'),
    'pluck':    ([(0, 46, 1.0, 0), (0, 24, 0.5, 0)], 'pluck'),
    'epiano':   ([(0, 0, 1.0, 0)], 'piano'),
    'bell':     ([(0, 8, 0.9, 0), (0, 9, 0.5, 0)], 'bell'),
    'toll':     ([(0, 14, 0.8, 12)], 'toll'),
    'brass':    ([(0, 61, 1.0, 0), (0, 60, 0.6, 0)], 'brass'),
    'strings':  ([(0, 49, 1.0, 0), (0, 48, 0.45, 0), (0, 50, 0.25, 0)], 'strings'),
    'stacc_str': ([(0, 48, 1.0, 0), (0, 45, 0.35, 0)], 'strings_st'),
    'choir':    ([(0, 52, 1.0, 0), (0, 53, 0.7, 0), (0, 91, 0.25, 0)], 'choir'),
    'organ':    ([(0, 19, 1.0, 0)], 'organ'),
    'slap':     ([(0, 36, 1.0, 0)], 'bass'),
    'pickbass': ([(0, 34, 1.0, 0)], 'bass'),
    'synbass':  ([(0, 38, 1.0, 0)], 'bass'),
    'softbass': ([(0, 33, 1.0, 0)], 'bass_soft'),
    'drone':    ([(0, 49, 0.8, 12), (0, 89, 0.5, 12)], 'drone'),
    'timpani':  ([(0, 47, 1.0, 0)], 'perc'),
}
# drum name -> (stem, GM note) on the GeneralUser 'Power' kit (bank 128 prog 16); None = VSCO / synth only
DRUMMAP = {'k': ('kick', 36), 's': ('snare', 38), 'p': ('snare', 39), 'h': ('hats', 42), 'H': ('hats', 46), 'c': ('cym', 49),
           'r': ('cym', 51), 't1': ('toms', 48), 't2': ('toms', 45), 't3': ('toms', 41), 'sh': ('hats', 70), 'cb': ('perc', 81),
           'T': ('taiko', None), 'b': ('boom', None), 'an': ('perc', None)}


# ---------------------------------------------------------------- MIDI + FluidSynth
def humanize(seed):
    return np.random.default_rng(int(hashlib.md5(str(seed).encode()).hexdigest()[:8], 16))


def write_midi(path, notes, bank, prog, end_t, ch=0, bends=False, seed=0, tjit=0.004, vjit=7):
    """notes: dicts t,d,m,v (+bend, stacc, glide).  times in seconds (tempo fixed 120 -> 1920 ticks/s)."""
    rng = humanize(seed)
    tpb = 960; tps = tpb * 2
    mf = mido.MidiFile(ticks_per_beat=tpb); tr = mido.MidiTrack(); mf.tracks.append(tr)
    msgs = [(0, 0, mido.Message('control_change', channel=ch, control=0, value=bank if bank < 128 else 0)),
            (0, 1, mido.Message('program_change', channel=ch, program=prog))]
    if bends:  # pitch-bend range 2 semitones
        for c, v in ((101, 0), (100, 0), (6, 2), (38, 0)):
            msgs.append((0, 2, mido.Message('control_change', channel=ch, control=c, value=v)))
    for n in notes:
        t0 = max(0.0, n['t'] + (rng.normal(0, tjit) if tjit else 0)); d = n['d'] * (0.55 if n.get('stacc') else 0.98)
        vel = int(np.clip(28 + n['v'] * 92 + rng.normal(0, vjit), 1, 127))
        m = int(n['m'])
        if not 0 <= m <= 127: continue
        if bends:
            if n.get('bend'):
                b = n['bend'] / 2.0
                for k in range(8):
                    tt = t0 + k * 0.012; val = int(-8191 * b * (1 - k / 7) ** 1.5)
                    msgs.append((tt - (0.002 if k == 0 else 0), 3, mido.Message('pitchwheel', channel=ch, pitch=val)))
            else:
                msgs.append((t0 - 0.002, 3, mido.Message('pitchwheel', channel=ch, pitch=0)))
            if d > 0.32:  # delayed vibrato
                k = 0; tt = t0 + 0.22
                while tt < t0 + d - 0.02:
                    depth = min(1, (tt - t0 - 0.22) / 0.25) * 0.22 / 2
                    msgs.append((tt, 3, mido.Message('pitchwheel', channel=ch, pitch=int(8191 * depth * np.sin(2 * np.pi * 5.6 * (tt - t0))))))
                    tt += 0.015
        msgs.append((t0, 5, mido.Message('note_on', channel=ch, note=m, velocity=vel)))
        msgs.append((t0 + d, 4, mido.Message('note_off', channel=ch, note=m, velocity=0)))
    msgs.append((end_t, 9, mido.Message('control_change', channel=ch, control=7, value=100)))
    msgs.sort(key=lambda x: (x[0], x[1]))
    now = 0
    for t, _, msg in msgs:
        tk = int(round(max(0, t) * tps)); msg.time = tk - now; now = tk; tr.append(msg)
    mf.save(path)


def fluid(mid, wav, sf2=GU, gain=0.5):
    subprocess.run(['fluidsynth', '-ni', '-q', '-o', 'synth.reverb.active=0', '-o', 'synth.chorus.active=0', '-o', 'synth.polyphony=512',
                    '-g', str(gain), '-r', str(SR), '-F', wav, sf2, mid], check=True, capture_output=True)
    x, sr = sf.read(wav, always_2d=True)
    return x.T


# ---------------------------------------------------------------- VSCO one-shots
_vs = {}
def vsco(name):
    if name not in _vs:
        p = os.path.join(VSCO, 'Percussion', name)
        if os.path.exists(p):
            x, sr = sf.read(p, always_2d=True); x = x.mean(1)
            if sr != SR: x = resample_poly(x, SR, sr)
            _vs[name] = x / (np.abs(x).max() + 1e-9)
        else:
            _vs[name] = None
    return _vs[name]


def place(buf, smp, t, g):
    if smp is None: return
    i = int(round(t * SR)); j = min(buf.shape[-1], i + len(smp))
    if i < j: buf[..., i:j] += smp[:j - i] * g


# ---------------------------------------------------------------- DSP helpers
def bw(x, fc, kind='low', order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), kind, fs=SR, output='sos'), x, axis=-1)


def board(x, *fx):
    return pb.Pedalboard(list(fx))(np.ascontiguousarray(x, dtype=np.float32), SR).astype(np.float64)


def amp(x, gain_db=34, tight=110, lead=False):
    """Two-stage high-gain amp + 4x12-style cabinet EQ (mono in -> mono out)."""
    x = x / (np.abs(x).max() + 1e-9) * 0.5
    up = resample_poly(x, 4, 1); sr4 = SR * 4
    up = sosfilt(butter(2, tight, 'high', fs=sr4, output='sos'), up)
    up = sosfilt(butter(1, 3500, 'low', fs=sr4, output='sos'), up) * 0.6 + up * 0.4    # pre-emphasis mids
    g = 10 ** (gain_db / 20)
    y = np.tanh(g * up + 0.15) - np.tanh(0.15)
    y = sosfilt(butter(1, 25, 'high', fs=sr4, output='sos'), y)
    y = np.tanh(2.2 * y)
    y = resample_poly(y, 1, 4)
    y = board(y, pb.HighpassFilter(85), pb.PeakFilter(115, 3.0, 1.0), pb.PeakFilter(450, -3.0, 0.9),
              pb.PeakFilter(2300 if not lead else 1800, 4.0 if not lead else 3.0, 1.1), pb.PeakFilter(3800, -2.0, 2.0))
    y = bw(bw(y, 5200, 'low', 4), 9000, 'low', 2)
    return y


def comp(x, thr=-18, ratio=3, att=10, rel=120):
    return board(x, pb.Compressor(threshold_db=thr, ratio=ratio, attack_ms=att, release_ms=rel))


def to_st(m, pan=0.0):
    if m.ndim == 2: return m
    a = (pan + 1) * np.pi / 4
    return np.stack([m * np.cos(a), m * np.sin(a)])


def width(x, w=1.3, mono_below=150):
    M = (x[0] + x[1]) / 2; Sd = (x[0] - x[1]) / 2
    Sd = bw(Sd, mono_below, 'high', 2) * w
    return np.stack([M + Sd, M - Sd])


def hall_ir(rt=2.8, pre=0.025, seed=7, bright=1.0):
    n = int(rt * 1.3 * SR); t = np.arange(n) / SR; out = []
    for c in range(2):
        rng = np.random.default_rng(seed + c)
        nz = rng.standard_normal(n)
        lo = bw(nz, 400, 'low', 2) * np.exp(-6.9 * t / (rt * 1.15))
        mid = bw(bw(nz, 400, 'high', 2), 3500 * bright, 'low', 2) * np.exp(-6.9 * t / rt)
        hi = bw(nz, 3500 * bright, 'high', 2) * np.exp(-6.9 * t / (rt * 0.45))
        ir = (lo * 0.9 + mid + hi * 0.5) * np.minimum(1, t / 0.03)
        er = np.zeros(n)
        for k in range(18):
            er[int(rng.uniform(0.004, 0.09) * SR)] += rng.uniform(0.3, 1.0) * (1 - k / 20) * (1 if rng.random() > .5 else -1)
        ir = ir * 0.8 + bw(er, 6000, 'low', 2) * 0.6
        ir = np.concatenate([np.zeros(int(pre * SR)), ir])
        out.append(ir / np.sqrt((ir ** 2).sum()))
    return np.stack(out)


def conv(x, ir):
    return np.stack([fftconvolve(x[c], ir[c])[:x.shape[1]] for c in range(2)])


def duck_env(n, kick_times, depth=0.3, rel=0.14):
    e = np.zeros(n); t = np.arange(int(rel * 5 * SR)) / SR; shape = np.exp(-t / rel) * np.minimum(1, t / 0.004)
    for tk in kick_times:
        i = int(tk * SR); j = min(n, i + len(shape))
        if i < n: e[i:j] = np.maximum(e[i:j], shape[:j - i])
    return 1 - depth * e


# ---------------------------------------------------------------- per-region stem rendering
def render_stems(song, which, tmp):
    ev, steps, sps, chmap = SC.build(song, which)
    if steps == 0: return None, 0, None
    body = steps * sps; nB = int(round(body * SR)); N = nB + int(TAIL * SR)
    end_t = body + TAIL - 0.05
    jobs = []   # (stem_name, preset, pan, gain, rev, layer args)
    stems = {}
    kick_t = []
    dark = song.get('mode') in DARK_MODES or song.get('style') == 'dark'
    for cname, cfg in chmap.items():
        evs = ev.get(cname)
        if not evs: continue
        if cfg['type'] == 'drums':
            groups = {}
            for e in evs:
                dn = e['dn']; stem, note = DRUMMAP[dn]
                if dn == 'k': kick_t.append(e['t'])
                groups.setdefault(stem, []).append(e)
            for stem, es in groups.items():
                gm = [dict(t=e['t'], d=0.25, m=DRUMMAP[e['dn']][1], v=e['v']) for e in es if DRUMMAP[e['dn']][1] is not None]
                jobs.append(('drum_' + stem, 'drum_' + stem, 0, 1.0, (128, 48 if dark else (8 if is_calm(song) else 16), gm, False, 0.002, 6), es))
            continue
        inst = cfg['inst']
        layers, preset = PATCH.get(inst, ([(0, 0, 1.0, 0)], 'piano'))
        if cfg['type'] in ('comp',) or 'ms' in evs[0]:
            notes = []
            for e in evs:
                for k, m in enumerate(e['ms']):
                    notes.append(dict(t=e['t'] + k * cfg.get('strum', 0.0), d=e['d'], m=m, v=e['v'] * (0.85 if e.get('mute') else 1.0), mute=e.get('mute')))
            evs2 = notes
        else:
            evs2 = [dict(e, m=e['m'] + cfg.get('transpose', 0)) for e in evs]
        mono = cfg['type'] in ('mel', 'padmel') and inst in ('guitar', 'flute', 'lead_soft', 'brass', 'psg')
        for li, (bank, prog, lg, tr) in enumerate(layers):
            notes = [dict(e, m=e['m'] + tr) for e in evs2]
            if inst == 'power':
                for take, pan in ((1, -0.85), (2, 0.85)):
                    for mu, pg in ((True, 28), (False, 27)):
                        nn = [dict(e) for e in notes if bool(e.get('mute')) == mu]
                        if nn: jobs.append((f'{cname}_t{take}{"m" if mu else "o"}', 'gtr_rhythm', pan, cfg['gain'], (bank, pg, nn, False, 0.006, 9), take))
            else:
                jobs.append((f'{cname}_{li}', preset, cfg.get('pan', 0), lg * cfg['gain'], (bank, prog, notes, mono, 0.005 if cfg['type'] != 'pad' else 0.012, 7), cname))
    # ---- Ys-Eternal-style sampled layers for the bright tracks: violin doubling the lead, piano voicing the pad chords
    if not dark and song.get('v2_layers', True):
        if ev.get('lead') and chmap['lead']['inst'] == 'guitar':
            jobs.append(('violin_0', 'violin', 0.25, 1.0, (0, 40, [dict(e) for e in ev['lead']], True, 0.006, 6), 'violin'))
        if ev.get('pad'):
            jobs.append(('piano_0', 'piano', 0, 1.0, (0, 0, [dict(e, m=e['m'] + 12, v=0.55) for e in ev['pad']], False, 0.01, 8), 'piano'))
    # ---- run fluidsynth jobs in parallel
    def run(job):
        name, preset, pan, g, (bank, prog, notes, bends, tj, vj), meta = job
        if not notes: return name, None
        mid = os.path.join(tmp, f'{which}_{name}.mid'); wav = mid[:-4] + '.wav'
        write_midi(mid, notes, bank, prog, end_t, ch=9 if bank == 128 else 0, bends=bends, seed=song['id'] + name + which, tjit=tj, vjit=vj)
        x = fluid(mid, wav)
        y = np.zeros((2, N), np.float32); L = min(N, x.shape[1]); y[:, :L] = x[:, :L]
        return name, y
    with ThreadPoolExecutor(8) as ex:
        res = dict(ex.map(run, jobs))
    info = {}
    for job in jobs:
        name, preset, pan, g, _, meta = job
        info[name] = (preset, pan, g, meta)
    # ---- synth / one-shot layers
    def stem_add(name, preset, x, pan=0, g=1.0):
        res[name] = x.astype(np.float32); info[name] = (preset, pan, g, None)
    if ev.get('drums'):
        kick = np.zeros(N); sn = np.zeros(N); tk = np.zeros((2, N)); bm = np.zeros((2, N)); an = np.zeros(N)
        for e in ev['drums']:
            dn = e['dn']
            if dn == 'k': place(kick, S.drum('k'), e['t'], e['v'] * 0.55)
            elif dn == 's': place(sn, S.drum('s'), e['t'], e['v'] * 0.35)
            elif dn == 'T':
                place(tk[0], S.drum('T'), e['t'], e['v'] * 0.8); place(tk[1], S.drum('T'), e['t'] + 0.006, e['v'] * 0.8)
                bd = vsco('BDrumNewhit_v%d_rr%d_Sum.wav' % (min(7, 3 + int(e['v'] * 4)), 1 + int(e['t'] * 7) % 2))
                place(tk, bd, e['t'], e['v'] * 0.7)
                low = vsco('LogDrumLo_MedM_v3_rr1_Sum.wav'); place(tk[0], low, e['t'] + 0.01, e['v'] * 0.15)
            elif dn == 'b':
                place(bm, S.drum('b'), e['t'], e['v'] * 0.8)
                place(bm, vsco('BDrumNewhit_v7_rr1_Sum.wav'), e['t'], e['v'] * 0.9)
                place(bm, vsco('gongHit_fff.wav'), e['t'], e['v'] * 0.35)
            elif dn == 'an':
                place(an, vsco('Anvil_Hit1_v%d_Sum.wav' % (1 + int(e['t'] * 5) % 3)), e['t'], e['v'] * 0.6)
            elif dn == 'c' and dark:
                place(bm, vsco('susCymb1-hit_f_rr1.wav'), e['t'], e['v'] * 0.25)
        stem_add('syn_kick', 'drum_kick_syn', np.stack([kick, kick]))
        stem_add('syn_snare', 'drum_snare_syn', np.stack([sn, sn]))
        if np.any(tk): stem_add('taiko', 'taiko', tk)
        if np.any(bm): stem_add('boom', 'boom', bm)
        if np.any(an): stem_add('anvil', 'perc', np.stack([an, an]), 0.25)
    if ev.get('drone'):
        d = np.zeros(N)
        for e in ev['drone']:
            place(d, S.drone(S.mtof(e['m']), e['d'], 0.8), e['t'], 1.0)
        stem_add('syn_sub', 'sub', np.stack([d, d]), 0, chmap['drone']['gain'] / 0.26)
    if ev.get('toll'):
        d = np.zeros(N)
        for e in ev['toll']:
            place(d, S.toll(S.mtof(e['m']), e['d'], 0.8), e['t'], 1.0)
        stem_add('syn_toll', 'toll', np.stack([d, d]), -0.1, chmap['toll']['gain'] / 0.3 * 0.6)
    if dark and ev.get('bass'):  # sub reinforcement under the bass (reference: heavy 40-80 Hz)
        d = np.zeros(N)
        for e in ev['bass']:
            place(d, S._bassbase(S.mtof(e['m']), max(e['d'], 0.08), 0.8, 0.3, 0.05, 0.1, 1.2, 0.05, 1.0, sub=1.0), e['t'], 1.0)
        stem_add('syn_bsub', 'sub', np.stack([d, d]), 0, 0.8)
    return dict(res=res, info=info, kick=kick_t, n=nB, N=N, dark=dark, sps=sps), nB, chmap


# ---------------------------------------------------------------- mixing presets
def process(name, preset, pan, g, x, ctx):
    """returns (dry stereo, reverb send, delay send)"""
    m = x.mean(0) if x.ndim == 2 else x
    rv, dl = 0.0, 0.0
    if preset == 'gtr_rhythm':
        y = amp(m, 36, 120) * 0.55
        y = comp(y, -20, 3, 5, 80)
        out = to_st(y, pan); rv = 0.06
    elif preset == 'gtr_lead':
        y = amp(m, 30, 160, lead=True) * 0.6
        y = comp(y, -22, 3, 3, 120)
        y = board(y, pb.PeakFilter(3000, 2.5, 1.0))
        st = to_st(y, pan)
        d = int(0.011 * SR); st = st + 0.25 * np.stack([np.r_[np.zeros(d), y[:-d]], np.r_[y[d // 2:], np.zeros(d // 2)]])  # short width
        out = st; rv, dl = 0.22, 0.2
    elif preset in ('bass', 'bass_soft'):
        y = board(m, pb.HighpassFilter(32), pb.PeakFilter(80, 3, 0.9), pb.PeakFilter(260, -3, 1.0), pb.PeakFilter(1200, 2.5 if preset == 'bass' else 0, 1.0),
                  pb.Compressor(threshold_db=-20, ratio=4, attack_ms=8, release_ms=100))
        y = np.tanh(1.6 * y / (np.abs(y).max() + 1e-9)) * np.abs(y).max()
        out = to_st(y, 0); rv = 0.02
    elif preset == 'sub':
        y = bw(m, 110, 'low', 2); out = to_st(y, 0)
    elif preset in ('strings', 'strings_st', 'choir', 'organ', 'drone'):
        y = board(x if x.ndim == 2 else to_st(x), pb.HighpassFilter(90 if preset != 'drone' else 30), pb.Compressor(threshold_db=-24, ratio=2, attack_ms=30, release_ms=250))
        if preset == 'choir': y = board(y, pb.PeakFilter(3000, -2, 1.0), pb.HighShelfFilter(9000, 1.5))
        if preset == 'strings_st': y = board(y, pb.PeakFilter(2500, 2, 1.0))
        out = width(y, 1.5) * 1.0; rv = {'choir': 0.55, 'organ': 0.45, 'drone': 0.3}.get(preset, 0.4)
    elif preset in ('wind', 'violin', 'brass', 'synth', 'pluck', 'piano', 'bell'):
        y = board(x if x.ndim == 2 else to_st(x), pb.HighpassFilter(140 if preset != 'piano' else 60), pb.Compressor(threshold_db=-22, ratio=2.5, attack_ms=15, release_ms=150))
        if preset == 'synth': y = board(y, pb.LowpassFilter(6000))
        y = y.mean(0); out = to_st(y, pan)
        if preset in ('piano', 'pluck', 'bell'): out = width(x if x.ndim == 2 else to_st(y), 1.2)
        rv, dl = {'wind': 0.32, 'violin': 0.35, 'brass': 0.3, 'synth': 0.25, 'pluck': 0.3, 'piano': 0.3, 'bell': 0.45}[preset], 0.15
    elif preset == 'toll':
        out = to_st(board(m, pb.HighpassFilter(40)), pan); rv = 0.6
    elif preset == 'perc':
        out = to_st(board(m, pb.HighpassFilter(60)), pan); rv = 0.3
    elif preset == 'drum_kick':
        y = board(m, pb.HighpassFilter(30), pb.PeakFilter(62, 4, 1.0), pb.PeakFilter(330, -5, 1.0), pb.PeakFilter(4000, 4, 1.0))
        out = to_st(y); rv = 0.02
    elif preset == 'drum_kick_syn':
        out = to_st(board(m, pb.HighpassFilter(28), pb.LowpassFilter(9000))); rv = 0.0
    elif preset in ('drum_snare', 'drum_snare_syn'):
        y = board(m, pb.HighpassFilter(90), pb.PeakFilter(200, 3, 1.0), pb.PeakFilter(900, -2, 1.0), pb.HighShelfFilter(5000, 3))
        out = to_st(y, 0.03); rv = 0.28
    elif preset == 'drum_toms':
        out = x if x.ndim == 2 else to_st(m); out = board(out, pb.PeakFilter(100, 2, 1)); rv = 0.2
    elif preset in ('drum_hats', 'drum_cym'):
        out = board(x, pb.HighpassFilter(350)); out = width(out, 1.3); rv = 0.12
    elif preset == 'drum_perc':
        out = board(x, pb.HighpassFilter(200)); rv = 0.25
    elif preset == 'drum_taiko' or preset == 'taiko':
        out = board(x if x.ndim == 2 else to_st(m), pb.HighpassFilter(35), pb.PeakFilter(70, 3, 0.8), pb.PeakFilter(400, -3, 1.0))
        out = width(out, 1.4); rv = 0.45
    elif preset in ('boom', 'drum_boom'):
        out = board(x if x.ndim == 2 else to_st(m), pb.HighpassFilter(25)); rv = 0.5
    else:
        out = x if x.ndim == 2 else to_st(m, pan); rv = 0.2
    return out * g, rv, dl


# gated active-RMS target per channel / stem (dBFS before master); song cfg gain vs default scales on top
LEVEL = {'lead': -19, 'lead2': -23, 'counter': -25, 'bell': -28, 'choir': -23, 'bass': -20, 'comp': -25, 'arp': -30, 'pad': -27,
         'choirpad': -27, 'toll': -26, 'ost': -26, 'organ': -27, 'brasspad': -27, 'drone': -29, 'piano': -29, 'violin': -28,
         'drum_kick': -21, 'syn_kick': -26, 'drum_snare': -22, 'syn_snare': -30, 'drum_hats': -31, 'drum_cym': -31, 'drum_toms': -26,
         'drum_perc': -30, 'taiko': -22, 'boom': -23, 'anvil': -30, 'syn_sub': -27, 'syn_bsub': -27, 'syn_toll': -29}
def active_rms(x):
    m = x.mean(0) if x.ndim == 2 else x
    hop = 2048; k = len(m) // hop
    if k == 0: return 1e-9
    fr = np.sqrt((m[:k * hop].reshape(k, hop) ** 2).mean(1) + 1e-20)
    gate = fr > fr.max() * 10 ** (-30 / 20)
    return np.sqrt((fr[gate] ** 2).mean())


def level_key(name):
    if name.startswith('drum_') or name.startswith('syn_') or name in ('taiko', 'boom', 'anvil'): return name
    return name.rsplit('_', 1)[0]


def bus_kind(preset):
    if preset.startswith('drum') or preset in ('taiko', 'boom'): return 'drums'
    if preset in ('bass', 'bass_soft', 'sub'): return 'bass'
    return 'music'


def mix(song, R):
    """R from render_stems; tile = function(x)-> tiled/processed timeline. returns stereo mix (tiled)."""
    info = R['info']
    busses = {'drums': 0, 'bass': 0, 'music': 0}
    rev = 0; dly = 0
    kick_dk = None
    for name in R['names']:
        xt = R['get'](name).astype(np.float64)
        if not np.any(xt): continue
        preset, pan, g, _ = info[name]
        out, rv, dl = process(name, preset, pan, 1.0, xt, R)
        key = level_key(name); base = SC.DEFAULT_CH.get(key, {}).get('gain')
        rel = (g / base) if (base and not name.startswith('syn_')) else g
        if name.split('_')[-1].isdigit() and int(name.split('_')[-1]) > 0:
            rel = g / (base or 1)  # secondary layer: already includes layer gain
        tgt = LEVEL.get(key, -28)
        if is_calm(song): tgt += {'lead': -2, 'drum_hats': -3, 'drum_cym': -3}.get(key, 0)
        if R['dark'] and key in ('syn_kick', 'syn_bsub', 'boom'): tgt += 2
        out *= 10 ** (tgt / 20) / active_rms(out) * rel
        mixg = song.get('mix2', {}).get(key, 1.0) * song.get('mix2', {}).get(name, 1.0)
        out *= mixg
        if os.environ.get('V2DBG'): print('   stem %-16s %-14s rms %6.1f dB' % (name, preset, 20*np.log10(np.sqrt((out**2).mean())+1e-12)))
        b = bus_kind(preset)
        busses[b] = busses[b] + out
        if not preset.startswith('drum_kick') and preset != 'sub':
            if rv: rev = rev + out * rv
            if dl: dly = dly + out * dl
        del xt, out
    n = next(v.shape[1] for v in busses.values() if not isinstance(v, int))
    # kick ducking on bass + music
    kt = R['kt_tiled']
    if kt is not None and len(kt):
        dk = duck_env(n, kt, depth=0.22 if R['dark'] else 0.18)
        for b in ('bass', 'music'):
            if not isinstance(busses[b], int): busses[b] = busses[b] * dk
    # drum bus: parallel compression + saturation
    if not isinstance(busses['drums'], int):
        d = busses['drums']
        crush = board(d, pb.Compressor(threshold_db=-28, ratio=6, attack_ms=3, release_ms=90), pb.Gain(8))
        busses['drums'] = d + 0.35 * crush
    if not isinstance(busses['bass'], int):
        busses['bass'] = board(busses['bass'], pb.Compressor(threshold_db=-18, ratio=3, attack_ms=15, release_ms=120))
    beat = 60.0 / song['bpm']
    # reverb + delay
    rt = song.get('rt60_2', max(1.8, song.get('rt60', 1.8) * 1.15))
    wet = 0
    if not isinstance(rev, int):
        wet = conv(board(rev, pb.HighpassFilter(180), pb.LowpassFilter(9000)), hall_ir(rt)) * song.get('wet2', 0.9)
    if not isinstance(dly, int):
        dir_ = S.delay_ir(0.75 * beat, fb=0.32)
        wet = wet + conv(board(dly, pb.HighpassFilter(300), pb.LowpassFilter(5000)), dir_) * 0.35
    music = busses['music'] if not isinstance(busses['music'], int) else 0
    total = busses['drums'] + busses['bass'] + music + wet
    if isinstance(total, int): total = np.zeros((2, n))
    return total


def master(song, x, dark):
    target = song.get('lufs2', -14.0 if is_calm(song) else -12.0)
    y = board(x, pb.HighpassFilter(24), pb.Compressor(threshold_db=-16, ratio=2, attack_ms=25, release_ms=180))
    if song.get('eq2'):
        y = apply_eq(y, song['eq2'])
    y = width(y, song.get('width2', 1.12), 140)
    if is_calm(song): y = board(y, pb.HighShelfFilter(8000, -3.0))
    if dark and os.path.exists(REF_METRICS) and song.get('match2', True):   # match-EQ toward the reference band profile, +-4 dB
        ref = json.load(open(REF_METRICS))['bands']; cur = analyze(y)['bands']
        diff = np.clip((np.array(ref) - np.array(cur)) * 0.7, -4, 4); diff[0] = min(diff[0], 5.0)
        cs = [np.sqrt(a * b) for a, b in BANDS]
        y = apply_eq(y, list(zip(cs, diff)))
        print('    match-EQ', [round(d, 1) for d in diff], flush=True)
    meter = pyln.Meter(SR)
    for it in range(3):  # iterate: gain -> soft clip -> limiter, until loudness hits target
        L = meter.integrated_loudness(y.T)
        y = y * 10 ** ((target - L) / 20)
        y = softclip(y, 0.94)
        y = limit(y)
    return y, target


def softclip(x, th=0.9):
    a = np.abs(x); over = a > th
    y = x.copy(); y[over] = np.sign(x[over]) * (th + (1 - th) * np.tanh((a[over] - th) / (1 - th)))
    return y


CEIL = 10 ** (-1.0 / 20)
def limit(x, la=0.005):
    W = int(la * SR)
    up = np.abs(resample_poly(x, 2, 1, axis=1)).max(0)[::2][:x.shape[1]]
    pk = np.maximum(np.abs(x).max(0), up)
    g = np.minimum(1.0, CEIL / np.maximum(pk, 1e-9))
    g = minimum_filter1d(g, 2 * W + 1)
    g = uniform_filter1d(g, W | 1)
    rel = uniform_filter1d(minimum_filter1d(g, int(0.03 * SR)), int(0.03 * SR))
    g = np.minimum(g, rel)
    return np.clip(x * g, -CEIL, CEIL)


def apply_eq(x, bands):
    """bands: list of (freq, gain_db) -> smooth zero-phase FFT EQ curve."""
    n = x.shape[1]; F = np.fft.rfft(x, axis=1); f = np.fft.rfftfreq(n, 1 / SR)
    fs = np.array([b[0] for b in bands]); gs = np.array([b[1] for b in bands])
    lf = np.log10(np.maximum(f, 10)); curve = np.interp(lf, np.log10(fs), gs)
    return np.fft.irfft(F * 10 ** (curve / 20), n=n, axis=1)


# ---------------------------------------------------------------- analysis (for reference matching)
BANDS = [(20, 40), (40, 80), (80, 160), (160, 320), (320, 640), (640, 1250), (1250, 2500), (2500, 5000), (5000, 10000), (10000, 20000)]
def analyze(x):
    m = x.mean(0); F = np.abs(np.fft.rfft(m)) ** 2; f = np.fft.rfftfreq(len(m), 1 / SR); tot = F[(f > 20)].sum()
    bands = [10 * np.log10(F[(f >= a) & (f < b)].sum() / tot + 1e-12) for a, b in BANDS]
    meter = pyln.Meter(SR); L = meter.integrated_loudness(x.T)
    w = 3 * SR; st = [meter.integrated_loudness(x[:, i:i + w].T) for i in range(0, x.shape[1] - w, SR)]
    st = [s for s in st if s > -70]
    lra = np.percentile(st, 95) - np.percentile(st, 10) if st else 0
    rms = np.sqrt((m ** 2).mean()); crest = 20 * np.log10(np.abs(x).max() / (rms + 1e-12))
    M = (x[0] + x[1]) / 2; Sd = (x[0] - x[1]) / 2
    side = 10 * np.log10((Sd ** 2).sum() / ((M ** 2).sum() + 1e-12))
    corr = np.corrcoef(x[0], x[1])[0, 1]
    cent = (f * F).sum() / F.sum()
    return dict(lufs=round(L, 1), lra=round(lra, 1), crest=round(crest, 1), side_db=round(side, 1), lr_corr=round(corr, 2), centroid=int(cent),
                peak=round(20 * np.log10(np.abs(x).max()), 2), bands=[round(b, 1) for b in bands])


# ---------------------------------------------------------------- song render
def render_song(path, outdir, stems_dir=None):
    t0 = time.time()
    song = load_song(path); sid = song['id']
    with tempfile.TemporaryDirectory() as tmp:
        RI, nI, _ = render_stems(song, 'intro', tmp) if song.get('intro') else (None, 0, None)
        RL, nL, _ = render_stems(song, 'loop', tmp) if song.get('loop') else (None, 0, None)
    dark = (RL or RI)['dark']
    if RL is not None:
        # fold each loop stem's tail, then build timeline = intro(+tail into loop1) + loop x3; process; keep intro + loop copy 2
        for k, x in RL['res'].items():
            if x is None: continue
            L = x[:, :nL].astype(np.float32); tail = x[:, nL:]; j = 0
            while j < tail.shape[1]:
                seg = tail[:, j:j + nL]; L[:, :seg.shape[1]] += seg; j += nL
            RL['res'][k] = L
        names = set(k for k, v in RL['res'].items() if v is not None) | (set(k for k, v in RI['res'].items() if v is not None) if RI else set())
        def tiled(k):   # built lazily, one stem at a time (memory)
            li = RL['res'].pop(k, None); ii = RI['res'].pop(k, None) if RI else None
            if li is None: li = np.zeros((2, nL), np.float32)
            tl = np.zeros((2, nI + 3 * nL), np.float32)
            if ii is not None:
                tl[:, :min(ii.shape[1], tl.shape[1])] += ii[:, :tl.shape[1]]
            for c in range(3): tl[:, nI + c * nL:nI + (c + 1) * nL] += li
            return tl
        R = dict(names=sorted(names), get=tiled, info={**(RI['info'] if RI else {}), **RL['info']}, dark=dark)
        kt = (RI['kick'] if RI else []) + [nI / SR + c * nL / SR + t for c in range(3) for t in RL['kick']]
        R['kt_tiled'] = kt
        mixed = mix(song, R)
        y, target = master(song, mixed, dark)
        out = np.concatenate([y[:, :nI], y[:, nI + nL:nI + 2 * nL]], axis=1)
        if stems_dir:
            os.makedirs(stems_dir, exist_ok=True)
    else:
        R = dict(RI); R['kt_tiled'] = RI['kick']; R['names'] = [k for k, v in RI['res'].items() if v is not None]; R['get'] = lambda k: RI['res'].pop(k)
        mixed = mix(song, R)
        y, target = master(song, mixed, dark)
        a = np.abs(y).max(0); nz = np.nonzero(a > 1e-4)[0]; out = y[:, :nz[-1] + int(0.1 * SR)]
        fade = int(0.08 * SR); out[:, -fade:] *= np.linspace(1, 0, fade)
    wav = os.path.join(tempfile.gettempdir(), f'_v2_{sid}.wav')
    sf.write(wav, out.T.astype(np.float32), SR, subtype='FLOAT')
    ogg = os.path.join(outdir, sid + '.ogg')
    meta = ['-metadata', 'title=' + song['title'], '-metadata', 'artist=thor-like-game BGM v2 (original)']
    if RL is not None: meta += ['-metadata', 'LOOPSTART=%d' % nI, '-metadata', 'LOOPLENGTH=%d' % nL]
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav, '-c:a', 'libvorbis', '-q:a', str(song.get('q2', 3))] + meta + [ogg], check=True)
    an = analyze(out[:, nI:] if RL is not None else out)
    os.remove(wav)
    info = dict(id=sid, file=sid + '.ogg', title=song['title'], en=song.get('en', ''), bpm=song['bpm'], key=song['key'] + ' ' + song.get('mode', 'minor'),
                loop=RL is not None, loopStart=round(nI / SR, 6), loopEnd=round((nI + nL) / SR, 6), duration=round(out.shape[1] / SR, 3),
                lufs=an['lufs'], truePeak=an['peak'], bytes=os.path.getsize(ogg), version=2)
    print('%-22s %5.1fs  %s  (%.0fs)' % (sid, info['duration'], json.dumps({k: an[k] for k in ('lufs', 'lra', 'crest', 'side_db', 'centroid', 'peak')}), time.time() - t0), flush=True)
    print('    bands', an['bands'], flush=True)
    return info, an


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    outdir = os.path.join(HERE, '..', '..', 'audio', 'bgm'); man_p = None
    for a in sys.argv:
        if a.startswith('--out='): outdir = a[6:]
    outdir = os.path.abspath(outdir); os.makedirs(outdir, exist_ok=True)
    man_p = os.path.join(outdir, 'bgm.json')
    man = json.load(open(man_p)) if os.path.exists(man_p) else {}
    rep = {}
    for sid in args:
        info, an = render_song(os.path.join(HERE, 'songs', sid + '.py'), outdir)
        man[sid] = info; rep[sid] = an
        json.dump(dict(sorted(man.items())), open(man_p, 'w'), ensure_ascii=False, indent=1)
    json.dump(rep, open(os.path.join(outdir, '_analysis_v2.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
