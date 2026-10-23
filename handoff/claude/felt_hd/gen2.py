"""Consistency test: same view as the hero ('low top-down'), forced palette from the chapel (color_image)."""
import os, sys, base64, io
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'felt_pixellab'))
import pl
from specs import STYLE
from PIL import Image
ch = Image.open('parts/chapel.png').convert('RGB'); buf = io.BytesIO(); ch.save(buf, 'PNG')
PAL = {'type': 'base64', 'base64': base64.b64encode(buf.getvalue()).decode(), 'format': 'png'}
B = 'building seen from the front and slightly above like a classic 16-bit JRPG town, front wall and door facing the viewer, roof visible, highly detailed, '
ASSETS = [
 ('atelier_v2', (400, 360), B + "ruined royal tailor workshop of carved pale stone with a broken gilded arch over the door, colorful faded cloth drapes patching the cracked walls and roof, a dress mannequin by the door"),
 ('burned_v2',  (300, 260), B + "burned-out ruined stone house, roof gone, charred black beams sticking up, soot-blackened walls, empty window holes"),
 ('house_v2',   (300, 280), B + "poor patched plank and stone house with a sagging dark slate roof, crooked chimney, small lit window"),
]
for aid, (w, h), desc in ASSETS:
    out = f'parts/{aid}.png'
    if os.path.exists(out): continue
    r = pl.submit('/map-objects', {'description': desc + ', ' + STYLE, 'image_size': {'width': w, 'height': h}, 'view': 'low top-down', 'color_image': PAL, 'seed': 11})
    if '_http' in r: print(aid, r); continue
    j = pl.wait(r['background_job_id'], every=5); pl.log(f'hd_{aid}', '/map-objects', j); ims = pl.images(j)
    if ims: open(out, 'wb').write(ims[0]); print(aid, 'ok')
    else: print(aid, 'no image', str(j)[:160])
print('felt log total', pl.total())
