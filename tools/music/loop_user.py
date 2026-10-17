#!/usr/bin/env python3
"""Convert a user-supplied (Gemini) track to a looping BGM ogg, following the BGM.md drop-in procedure:
decode -> gain down only if peak > -1.0 dBFS -> beat grid (librosa) -> best 4-bar-boundary pair (s,e) after the intro and
before the fade by 3 s mel-spectrum similarity around the boundaries -> refine e by +-40 ms waveform correlation ->
60 ms equal-power crossfade of the tail into the audio just before s -> cut at e -> Ogg Vorbis q6.
usage: loop_user.py in.mp3 out.ogg [min_loop_s] ; prints JSON with loopStart/loopEnd/bpm/bars."""
import sys, json, subprocess, numpy as np, librosa, soundfile as sf, pyloudnorm as pyln
src, out = sys.argv[1], sys.argv[2]; MINLOOP = float(sys.argv[3]) if len(sys.argv) > 3 else 60
y, sr = librosa.load(src, sr=44100, mono=False); y = np.atleast_2d(y)
pk = np.abs(y).max(); lim = 10 ** (-1.0 / 20)  # -1 dBFS: room for Vorbis overshoot (at -0.3 one track clipped after encoding)
if pk > lim: y = y * (lim / pk)
m = y.mean(0); dur = len(m) / sr
# beat grid from low-band onsets
lo = librosa.effects.preemphasis(m, coef=-0.97)
tempo, beats = librosa.beat.beat_track(y=m, sr=sr, hop_length=512, units='samples')
bpm = float(np.atleast_1d(tempo)[0])
# fade start: last time the 2 s rms is within 6 dB of the median
hop = sr // 2; rms = np.array([np.sqrt(np.mean(m[i:i + 2 * sr] ** 2) + 1e-12) for i in range(0, len(m) - 2 * sr, hop)])
med = np.median(rms); ok = np.where(rms > med / 2)[0]; fade = ok[-1] * 0.5 if len(ok) else dur
first = ok[0] * 0.5 if len(ok) else 0
M = librosa.power_to_db(librosa.feature.melspectrogram(y=m, sr=sr, hop_length=1024, n_mels=64))
fr = lambda s: int(s / 1024)
W = fr(3 * sr)
def feat(i, side):
    a = fr(i); seg = M[:, a - W:a] if side < 0 else M[:, a:a + W]
    return seg.flatten() if seg.shape[1] == W else None
best = None
bt = beats[(beats > 6 * sr) & (beats < (fade - 3) * sr)]
for si in range(len(bt)):
    s = bt[si]
    if s / sr < max(first, 6): continue
    fs_b, fs_a = feat(s, -1), feat(s, 1)
    if fs_b is None or fs_a is None: continue
    for ei in range(si + 16, len(bt), 16):
        e = bt[ei]
        if (e - s) / sr < MINLOOP: continue
        fe_b, fe_a = feat(e, -1), feat(e, 1)
        if fe_b is None or fe_a is None: continue
        c = np.corrcoef(fs_a, fe_a)[0, 1] + np.corrcoef(fs_b, fe_b)[0, 1]
        sc = c + 0.002 * (e - s) / sr  # slight preference for longer loops
        if best is None or sc > best[0]: best = (sc, s, e, (ei - si) // 4, c / 2)
_, s, e, bars, sim = best
# refine e by waveform correlation (+-40 ms) of the 50 ms after e vs after s
R = int(0.04 * sr); L = int(0.05 * sr); ref = m[s:s + L]
cs = [np.dot(m[e + d:e + d + L], ref) / (np.linalg.norm(m[e + d:e + d + L]) * np.linalg.norm(ref) + 1e-9) for d in range(-R, R + 1)]
e = e + int(np.argmax(cs)) - R
X = int(0.06 * sr); outa = y[:, :e].copy()
t = np.linspace(0, np.pi / 2, X)
outa[:, e - X:e] = outa[:, e - X:e] * np.cos(t) + y[:, s - X:s] * np.sin(t)
sf.write('/tmp/_lu.wav', outa.T, sr)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', '/tmp/_lu.wav', '-c:a', 'libvorbis', '-q:a', '6', out], check=True)
# seam test: render loop x2 and measure the jump at the seam
two = np.concatenate([outa[:, :e], outa[:, s:e], outa[:, s:e]], 1)
sf.write(out.replace('.ogg', '_seamx2.wav') if '--seam' in sys.argv else '/tmp/_seam.wav', two.T, sr)
mm = outa.mean(0); jump = abs(mm[s] - mm[e - 1]); typ = np.percentile(np.abs(np.diff(mm)), 99.9)
meter = pyln.Meter(sr)
print(json.dumps({'bpm': round(bpm, 1), 'loopStart': round(s / sr, 6), 'loopEnd': round(e / sr, 6), 'duration': round(e / sr, 3), 'loopBars': int(bars),
  'seamSim': round(float(sim), 3), 'seamJump': round(float(jump), 4), 'p999diff': round(float(typ), 4), 'fadeAt': float(fade),
  'lufs': round(float(meter.integrated_loudness(outa.T)), 1), 'peakDb': round(float(20 * np.log10(np.abs(outa).max())), 2)}))
