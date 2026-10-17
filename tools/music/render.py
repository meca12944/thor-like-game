#!/usr/bin/env python3
"""Render BGM songs -> seamless-loop .ogg files + bgm.json manifest.

usage:  python3 tools/music/render.py [song_id ...] [--wav] [--out audio/bgm]
Each song in tools/music/songs/<id>.py defines SONG (see README.md).
Loop data: the file = intro + loop body.  loopStart/loopEnd (seconds, sample exact) are written to
bgm.json and to the Vorbis comments LOOPSTART / LOOPLENGTH (samples, RPG-Maker style).
"""
import sys, os, json, importlib.util, subprocess, glob, time
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.ndimage import minimum_filter1d, uniform_filter1d
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import synth as S
import score as SC

SR = S.SR
TAIL = 3.5  # seconds of release/reverb rendered past a region end
TARGET_LUFS = -14.0
CEIL = 10 ** (-1.2 / 20)


def load_song(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.SONG


def render_region(song, which):
    ev, steps, sps, chmap = SC.build(song, which)
    if steps == 0:
        return None, 0
    n_body = int(round(steps * sps * SR))
    N = n_body + int(TAIL * SR)
    dry = np.zeros((2, N)); rev = np.zeros((2, N)); dly = np.zeros((2, N))
    for cname, cfg in chmap.items():
        evs = ev.get(cname)
        if not evs:
            continue
        buf = np.zeros(N)
        if cfg['type'] == 'drums':
            for e in evs:
                dn = e['dn']; smp = S.drum(dn)
                i = int(round(e['t'] * SR)); j = min(N, i + len(smp))
                pan, g, rs = S.DRUM_MIX[dn]
                g *= song.get('drum_gain', {}).get(dn, 1.0)
                seg = smp[:j - i] * e['v'] * g * cfg['gain']
                st = S.pan2(seg, pan)
                dry[:, i:j] += st
                rev[:, i:j] += st * rs * (cfg.get('rev', 0.15) / 0.15)
            continue
        fn = S.INST[cfg['inst']] if cfg['inst'] != 'power' else None
        opt = cfg.get('opt', {})
        for e in evs:
            i = int(round(e['t'] * SR))
            if i >= N:
                continue
            if cfg['inst'] == 'power':
                y = S.power([S.mtof(m) for m in e['ms']], e['d'], e['v'], mute=e.get('mute', True), **opt)
            elif 'ms' in e:  # chord on a melodic instrument (stabs / strums)
                y = None
                for k, m in enumerate(e['ms']):
                    yy = fn(S.mtof(m), e['d'], e['v'] * 0.6, **opt)
                    off = int(k * cfg.get('strum', 0.0) * SR)
                    yy = np.concatenate([np.zeros(off), yy])
                    if y is None: y = yy
                    else:
                        L = max(len(y), len(yy)); y = np.pad(y, (0, L - len(y))) + np.pad(yy, (0, L - len(yy)))
            else:
                kw = dict(opt)
                for k2 in ('bend', 'stacc', 'ghost'):
                    if e.get(k2): kw[k2] = e[k2]
                if e.get('glide'):
                    kw['glide_from'] = e['glide']
                f = S.mtof(e['m'] + cfg.get('transpose', 0))
                try:
                    y = fn(f, e['d'], e['v'], **kw)
                except TypeError:
                    kw.pop('glide_from', None); y = fn(f, e['d'], e['v'], **kw)
            j = min(N, i + len(y))
            buf[i:j] += y[:j - i]
        if cfg.get('hp'): buf = S.hp(buf, cfg['hp'])
        if cfg.get('lp'): buf = S.lp(buf, cfg['lp'])
        buf *= cfg['gain']
        st = S.pan2(buf, cfg.get('pan', 0))
        if cfg.get('double'):  # stereo double-tracking (rhythm guitar)
            d = int(0.013 * SR)
            other = S.pan2(np.concatenate([np.zeros(d), buf[:-d]]) * 0.9, -cfg.get('pan', 0) or cfg['double'])
            st = st * 0.8 + other * 0.8
        dry += st
        rev += st * cfg.get('rev', 0)
        dly += st * cfg.get('dly', 0)
    beat = 60.0 / song['bpm']
    d_ir = S.delay_ir(song.get('delay', 0.75) * beat, fb=song.get('delay_fb', 0.35))
    dl = S.conv_stereo(dly, d_ir) * 0.55
    rev += dl * 0.4
    r_ir = S.reverb_ir(song.get('rt60', 1.8), song.get('damp', 6500))
    wet = S.conv_stereo(rev, r_ir) * song.get('wet', 1.0)
    mix = dry + dl + wet
    mix = S.hp(mix, 28)
    return mix, n_body


def master(song, intro, loop, nI, nL):
    """returns final stereo array (intro body + loop body), gain-matched and peak-limited."""
    parts = []
    if loop is not None:
        L = loop[:, :nL].copy()
        tail = loop[:, nL:]
        k = 0
        while k < tail.shape[1]:  # fold the loop tail circularly onto the loop start
            seg = tail[:, k:k + nL]; L[:, :seg.shape[1]] += seg; k += nL
        meas = L
    else:
        meas = intro
    meter = pyln.Meter(SR)
    lufs = meter.integrated_loudness(meas.T)
    g = 10 ** ((song.get('lufs', TARGET_LUFS) - lufs) / 20)
    if loop is not None:
        I = intro[:, :nI] * g if intro is not None else np.zeros((2, 0))
        cat = np.concatenate([I, L * g, L * g, L * g], axis=1)
        y = limit(cat)
        out = np.concatenate([y[:, :nI], y[:, nI + nL:nI + 2 * nL]], axis=1)
    else:
        y = limit(intro * g)
        # trim trailing silence
        a = np.abs(y).max(0); nz = np.nonzero(a > 1e-4)[0]
        y = y[:, :nz[-1] + int(0.1 * SR)] if len(nz) else y
        fade = int(0.08 * SR); y[:, -fade:] *= np.linspace(1, 0, fade)
        out = y
    return out, lufs


def limit(x, la=0.006):
    W = int(la * SR)
    pk = np.abs(x).max(0)
    # oversampled peak estimate for intersample safety
    g_raw = np.minimum(1.0, CEIL / np.maximum(pk * 1.05, 1e-9))
    g = minimum_filter1d(g_raw, 2 * W + 1)
    g = uniform_filter1d(g, W | 1)
    g = minimum_filter1d(g, 3)
    # slower release smoothing (never above the fast curve)
    rel = uniform_filter1d(minimum_filter1d(g, int(0.05 * SR)), int(0.05 * SR))
    g = np.minimum(g, np.maximum(rel, g * 0.0 + rel))
    y = x * g
    return np.clip(y, -CEIL, CEIL)


def render_song(path, outdir, wav=False):
    t0 = time.time()
    song = load_song(path)
    sid = song['id']
    intro, nI = render_region(song, 'intro') if song.get('intro') else (None, 0)
    if song.get('loop'):
        loop, nL = render_region(song, 'loop')
    else:
        loop, nL = None, 0
    out, lufs_raw = master(song, intro, loop, nI, nL)
    # stats
    meter = pyln.Meter(SR)
    lufs = meter.integrated_loudness(out.T)
    tp = 20 * np.log10(np.abs(resample_poly(out, 4, 1, axis=1)).max() + 1e-12)
    wavp = os.path.join(outdir, sid + '.wav') if wav else '/tmp/_bgm_%s.wav' % sid
    sf.write(wavp, out.T.astype(np.float32), SR, subtype='FLOAT')
    oggp = os.path.join(outdir, sid + '.ogg')
    meta = ['-metadata', 'title=' + song['title'], '-metadata', 'artist=thor-like-game BGM (original)']
    if loop is not None:
        meta += ['-metadata', 'LOOPSTART=%d' % nI, '-metadata', 'LOOPLENGTH=%d' % nL]
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wavp, '-c:a', 'libvorbis', '-q:a', str(song.get('q', 1))] + meta + [oggp], check=True)
    if not wav:
        os.remove(wavp)
    info = dict(id=sid, file=sid + '.ogg', title=song['title'], en=song.get('en', ''), bpm=song['bpm'],
                key=song['key'] + ' ' + song.get('mode', 'minor'), loop=loop is not None,
                loopStart=round(nI / SR, 6), loopEnd=round((nI + nL) / SR, 6), duration=round(out.shape[1] / SR, 3),
                lufs=round(lufs, 1), truePeak=round(tp, 2), bytes=os.path.getsize(oggp))
    print('%-22s %5.1fs loop %s %6.1f LUFS tp %5.2f dB  %4d KB  (%.1fs)' % (sid, info['duration'], info['loop'], lufs, tp, info['bytes'] // 1024, time.time() - t0), flush=True)
    return info


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    wav = '--wav' in sys.argv
    outdir = os.path.join(HERE, '..', '..', 'audio', 'bgm')
    for a in sys.argv:
        if a.startswith('--out='): outdir = a[6:]
    outdir = os.path.abspath(outdir); os.makedirs(outdir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(HERE, 'songs', '*.py')))
    files = [f for f in files if not os.path.basename(f).startswith('_')]
    if args:
        files = [f for f in files if os.path.basename(f)[:-3] in args]
    man_p = os.path.join(outdir, 'bgm.json')
    man = json.load(open(man_p)) if os.path.exists(man_p) else {}
    for f in files:
        info = render_song(f, outdir, wav)
        if man.get(info['id'], {}).get('userSupplied'): info['id'] += 'Alt'   # never overwrite a user-supplied track entry
        man[info['id']] = info
    json.dump(dict(sorted(man.items())), open(man_p, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
