# 주인공 점검 (팀장·사장님 10-25 「주인공도 몹처럼 자동 점검표, 빨간 칸 있으면 main 못 들어감」).
#   python3 test128/tools/hero_check.py [base_url=http://127.0.0.1:8931] [out.png]
#   reads the hero atlas the game really uses (__game.H8: anims[name] = [[sheet, cell, ticks], ...], cells[sheet][cell] = [x,y,w,h,ax,ay])
#   and the code timing (__world.heroTiming(): attack length / blade-hit tick, dodge length, jump length), measures the art in the page, saves a table image.
#   red = below the standard: frame count (walk·run 8, dodge 5, attack 4 (a one-frame attack is labelled 몸 그림 없음, still red), hurt 3, jump 5) / any frame under 3 ticks /
#   art length vs code length (attack·dodge·jump, more than 3 ticks apart) / the widest (= striking) frame not on the blade-hit tick (8/8/11, ±2) /
#   run: head bob 4~6 px and foot swing >= 15 px (atlas px, figure about 124~144 px tall).
import json, os, sys, subprocess
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8931'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/hero_check.png'
MIN_N = {'walk': 8, 'run': 8, 'dash': 5, 'hit1': 4, 'hit2': 4, 'hit3': 4, 'hurt': 3, 'jump': 5}
MEASURE = r"""async () => {
  const H = __game.H8, T = __world.heroTiming(), V = window.__v || (u => u), out = [];
  const imgs = await Promise.all(H.sheets.map(s => new Promise(r => { const im = new Image(); im.onload = () => r(im); im.onerror = () => r(null); im.src = V('assets/' + s); })));
  const cv = document.createElement('canvas'), g = cv.getContext('2d', { willReadFrequently: true });
  function box(f) { const im = imgs[f[0]], c = H.cells[f[0]] && H.cells[f[0]][f[1]]; if (!im || !c) return null; const [x, y, w, h, ax, ay] = c; cv.width = w; cv.height = h; g.clearRect(0, 0, w, h); g.drawImage(im, x, y, w, h, 0, 0, w, h);
    const d = g.getImageData(0, 0, w, h).data; let top = h, l = w, r = -1, fl = w, fr = -1; const band = Math.round(h * .12);
    for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) if (d[(yy * w + xx) * 4 + 3] > 40) { if (yy < top) top = yy; if (xx < l) l = xx; if (xx > r) r = xx; if (yy >= ay - band && yy <= ay) { if (xx < fl) fl = xx; if (xx > fr) fr = xx; } }
    return { top: top - ay, wide: r - l, reach: Math.max(ax - l, r - ax), foot: fr >= fl ? fr - fl : 0 }; }
  for (const name of Object.keys(H.anims)) { const m = name.match(/^(walk|run|dash|hit1|hit2|hit3|hurt|jump)_(down|up|right|left|dr|n)$/); if (!m || m[2] === 'left') continue;
    const fr = H.anims[name], ticks = fr.map(f => f[2] || 0), sum = ticks.reduce((a, b) => a + b, 0), bx = fr.map(box);
    const row = { name, act: m[1], dir: m[2], n: fr.length, minT: Math.min(...ticks), sum, ticks };
    if (/^hit/.test(m[1])) { const i = +m[1][3] - 1; row.code = Math.round(T.atk[i]); row.hitCode = Math.round(T.hit[i]); let best = -1, bi = 0; bx.forEach((b, k) => { if (b && b.reach > best) { best = b.reach; bi = k; } }); row.strike = ticks.slice(0, bi).reduce((a, b) => a + b, 0); }
    if (m[1] === 'dash') row.code = Math.round(T.dash); if (m[1] === 'jump') row.code = Math.round(T.jump);
    if (m[1] === 'run' || m[1] === 'walk') { const tops = bx.filter(Boolean).map(b => b.top), ft = bx.filter(Boolean).map(b => b.foot); row.bob = Math.max(...tops) - Math.min(...tops); row.footSwing = Math.max(...ft) - Math.min(...ft); }
    out.push(row); }
  return out; }"""
