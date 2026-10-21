"""Try every subset (size 0-3) of the 5 seam frames appended after the 8 base frames, post-process each, keep the smoothest loop.
side (mode foot): minimise the planted-foot slip sum; diagonal (mode fixed:N): minimise the largest silhouette change relative to the average.
python3 pick_seam.py <motion> <dir> <speed> <mode>  -> anim/<motion>/<dir>_final (+ choice.json)"""
import sys, os, shutil, subprocess, itertools, re, json
m, d, sp, mode = sys.argv[1:5]
T = '/tmp/claude-0/-home-user-thor-like-game/16277cc3-67c1-5ded-80dc-465b39d4f5af/scratchpad/pick'
base = [f'anim/{m}/{d}/{i:03d}.png' for i in range(8)]; import glob; seam = sorted(glob.glob(f'anim/seam/{m}_{d}/seam_*.png'))
best = None
for opt in [()] + [c for r in (1, 2, 3) for c in itertools.combinations(range(len(seam)), r)]:
    tag = '_'.join(map(str, opt)) or 'none'; raw = f'{T}/{m}_{d}/raw_{tag}'; post = raw.replace('raw_', 'post_')
    shutil.rmtree(raw, ignore_errors=True); os.makedirs(raw); shutil.rmtree(post, ignore_errors=True)
    for k, f in enumerate(base + [seam[i] for i in opt]): shutil.copy(f, f'{raw}/{k:03d}.png')
    subprocess.run(['python3', '-I', 'post_run.py', raw, post, sp, mode], capture_output=True)
    out = subprocess.run(['python3', '-I', 'check_run.py', post, 'json', sp, post + '_chk'], capture_output=True, text=True).stdout
    slip = float(re.search(r'sum ([\d.]+)', out).group(1)); ch = json.loads(re.search(r'silhouette change i->i\+1 (\[.*?\])', out).group(1))
    avg = sum(ch) / len(ch); peak = max(ch) / avg
    score = slip if mode == 'foot' else peak
    if best is None or score < best[0]: best = (score, opt, post, slip, round(peak, 2))
score, opt, post, slip, peak = best; dst = f'anim/{m}/{d}_final'; shutil.rmtree(dst, ignore_errors=True); shutil.copytree(post, dst)
json.dump({'seam_frames': list(opt), 'slip_sum': slip, 'peak_change_over_avg': peak, 'mode': mode, 'speed': float(sp)}, open(f'{dst}/choice.json', 'w'))
print(m, d, 'seam', opt, 'slip', slip, 'peak/avg', peak)
