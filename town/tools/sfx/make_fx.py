"""Copy docs_music/sfx_draft/*.ogg -> town/assets/sfx/fx/ (+ .m4a AAC for Safari). Hit/hurt drafts with long reverb tails are
trimmed + faded to short in-game versions. Prints peak / LUFS per file. Run: python3 town/tools/sfx/make_fx.py"""
import glob, os, subprocess, json
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')); SRC = R + '/docs_music/sfx_draft/'; DST = R + '/town/assets/sfx/fx/'
TRIM = {'hit_normal': .22, 'hit_finisher': .45, 'hit_critical': .45, 'player_hurt': .3, 'combo_hit': .1}  # seconds kept (last 40% faded)
def meas(f):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(r.rsplit('I:', 1)[1].split('LUFS')[0]), float(r.rsplit('Peak:', 1)[1].split('dBFS')[0])
os.makedirs(DST, exist_ok=True)
for f in glob.glob(DST + '*'): os.remove(f)
for src in sorted(glob.glob(SRC + '*.ogg')):
    k = os.path.basename(src)[:-4]; o = DST + k + '.ogg'
    if k in TRIM:
        t = TRIM[k]; af = f'atrim=0:{t},afade=t=out:st={t*.6:.3f}:d={t*.4:.3f}'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-af', af, '-c:a', 'libvorbis', '-q:a', '4', o], check=True)
    else: subprocess.run(['cp', src, o], check=True)
    I0, P0 = meas(o); g = min(-1.0 - P0, (-14.0 - I0) if I0 > -60 else 0.0)  # only attenuate: true peak <= -1 dBTP, loudness <= -14 LUFS
    if g < -0.3:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', o, '-af', f'volume={g:.2f}dB', '-c:a', 'libvorbis', '-q:a', '4', o + '.tmp.ogg'], check=True); os.replace(o + '.tmp.ogg', o)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', o, '-c:a', 'aac', '-b:a', '64k', DST + k + '.m4a'], check=True)
    I, P = meas(o); rms = subprocess.run(['ffmpeg', '-hide_banner', '-i', o, '-af', 'astats=measure_overall=RMS_level:measure_perchannel=0', '-f', 'null', '-'], capture_output=True, text=True).stderr.rsplit('RMS level dB:', 1)[1].split()[0]
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', o], capture_output=True, text=True).stdout)
    print(f'{k:20s} {d:5.2f}s  I={I:6.1f} LUFS (-70 = too short to gate)  RMS={rms:>6s} dB  truePeak={P:5.1f} dBTP' + ('  TRIMMED' if k in TRIM else '') + (f'  gain {g:+.1f} dB' if g < -0.3 else ''))
