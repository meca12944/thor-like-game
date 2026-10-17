#!/usr/bin/env python3
"""Listen-check helpers: decode each .ogg, verify loop seam, clipping, loudness; optional spectrogram png."""
import sys, json, os, subprocess
import numpy as np, soundfile as sf, pyloudnorm as pyln

def decode(p):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', '44100', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T

def main():
    d = sys.argv[1]
    man = json.load(open(os.path.join(d, 'bgm.json')))
    ids = sys.argv[2:] or list(man)
    tot = 0
    for sid in ids:
        m = man[sid]; x = decode(os.path.join(d, m['file'])); sr = 44100
        tot += m['bytes']
        peak = 20 * np.log10(np.abs(x).max())
        clip = int((np.abs(x) > 0.999).sum())
        lufs = pyln.Meter(sr).integrated_loudness(x.T)
        s = ''
        if m['loop']:
            a, b = int(round(m['loopStart'] * sr)), int(round(m['loopEnd'] * sr))
            b = min(b, x.shape[1])
            # seam: jump between last sample of loop and first sample of loop vs typical adjacent-sample jump
            jump = np.abs(x[:, b - 1] - x[:, a]).max()
            typ = np.percentile(np.abs(np.diff(x[:, a:b], axis=1)).max(0), 99.9)
            # spectral continuity: rms of 20ms windows across seam
            w = int(0.02 * sr)
            r1 = np.sqrt((x[:, b - w:b] ** 2).mean()); r2 = np.sqrt((x[:, a:a + w] ** 2).mean())
            s = 'seam jump %.4f (p99.9 %.4f) rms %.3f->%.3f %s' % (jump, typ, r1, r2, 'OK' if jump <= typ * 1.5 else 'CHECK')
        print('%-22s %5.1fs peak %6.2f dB clip %d  %5.1f LUFS  %s' % (sid, x.shape[1] / sr, peak, clip, lufs, s))
    print('total %.2f MB' % (tot / 1e6))

if __name__ == '__main__':
    main()
