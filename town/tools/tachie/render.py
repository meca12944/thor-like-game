# Render procedural tachie SVGs to transparent PNGs via headless Chromium.
# usage: python3 render.py [outdir] [scale] [id:expr ...]
import sys,os,asyncio
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__))
out=sys.argv[1] if len(sys.argv)>1 else '/tmp/tachie'; sc=float(sys.argv[2]) if len(sys.argv)>2 else 1.0
jobs=[a.split(':') for a in sys.argv[3:]]
os.makedirs(out,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':600,'height':1720},device_scale_factor=sc)
    for cid,ex in jobs:
        pg.goto(f'file://{D}/view.html?c={cid}&e={ex}'); pg.wait_for_function('document.title=="ok"')
        pg.screenshot(path=f'{out}/{cid}_{ex}.png',omit_background=True,clip={'x':0,'y':0,'width':600,'height':1720})
        print('ok',cid,ex)
    b.close()