def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('PW_CHROME') or '/opt/pw-browsers/chromium'); pg = b.new_page(viewport={'width': 960, 'height': 540}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + '/index.html?nosave&worldreset&noscene&go=field_felt'); pg.wait_for_function('window.__world&&__world.heroTiming&&window.__game&&__game.H8', timeout=90000); pg.wait_for_timeout(1500)
        rows = pg.evaluate(MEASURE); b.close()
    order = {'walk': 0, 'run': 1, 'dash': 2, 'jump': 3, 'hit1': 4, 'hit2': 5, 'hit3': 6, 'hurt': 7}; dorder = {'down': 0, 'dr': 1, 'right': 2, 'n': 3, 'up': 4}
    rows.sort(key=lambda r: (order[r['act']], dorder.get(r['dir'], 9)))
    for r in rows:
        bad = {}
        bad['n'] = r['n'] < MIN_N[r['act']]
        bad['minT'] = r['minT'] < 3
        if 'code' in r: bad['sum'] = abs(r['sum'] - r['code']) > 3
        if 'hitCode' in r: bad['strike'] = abs(r['strike'] - r['hitCode']) > 2
        if r['act'] == 'run': bad['bob'] = not (4 <= r['bob'] <= 6); bad['footSwing'] = r['footSwing'] < 15
        r['bad'] = bad; r['red'] = sum(1 for v in bad.values() if v)
    f = subprocess.run(['fc-match', '-f', '%{file}', ':lang=ko'], capture_output=True, text=True).stdout or '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
    F = ImageFont.truetype(f, 18); Hf = ImageFont.truetype(f, 16)
    cols = [('동작', 'name', 250), ('장 수', 'n', 70), ('최소 틱', 'minT', 80), ('그림 합', 'sum', 80), ('코드 길이', 'code', 90), ('치는 칸 틱', 'strike', 100), ('코드 맞는 틱', 'hitCode', 110), ('머리 오르내림', 'bob', 120), ('발 흔들림', 'footSwing', 100), ('틱', 'ticks', 330)]
    W = 20 + sum(c[2] for c in cols); im = Image.new('RGB', (W, 70 + 30 * len(rows) + 60), '#1b1f2a'); d = ImageDraw.Draw(im); x = 20
    for t, _, w in cols: d.text((x, 20), t, font=Hf, fill='#aab'); x += w
    for i, r in enumerate(rows):
        x = 20; y = 56 + i * 30
        for t, k, w in cols:
            v = r.get(k, '')
            if k == 'ticks': v = ' '.join(str(t) for t in v)[:44]
            if k == 'name' and r['act'].startswith('hit') and r['n'] <= 1: v += ' (몸 그림 없음)'
            colr = '#fff' if k in ('name', 'ticks') else ('#ff8a7a' if r['bad'].get(k if k != 'code' else 'sum') else ('#9fe8a0' if v != '' else '#556'))
            if k == 'hitCode' and r['bad'].get('strike'): colr = '#ff8a7a'
            d.text((x, y), str(v) if v != '' else '-', font=F, fill=colr); x += w
    reds = sum(r['red'] for r in rows)
    d.text((20, 62 + 30 * len(rows)), f'빨간 칸 {reds}개 — 기준: 장 수(걷기·달리기 8·회피 5·공격 4·맞기 3·점프 5), 한 장 3틱 이상, 그림 합 ≈ 코드 길이(±3틱),', font=Hf, fill='#ff8a7a' if reds else '#9fe8a0')
    d.text((20, 84 + 30 * len(rows)), '가장 뻗은 칸 = 코드 칼 맞는 틱(±2), 달리기 머리 4~6px·발 15px 이상 (그림 px). 빨간 칸이 있으면 main에 넣지 않는다.', font=Hf, fill='#889')
    im.save(OUT); print(json.dumps({'reds': reds, 'rows': len(rows), 'errors': errs[:3]}, ensure_ascii=False)); print('saved', OUT)
    return reds
if __name__ == '__main__':
    sys.exit(1 if main() else 0)
