# Put an existing side-view motion onto the diagonal sprite (owner 10-20: "아까 만들어 놓은거에 입히면 되지"):
# diagonal keypoints(t) = diagonal still keypoints + S * (side keypoints(t) - side keypoints(0)); S squeezes x (3/4 view) a little.
# usage: diag_from_side.py <side_seq.json> <diag_start_kp.json> <out.json> [sx=0.8]
import json,sys
seq=json.load(open(sys.argv[1])); D={p['label']:p for p in json.load(open(sys.argv[2]))['keypoints']}; sx=float(sys.argv[4]) if len(sys.argv)>4 else 0.8
S0={p['label']:p for p in seq[0]}; out=[]
for f in seq:
    F={p['label']:p for p in f}; fr=[]
    for k,d in D.items():
        if k not in F: continue
        fr.append({'x':min(1,max(0,d['x']+sx*(F[k]['x']-S0[k]['x']))),'y':min(1,max(0,d['y']+(F[k]['y']-S0[k]['y']))),'label':k,'z_index':int(d.get('z_index',0))})
    out.append(fr)
json.dump(out,open(sys.argv[3],'w')); print(len(out),'frames')
