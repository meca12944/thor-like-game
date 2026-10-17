"""Per-sheet hero proportion measurement on the SOURCE strips (src/hero/anim_raw): head height (crown->chin, skin taper)
for front/side frames, head width (widest row in the top band) for every frame, standing height.  Used to normalise
every animation sheet to the FRONT idle frame (idle3 #0)."""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import load_frames, body, crown_sole, chin_auto
RAW = '/workspace/town-demo/src/hero/anim_raw/'
C = json.load(open('/workspace/town-demo/tools/anim/hero_anim.src.json'))
def head_w(m, crown, H):
    w = 0
    for y in range(crown, crown + int(H * .2)):
        xx = np.where(m[y])[0]
        if len(xx): w = max(w, xx[-1] - xx[0] + 1)
    return w
def view_of(k, f):
    fn = C['sheets'][k]['file']
    return 'back' if '_up' in fn else 'side' if ('right' in fn or 'spin' in fn or fn.startswith('hurt')) else 'front'
if __name__ == '__main__':
    out = {}
    for k, s in C['sheets'].items():
        fr = load_frames(RAW + s['file'] + '.jpg', s['n']); R = []
        for i, f in enumerate(fr):
            m = body(f, 'hero'); c0, c3 = crown_sole(m, 3); H = c3 - c0 + 1
            ch = chin_auto(f, m, c0, c3)
            R.append(dict(i=i, crown=c0, sole=c3, H=H, chin=ch, head=(ch - c0) if ch else None, headW=head_w(m, c0, H)))
        heads = [r['head'] for r in R if r['head']]; hw = [r['headW'] for r in R]
        out[k] = dict(file=s['file'], n=s['n'], ref=s['ref'], refFactor=s.get('refFactor', 1), frames=R,
                      head_med=float(np.median(heads)) if heads else None, headW_med=float(np.median(hw)), refH=R[s['ref']]['H'])
        print(k, s['file'], 'headmed', out[k]['head_med'], 'headWmed', out[k]['headW_med'], 'refH', out[k]['refH'], 'rf', s.get('refFactor', 1))
    json.dump(json.loads(json.dumps(out, default=float)), open('/workspace/town-demo/style_sample/work/hero_sheet_meas.json', 'w'))
