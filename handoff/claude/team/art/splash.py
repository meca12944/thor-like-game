"""보스 등장 큰 그림 (팀장 마을배경방): PixelLab generate-image-v2, 참고 = 게임 속 아라크네 몸·얼굴. 키는 PIXELLAB_API_KEY 에서만."""
import os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..', 'felt_pixellab')); import pl
from PIL import Image
def ref(f, use):
    im = Image.open(os.path.join(H, f)); return {'image': {'type': 'base64', 'base64': pl.b64(os.path.join(H, f)), 'format': 'png'},
            'size': {'width': im.width, 'height': im.height}, 'usage_description': use}
DESC = ("dramatic boss introduction splash art, pixel art, dark fantasy: Arachne the thread tailor, a pale woman's upper body stitched onto a "
        "huge black spider body, long black hair, sewn smile, hollow eyes, holding giant shears, threads and silk webs streaming around her, "
        "glowing red thread lines, dark ruined workshop with hanging cocoons behind, low angle, ominous, 16-bit JRPG boss portrait")
for i, seed in enumerate([3, 11]):
    out = os.path.join(H, f'splash_{i}.png')
    if os.path.exists(out): continue
    body = {'description': DESC, 'image_size': {'width': 384, 'height': 216}, 'seed': seed,
            'reference_images': [ref('ref_boss.png', 'the boss body design: woman torso on a black spider body with long thin legs'), ref('ref_face.png', 'her face: pale, sewn smile, hollow eyes, black hair')]}
    r = pl.submit('/generate-image-v2', body)
    if '_http' in r: print(r); continue
    j = pl.wait(r['background_job_id'], every=5) if 'background_job_id' in r else {'status': 'completed', 'last_response': r}
    pl.log(f'team_splash_{i}', '/generate-image-v2', j); ims = pl.images(j)
    if ims: open(out, 'wb').write(ims[0]); print('ok', out)
    else: print('no image', json.dumps(j)[:400])
print('felt log total', pl.total())
