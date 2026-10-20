"""ref/nobg_<view>.png (bg removed, 400 px tall) -> PixelLab image-to-pixelart-pro (native pixel scale detected) -> ref/px_<view>.png"""
import os, sys, io, base64
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref')
for n in sys.argv[1:]:
    out = os.path.join(R, f'px_{n}.png')
    if os.path.exists(out): continue
    im = Image.open(os.path.join(R, f'nobg_{n}.png')).convert('RGBA'); bg = Image.new('RGBA', im.size, (150, 150, 155, 255)); bg.alpha_composite(im)
    b = io.BytesIO(); im.save(b, 'PNG')
    r = pl.submit('/image-to-pixelart-pro', {'image': {'type': 'base64', 'base64': base64.b64encode(b.getvalue()).decode(), 'format': 'png'},
        'description': '16-bit JRPG pixel art game sprite, crisp single-colour dark outline, keep the design and colours exactly, transparent background'})
    j = pl.wait(r['background_job_id'], every=4) if r.get('background_job_id') else r
    rec = pl.log(f'px_{n}', '/image-to-pixelart-pro', j); ims = pl.images(j)
    print(n, rec['status'], rec['n'], len(ims), str(r)[:200] if not r.get('background_job_id') else '')
    if ims: open(out, 'wb').write(ims[0]); print(Image.open(out).size)
