"""1장 이야기 장면 그림 (팀장 마을배경방): generate-image-v2 384x216 = 게임 저해상 화면. 참고 = 게임 속 주인공·리네트·아라크네·그록 펠트.
python3 cg.py <id..>   키는 PIXELLAB_API_KEY 에서만."""
import os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..', 'felt_pixellab')); import pl
from PIL import Image
def ref(f, use):
    p = f if os.path.isabs(f) else os.path.join(H, f); im = Image.open(p)
    return {'image': {'type': 'base64', 'base64': pl.b64(p), 'format': 'png'}, 'size': {'width': im.width, 'height': im.height}, 'usage_description': use}
HERO = ref('ref_hero.png', 'the protagonist: tall swordsman, long black hair, dark navy coat with gold shoulder guards, red-lined black cape, longsword')
LIN = ref('ref_linette.png', 'Linette the young seamstress: blonde ponytail, blue ribbon, red top, two long needles')
ARA = ref('ref_boss.png', 'Arachne: pale woman torso stitched onto a black spider body with a thread spool')
FELT = ref(os.path.join(H, '..', '..', 'felt_grok_layout', 'grok_felt_keyart.png'), 'the slum village Felt below a burned royal castle, sepia, smoke')
STY = 'dark fantasy pixel art, 16-bit JRPG cutscene illustration, muted sepia and ash tones with ember and red thread accents, no text, no letters'
CG = {
 'cg_felt_arrival': ('the swordsman seen from behind standing on a hill of ash at dusk, looking down at a ruined slum village under a huge burned royal castle with smoke rising, embers floating', [HERO, FELT], 5),
 'cg_lair_gate': ('the swordsman and the young seamstress standing before a dark ruined workshop entrance covered in thick white spider webs and hanging cocoons, a faint red glow inside, ominous', [HERO, LIN], 7),
 'cg_arachne_end': ('the spider tailor Arachne collapsing, her threads unravelling into falling ash and white silk, her face peaceful and sad, the swordsman standing with his sword lowered in a dark red-lit lair', [ARA, HERO], 9),
 'cg_linette_join': ('the young seamstress walking beside the swordsman out of the dark workshop into grey dawn light over the ash village, she looks up at him hopefully, he looks ahead', [HERO, LIN], 11),
}
for cid in sys.argv[1:]:
    out = os.path.join(H, cid + '.png')
    if os.path.exists(out): print(cid, 'skip'); continue
    desc, refs, seed = CG[cid]
    r = pl.submit('/generate-image-v2', {'description': desc + ', ' + STY, 'image_size': {'width': 384, 'height': 216}, 'seed': seed, 'reference_images': refs})
    if '_http' in r: print(cid, r); continue
    j = pl.wait(r['background_job_id'], every=5) if 'background_job_id' in r else {'status': 'completed', 'last_response': r}
    pl.log('team_' + cid, '/generate-image-v2', j); ims = pl.images(j)
    if ims: open(out, 'wb').write(ims[0]); print(cid, 'ok')
    else: print(cid, 'no image', json.dumps(j)[:300])
print('felt log total', pl.total())
