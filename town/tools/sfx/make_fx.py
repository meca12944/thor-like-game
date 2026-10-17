"""Copy docs_music/sfx_draft/*.ogg -> town/assets/sfx/fx/ (+ .m4a AAC for Safari). Hit/hurt drafts with long reverb tails are
trimmed + faded to short in-game versions. Prints peak / LUFS per file. Run: python3 town/tools/sfx/make_fx.py

Drafts are pre-leveled (1s-pad ebur128): SFX -14 LUFS, UI -17, footsteps -18, swing 1/2 -16 vs swing 3 -14 (~2.2 dB).
This script does not re-LUFS; it only peak-limits to <= -1 dBTP (vorbis can raise true peak after trim).
"""
import glob, os, subprocess, tempfile
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')); SRC = R + '/docs_music/sfx_draft/'; DST = R + '/town/assets/sfx/fx/'
TRIM = {'hit_normal': .22, 'hit_finisher': .45, 'hit_critical': .45, 'player_hurt': .3, 'combo_hit': .1}  # seconds kept (last 40% faded)
def meas(f):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(r.rsplit('I:', 1)[1].split('LUFS')[0]), float(r.rsplit('Peak:', 1)[1].split('dBFS')[0])
def encode_ogg(src, dst, af=None, gain_db=0.0):
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-i', src]
    filters = []
    if af: filters.append(af)
    if abs(gain_db) > 0.05: filters.append(f'volume={gain_db:.2f}dB')
    if filters: cmd += ['-af', ','.join(filters)]
    cmd += ['-c:a', 'libvorbis', '-q:a', '4', dst]
    subprocess.run(cmd, check=True)
os.makedirs(DST, exist_ok=True)
for f in glob.glob(DST + '*'): os.remove(f)
for src in sorted(glob.glob(SRC + '*.ogg')):
    k = os.path.basename(src)[:-4]; o = DST + k + '.ogg'; g = 0.0
    if k in TRIM:
        t = TRIM[k]; af = f'atrim=0:{t},afade=t=out:st={t*.6:.3f}:d={t*.4:.3f}'
        # trim to wav first so peak limit is applied once before a single vorbis encode
        wav = o + '.trim.wav'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-af', af, wav], check=True)
        _, Pw = meas(wav)
        # ~0.3–1.5 dB codec headroom: vorbis often raises true peak vs PCM
        g = min(0.0, -1.2 - Pw)
        for extra in (0.0, 0.3, 0.6, 1.0, 1.5):
            encode_ogg(wav, o, gain_db=g - extra)
            _, Po = meas(o)
            if Po <= -1.0:
                g = g - extra
                break
        os.remove(wav)
    else:
        subprocess.run(['cp', src, o], check=True)
        for _ in range(5):
            _, P0 = meas(o)
            if P0 <= -1.0: break
            g = -1.05 - P0
            encode_ogg(o, o + '.tmp.ogg', gain_db=g); os.replace(o + '.tmp.ogg', o)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', o, '-c:a', 'aac', '-b:a', '64k', DST + k + '.m4a'], check=True)
    I, P = meas(o); rms = subprocess.run(['ffmpeg', '-hide_banner', '-i', o, '-af', 'astats=measure_overall=RMS_level:measure_perchannel=0', '-f', 'null', '-'], capture_output=True, text=True).stderr.rsplit('RMS level dB:', 1)[1].split()[0]
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', o], capture_output=True, text=True).stdout)
    print(f'{k:20s} {d:5.2f}s  I={I:6.1f} LUFS (-70 = too short to gate)  RMS={rms:>6s} dB  truePeak={P:5.1f} dBTP' + ('  TRIMMED' if k in TRIM else '') + (f'  gain {g:+.1f} dB' if g < -0.05 else ''))
