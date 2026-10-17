"""Small FM / chip synth for the game BGM (numpy only + scipy filters).

Every instrument is a function  f(freq_hz, dur_s, vel, **opt) -> mono float32 array
(note length + its own release tail).  Drums are cached one-shots.
The sound targets 1987-1993 Japanese FM rock (PC-88 / Mega Drive / PC Engine):
2-3 operator FM voices, overdriven FM lead, slap/pick FM bass, PSG squares.
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
TAU = 2 * np.pi
_rng = np.random.default_rng(1234)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def _t(n):
    return np.arange(n) / SR


def env_adsr(n, nOn, a=0.005, d=0.2, s=0.7, r=0.08):
    """n = total samples, nOn = gate samples.  linear attack, exp decay, exp release."""
    t = _t(n)
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    gate_t = nOn / SR
    lvl = e[min(nOn, n - 1)] if nOn < n else e[-1]
    rel = np.exp(-np.maximum(t - gate_t, 0) / max(r, 1e-4))
    e = np.where(t < gate_t, e, lvl * rel)
    return e


def pitch_curve(f, n, bend=0.0, vib=0.0, vib_rate=5.5, vib_delay=0.22, glide_from=None, glide_t=0.04):
    t = _t(n)
    semi = np.zeros(n)
    if bend:
        semi += -bend * np.exp(-t / 0.045)
    if glide_from is not None:
        semi += (glide_from) * np.exp(-t / glide_t)
    if vib:
        ramp = np.clip((t - vib_delay) / 0.25, 0, 1)
        semi += vib * ramp * np.sin(TAU * vib_rate * t)
    fr = f * 2 ** (semi / 12)
    return np.cumsum(fr) / SR  # phase in cycles


def lp(x, fc, order=2):
    fc = min(fc, SR * 0.45)
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x, axis=-1)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x, axis=-1)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, min(hi, SR * 0.45)], 'band', fs=SR, output='sos'), x, axis=-1)


# ---------------------------------------------------------------- melodic voices
def guitar(f, dur, vel=0.8, bend=0.0, vib=0.28, drive=3.2, bright=1.0, rel=0.09, stacc=False, **k):
    """Overdriven 3-op FM 'guitar' lead (the Ys-style lead)."""
    gate = dur * (0.55 if stacc else 0.97)
    n = int((gate + rel * 5) * SR)
    nOn = int(gate * SR)
    t = _t(n)
    ph = pitch_curve(f, n, bend=bend, vib=vib if dur > 0.2 else 0)
    m2 = 0.9 * bright * np.exp(-t / 0.09) * np.sin(TAU * 3 * ph)
    I1 = bright * (2.6 * np.exp(-t / 0.18) + 1.25)
    m1 = np.sin(TAU * ph + m2)
    car = np.sin(TAU * ph + I1 * m1) + 0.55 * np.sin(TAU * 1.004 * ph + 0.8 * I1 * m1)
    e = env_adsr(n, nOn, a=0.004, d=0.6, s=0.78, r=rel)
    y = np.tanh(drive * car * (0.5 + 0.5 * vel)) * e
    return y * vel


def lead_soft(f, dur, vel=0.8, bend=0.0, vib=0.22, rel=0.18, **k):
    """Clean FM brass/flute-ish lead for calm themes."""
    n = int((dur + rel * 5) * SR); nOn = int(dur * 0.95 * SR); t = _t(n)
    ph = pitch_curve(f, n, bend=bend, vib=vib if dur > 0.25 else 0)
    I = 0.9 + 0.8 * (1 - np.exp(-t / 0.08))
    y = np.sin(TAU * ph + I * np.sin(TAU * ph)) + 0.25 * np.sin(TAU * 2 * ph)
    return y * env_adsr(n, nOn, a=0.03, d=0.8, s=0.8, r=rel) * vel


def flute(f, dur, vel=0.8, bend=0.0, vib=0.25, rel=0.12, **k):
    n = int((dur + rel * 5) * SR); nOn = int(dur * 0.95 * SR); t = _t(n)
    ph = pitch_curve(f, n, bend=bend, vib=vib if dur > 0.25 else 0, vib_rate=5.0)
    y = np.sin(TAU * ph + 0.35 * np.sin(TAU * ph)) + 0.12 * np.sin(TAU * 2 * ph)
    br = bp(_rng.standard_normal(n), max(f, 200), min(f * 4, 12000)) * 0.08 * np.exp(-t / 0.08)
    return (y + br) * env_adsr(n, nOn, a=0.045, d=1.0, s=0.85, r=rel) * vel


def psg(f, dur, vel=0.8, duty=0.5, vib=0.15, rel=0.03, bend=0.0, decay=None, **k):
    """PSG / chip square."""
    n = int((dur + rel * 5) * SR); nOn = int(dur * 0.92 * SR)
    ph = pitch_curve(f, n, bend=bend, vib=vib if dur > 0.3 else 0)
    y = np.where((ph % 1.0) < duty, 1.0, -1.0)
    e = env_adsr(n, nOn, a=0.002, d=decay or 0.5, s=0.6 if decay is None else 0.0, r=rel)
    return y * e * vel * 0.5


def pluck(f, dur, vel=0.8, rel=0.25, decay=0.7, bright=1.0, **k):
    """FM pluck: harp / acoustic-ish town guitar / koto-ish."""
    n = int((dur + decay * 2.5) * SR); t = _t(n)
    ph = pitch_curve(f, n)
    I = bright * (2.2 * np.exp(-t / 0.08) + 0.25)
    y = np.sin(TAU * ph + I * np.sin(TAU * ph + 0.6 * np.exp(-t / 0.05) * np.sin(TAU * 2 * ph)))
    e = np.exp(-t / decay) * np.minimum(1, t / 0.002)
    e *= np.where(t < dur + 0.05, 1, np.exp(-(t - dur - 0.05) / rel))
    return y * e * vel


def epiano(f, dur, vel=0.8, rel=0.3, **k):
    """DX-style FM electric piano."""
    n = int((dur + 1.2) * SR); t = _t(n)
    ph = pitch_curve(f, n)
    body = np.sin(TAU * ph + 1.3 * np.exp(-t / 0.5) * np.sin(TAU * ph))
    tine = 0.25 * np.exp(-t / 0.06) * np.sin(TAU * 14 * ph + 0.8 * np.sin(TAU * ph))
    e = np.exp(-t / 1.6) * np.minimum(1, t / 0.002)
    e *= np.where(t < dur, 1, np.exp(-(t - dur) / rel))
    return (body + tine) * e * vel


def bell(f, dur, vel=0.8, ratio=3.5, decay=1.6, **k):
    n = int((max(dur, 0.2) + decay * 3) * SR); t = _t(n)
    ph = np.cumsum(np.full(n, f)) / SR
    I = 3.2 * np.exp(-t / (decay * 0.3)) + 0.25
    y = np.sin(TAU * ph + I * np.sin(TAU * ratio * ph))
    return y * np.exp(-t / decay) * np.minimum(1, t / 0.001) * vel


def toll(f, dur, vel=0.8, decay=3.5, **k):
    """Deep funeral bell (inharmonic partials)."""
    n = int((decay * 3) * SR); t = _t(n)
    parts = [(0.5, 1.0, 1.0), (1.0, 0.8, 0.7), (1.19, 0.55, 0.6), (1.56, 0.4, 0.45), (2.0, 0.5, 0.4), (2.74, 0.3, 0.3), (3.76, 0.2, 0.2)]
    y = np.zeros(n)
    for r, a, dk in parts:
        y += a * np.sin(TAU * f * r * t + _rng.random() * 6) * np.exp(-t / (decay * dk))
    return y * np.minimum(1, t / 0.002) * vel * 0.45


def brass(f, dur, vel=0.8, rel=0.12, vib=0.15, **k):
    n = int((dur + rel * 5) * SR); nOn = int(dur * 0.96 * SR); t = _t(n)
    ph = pitch_curve(f, n, vib=vib if dur > 0.3 else 0)
    I = 0.6 + 2.2 * (1 - np.exp(-t / 0.06))
    y = np.sin(TAU * ph + I * np.sin(TAU * ph)) + 0.6 * np.sin(TAU * 1.005 * ph + I * np.sin(TAU * 1.005 * ph))
    return y * env_adsr(n, nOn, a=0.035, d=0.5, s=0.75, r=rel) * vel * 0.6


def _fmsaw(ph, I=1.5):
    return np.sin(TAU * ph + I * np.sin(TAU * ph))


def strings(f, dur, vel=0.8, att=0.25, rel=0.6, **k):
    n = int((dur + rel * 4) * SR); nOn = int(dur * SR); t = _t(n)
    y = np.zeros(n)
    for dt, ph0 in ((-0.006, 0.1), (0.0, 0.5), (0.0065, 0.8)):
        ph = pitch_curve(f * (1 + dt), n, vib=0.08, vib_rate=4.7 + dt * 100, vib_delay=0.1) + ph0
        y += _fmsaw(ph, 1.4)
    return y / 3 * env_adsr(n, nOn, a=att, d=1.0, s=0.9, r=rel) * vel


def stacc_str(f, dur, vel=0.8, **k):
    n = int((dur * 0.6 + 0.25) * SR); t = _t(n)
    y = 0
    for dt in (-0.005, 0.005):
        y = y + _fmsaw(pitch_curve(f * (1 + dt), n), 1.8)
    e = np.exp(-t / 0.09) * np.minimum(1, t / 0.006)
    return y * 0.5 * e * vel


def choir(f, dur, vel=0.8, att=0.45, rel=0.8, vowel='a', **k):
    """Additive 'aah/ooh' choir pad (formant weighted harmonics, 3 detuned voices)."""
    F = {'a': [(800, 90, 1.0), (1150, 110, 0.5), (2900, 200, 0.18)],
         'o': [(450, 80, 1.0), (800, 100, 0.35), (2830, 200, 0.08)]}[vowel]
    n = int((dur + rel * 4) * SR); nOn = int(dur * SR); t = _t(n)
    y = np.zeros(n)
    kmax = int(min(5000 / f, 40))
    for v, dt in enumerate((-0.007, 0.0, 0.006)):
        ph = pitch_curve(f * (1 + dt), n, vib=0.12, vib_rate=5.2 + v * 0.4, vib_delay=0.15)
        for kk in range(1, kmax + 1):
            fk = f * kk
            w = 0.04 / kk + sum(a * np.exp(-((fk - c) / bw) ** 2) for c, bw, a in F)
            if w < 0.01:
                continue
            y += w * np.sin(TAU * kk * ph + v * 1.7 + kk)
    y /= 3
    return y * env_adsr(n, nOn, a=att, d=1.5, s=0.9, r=rel) * vel


def organ(f, dur, vel=0.8, rel=0.15, **k):
    n = int((dur + rel * 5) * SR); nOn = int(dur * SR); t = _t(n)
    ph = pitch_curve(f, n)
    y = np.zeros(n)
    for h, w in ((0.5, 0.6), (1, 1.0), (2, 0.7), (3, 0.45), (4, 0.3), (6, 0.18), (8, 0.12)):
        if f * h < 9000:
            y += w * np.sin(TAU * h * ph)
    y *= 1 + 0.15 * np.sin(TAU * 6.2 * t)
    return y * 0.35 * env_adsr(n, nOn, a=0.02, d=2, s=0.95, r=rel) * vel


def power(fs, dur, vel=0.8, mute=True, drive=5.0, **k):
    """Distorted FM power chord. fs = list of freqs."""
    dec = 0.11 if mute else 1.4
    n = int((dur + (0.1 if mute else 0.25)) * SR); nOn = int(dur * 0.95 * SR); t = _t(n)
    y = np.zeros(n)
    for f in fs:
        ph = pitch_curve(f, n)
        y += np.sin(TAU * ph + 1.8 * np.sin(TAU * ph))
    e = np.exp(-t / dec) * np.minimum(1, t / 0.002)
    e *= np.where(t < dur * 0.95, 1, np.exp(-np.maximum(t - dur * 0.95, 0) / 0.04))
    return np.tanh(drive * y / len(fs)) * e * vel


def _bassbase(f, dur, vel, I0, idec, I1, decay, rel, drive, sub=0.5, glide_from=None):
    n = int((dur + rel * 5) * SR); nOn = int(dur * 0.95 * SR); t = _t(n)
    ph = pitch_curve(f, n, glide_from=glide_from)
    I = I0 * np.exp(-t / idec) + I1
    y = np.sin(TAU * ph + I * np.sin(TAU * ph)) + sub * np.sin(TAU * ph)
    e = np.exp(-t / decay) * np.minimum(1, t / 0.0015)
    e *= np.where(t < dur * 0.95, 1, np.exp(-np.maximum(t - dur * 0.95, 0) / rel))
    return np.tanh(drive * y) / np.tanh(drive) * e * vel


def slap(f, dur, vel=0.8, ghost=False, **k):
    if ghost:
        return _bassbase(f, 0.04, vel * 0.5, 3, 0.01, 0.5, 0.03, 0.02, 1.5)
    return _bassbase(f, dur, vel, 6.0, 0.025, 0.9, 0.9, 0.04, 1.6)


def pickbass(f, dur, vel=0.8, ghost=False, **k):
    if ghost:
        return _bassbase(f, 0.05, vel * 0.5, 2, 0.02, 0.6, 0.04, 0.02, 1.4)
    return _bassbase(f, dur, vel, 2.8, 0.07, 1.1, 1.2, 0.04, 1.4)


def synbass(f, dur, vel=0.8, ghost=False, **k):
    return _bassbase(f, dur if not ghost else 0.05, vel, 1.5, 0.2, 1.6, 3.0, 0.06, 2.2, sub=0.9)


def softbass(f, dur, vel=0.8, ghost=False, **k):
    return _bassbase(f, dur if not ghost else 0.06, vel, 1.0, 0.1, 0.35, 1.5, 0.08, 1.0, sub=0.3)


def drone(f, dur, vel=0.8, **k):
    """Dark sub pedal: sine + soft saw, slow swell."""
    n = int((dur + 1.5) * SR); nOn = int(dur * SR); t = _t(n)
    ph = pitch_curve(f, n)
    y = np.sin(TAU * ph) + 0.3 * _fmsaw(ph * 2, 1.2) + 0.15 * np.sin(TAU * 3.003 * ph)
    return y * env_adsr(n, nOn, a=0.6, d=2, s=0.9, r=0.8) * vel


def timpani(f, dur, vel=0.8, **k):
    n = int(1.6 * SR); t = _t(n)
    ph = np.cumsum(f * (1 + 0.04 * np.exp(-t / 0.05))) / SR
    y = np.sin(TAU * ph) + 0.4 * np.sin(TAU * 1.5 * ph) * np.exp(-t / 0.2)
    nz = lp(_rng.standard_normal(n), 900) * np.exp(-t / 0.03) * 0.6
    return (y * np.exp(-t / 0.9) + nz) * vel


INST = dict(guitar=guitar, lead_soft=lead_soft, flute=flute, psg=psg, pluck=pluck, epiano=epiano, bell=bell,
            toll=toll, brass=brass, strings=strings, stacc_str=stacc_str, choir=choir, organ=organ,
            slap=slap, pickbass=pickbass, synbass=synbass, softbass=softbass, drone=drone, timpani=timpani)


# ---------------------------------------------------------------- drums (cached one-shots)
_dcache = {}


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def drum(name):
    if name in _dcache:
        return _dcache[name]
    if name == 'k':  # punchy FM-era kick
        n = int(0.45 * SR); t = _t(n)
        f = 52 + 120 * np.exp(-t / 0.035)
        y = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t / 0.22)
        y += 0.5 * hp(_noise(n, 1), 2000) * np.exp(-t / 0.004)
        y = np.tanh(1.6 * y)
    elif name == 's':
        n = int(0.4 * SR); t = _t(n)
        tone = np.sin(TAU * np.cumsum(185 + 60 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.07)
        nz = bp(_noise(n, 2), 900, 9000) * np.exp(-t / 0.13)
        y = np.tanh(1.4 * (0.8 * tone + 1.1 * nz))
    elif name == 'h':
        n = int(0.12 * SR); t = _t(n)
        y = hp(_noise(n, 3), 7000, 4) * np.exp(-t / 0.025) * 0.9
    elif name == 'H':
        n = int(0.5 * SR); t = _t(n)
        y = hp(_noise(n, 4), 6500, 4) * np.exp(-t / 0.18) * 0.7
    elif name == 'c':
        n = int(2.6 * SR); t = _t(n)
        nz = hp(_noise(n, 5), 4000, 2)
        ring = sum(np.sin(TAU * fr * t + i) for i, fr in enumerate((3301, 4217, 5550, 6890))) * 0.08
        y = (nz + ring) * np.exp(-t / 0.75) * 0.75
    elif name == 'r':  # ride
        n = int(1.2 * SR); t = _t(n)
        y = (hp(_noise(n, 6), 5000) * 0.35 + sum(np.sin(TAU * fr * t) for fr in (2900, 4400, 5170)) * 0.12) * np.exp(-t / 0.35)
    elif name in ('t1', 't2', 't3'):
        base = {'t1': 210, 't2': 160, 't3': 115}[name]
        n = int(0.6 * SR); t = _t(n)
        y = np.sin(TAU * np.cumsum(base * (1 + 0.6 * np.exp(-t / 0.03))) / SR) * np.exp(-t / 0.22)
        y += 0.25 * bp(_noise(n, 7), 300, 3000) * np.exp(-t / 0.03)
        y = np.tanh(1.3 * y)
    elif name == 'T':  # taiko / big cinematic drum
        n = int(1.8 * SR); t = _t(n)
        y = np.sin(TAU * np.cumsum(52 + 70 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.55)
        y += 0.5 * lp(_noise(n, 8), 1400) * np.exp(-t / 0.06)
        y = np.tanh(1.8 * y)
    elif name == 'p':  # clap / rim
        n = int(0.3 * SR); t = _t(n)
        env = sum(np.exp(-np.maximum(t - d, 0) / 0.008) * (t >= d) for d in (0, 0.009, 0.018)) + np.exp(-np.maximum(t - 0.027, 0) / 0.08) * (t >= 0.027)
        y = bp(_noise(n, 9), 900, 5000) * env * 0.6
    elif name == 'b':  # boom / sub impact
        n = int(3.0 * SR); t = _t(n)
        y = np.sin(TAU * np.cumsum(32 + 60 * np.exp(-t / 0.12)) / SR) * np.exp(-t / 1.1)
        y += 0.35 * lp(_noise(n, 10), 500) * np.exp(-t / 0.3)
        y = np.tanh(1.5 * y)
    elif name == 'sh':  # shaker / bell tambourine for towns
        n = int(0.15 * SR); t = _t(n)
        y = hp(_noise(n, 11), 5000) * (np.minimum(1, t / 0.01) * np.exp(-t / 0.04)) * 0.6
    elif name == 'cb':  # small camel bell / triangle
        n = int(0.8 * SR); t = _t(n)
        y = (np.sin(TAU * 1830 * t) + 0.6 * np.sin(TAU * 2740 * t)) * np.exp(-t / 0.25) * 0.35
    elif name == 'an':  # anvil (forge)
        n = int(1.4 * SR); t = _t(n)
        y = sum(a * np.sin(TAU * fr * t) * np.exp(-t / d) for fr, a, d in ((1180, 1, .5), (2950, .6, .3), (4120, .4, .2), (6100, .25, .1)))
        y = y * 0.4 + 0.4 * hp(_noise(n, 12), 3000) * np.exp(-t / 0.01)
    else:
        raise KeyError(name)
    y = y.astype(np.float64)
    _dcache[name] = y
    return y


# drum default pans/levels/reverb sends
DRUM_MIX = {'k': (0.0, 1.0, 0.03), 's': (0.05, 0.75, 0.22), 'h': (0.3, 0.32, 0.03), 'H': (0.3, 0.3, 0.05),
            'c': (-0.35, 0.42, 0.12), 'r': (0.35, 0.3, 0.06), 't1': (0.3, 0.7, 0.18), 't2': (0.0, 0.7, 0.18),
            't3': (-0.3, 0.75, 0.18), 'T': (-0.1, 0.95, 0.35), 'p': (-0.1, 0.55, 0.2), 'b': (0.0, 0.9, 0.3),
            'sh': (0.4, 0.35, 0.05), 'cb': (-0.4, 0.4, 0.2), 'an': (0.25, 0.45, 0.25)}


# ---------------------------------------------------------------- effects
def reverb_ir(rt60=1.8, damp=6000, predelay=0.018, seed=21):
    n = int(rt60 * 1.1 * SR); t = _t(n)
    out = []
    for ch in range(2):
        nz = np.random.default_rng(seed + ch).standard_normal(n)
        nz = lp(nz, damp, 1)
        ir = nz * np.exp(-6.9 * t / rt60) * np.minimum(1, t / 0.008)
        ir = np.concatenate([np.zeros(int(predelay * SR)), ir])
        out.append(ir / np.sqrt((ir ** 2).sum()))
    return np.stack(out) * 0.9


def delay_ir(dly, fb=0.38, taps=6):
    n = int(dly * taps * SR) + 1
    ir = np.zeros((2, n))
    for k in range(1, taps + 1):
        i = int(round(dly * k * SR))
        if i < n:
            ir[(k + 1) % 2, i] = fb ** (k - 1)  # ping-pong
    return ir


def conv_stereo(x, ir):
    return np.stack([fftconvolve(x[c], ir[c])[:x.shape[1]] for c in range(2)])


def pan2(y, pan):
    a = (pan + 1) * np.pi / 4
    return np.stack([y * np.cos(a), y * np.sin(a)])
