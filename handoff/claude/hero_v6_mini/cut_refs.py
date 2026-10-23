"""Cut the 4 views out of ref/turnaround_v6.jpg with PixelLab remove-background (complex), then normalise each to the game canvas:
256x256, feet root at (128,189), figure height 124 px (hero8.json figH), sword included."""
import os, sys, io, base64, json
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'ref')
src = Image.open(os.path.join(R, 'turnaround_v6.jpg')).convert('RGB')
VIEWS = [('south', 0, 330), ('east', 330, 630), ('south-east', 630, 950), ('north', 950, 1280)]
for name, x0, x1 in VIEWS:
    out = os.path.join(R, f'nobg_{name}.png')
    if not os.path.exists(out):
        crop = src.crop((x0, 0, x1, 720)); k = min(1, 400 / crop.height, 400 / crop.width)
        crop = crop.resize((int(crop.width * k), int(crop.height * k)), Image.LANCZOS)
        b = io.BytesIO(); crop.save(b, 'PNG')
        r = pl.submit('/remove-background', {'image': {'type': 'base64', 'base64': base64.b64encode(b.getvalue()).decode(), 'format': 'png'},
            'image_size': {'width': crop.width, 'height': crop.height}, 'background_removal_task': 'remove_complex_background',
            'text': 'anime swordsman with short black hair, navy coat with gold trim, gold pauldrons, longsword'})
        if r.get('background_job_id'): j = pl.wait(r['background_job_id'], every=3)
        else: j = r
        rec = pl.log(f'nobg_{name}', '/remove-background', j if r.get('background_job_id') else {'status': 'sync', 'usage': r.get('usage')})
        ims = pl.images(j)
        if not ims and isinstance(r.get('image'), dict): ims = [base64.b64decode(r['image']['base64'])]
        print(name, rec, len(ims), {k: str(v)[:80] for k, v in r.items() if k not in ('image',)})
        if ims: open(out, 'wb').write(ims[0])
