"""Idle fix without credits: keep the first K frames (the calm part, before PixelLab starts turning the head / body) and play them
back and forth: 0,1,..,K-1,..,1 -> no seam jump. Input = post_run idle output. python3 idle_pingpong.py <post dir> <out dir> [K=4] [ticks=8] [first frame=0]"""
import sys, os, json, shutil
SRC, OUT = sys.argv[1], sys.argv[2]; K = int(sys.argv[3]) if len(sys.argv) > 3 else 4; TK = int(sys.argv[4]) if len(sys.argv) > 4 else 8; S0 = int(sys.argv[5]) if len(sys.argv) > 5 else 0
seq = [S0 + i for i in list(range(K)) + list(range(K - 2, 0, -1))]; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
for i, s in enumerate(seq): shutil.copy(os.path.join(SRC, f'{s:03d}.png'), os.path.join(OUT, f'{i:03d}.png'))
json.dump({'ticks': [TK] * len(seq), 'source_frames': seq, 'cycle_ticks': TK * len(seq)}, open(os.path.join(OUT, 'timing.json'), 'w'))
print(OUT, seq)
