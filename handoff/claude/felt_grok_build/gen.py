"""펠트(그록 대표 그림 배치) 건물 부품 — PixelLab map-objects, low top-down, 마을 32색, 그록 조각을 init_image로.
크기: 그록 1점 = 월드 0.8px, 최종 D=3 → 1.68배 (= 그록 크기 × 0.7, 한 장 최대 400px).
python3 gen.py <id...> [--var a|b]   키는 PIXELLAB_API_KEY 에서만."""
import os, sys, io, base64, json
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'felt_pixellab')); import pl
from PIL import Image
STYLE = ('dark fantasy slum on the outskirts of a burned royal capital, soot-stained, poor and patched, muted sepia browns and greys, '
         'warm dusk light from the upper left, 16-bit JRPG town pixel art, crisp pixels')
B = 'building seen from the front and slightly above like a classic 16-bit JRPG town, front wall and door facing the viewer, roof visible, '
SPEC = {
 'inn':       B + "two-storey timber-framed inn and tavern with a steep red-brown tiled roof, lit warm windows, wooden sign, barrels by the door",
 'se_house':  B + "squat stone blacksmith forge with a thick chimney, open front workshop under a small yellow cloth awning, anvil and glowing hearth inside, rock piles",
 's_house':   B + "village elder's modest stone and timber house with a dark slate roof and two chimneys, porch with a table and benches",
 'e_row':     B + "herbalist's cottage, bundles of dried herbs hanging under the eaves, shelves of jars and pots, worn wooden steps",
 'chapel':    B + "old stone chapel with a tall square bell tower, arched door, cracked walls",
 'watchtower':"tall wooden watchtower on stilts with a small roofed lookout platform and ladder, seen from slightly above, 16-bit JRPG",
 'linette':   B + "ruined royal tailor workshop of carved pale stone with tall arched windows and a broken gilded arch over the door, faded cloth drapes patching cracks",
 'west_a':    B + "narrow three-storey stone shop house, second-hand weapon shop with a crossed swords sign, red cloth awning over a weapon rack",
 'west_b':    B + "tall gabled stone and timber shop house with a striped cloth awning over a market counter of goods",
 'shop_sign': B + "general store of timber and stone with a slate roof, hanging sign with a feather, teal cloth awning, crates and sacks",
 'sw_house':  B + "poor stone house with a dark slate roof and a blue cloth awning over the door",
 'west_edge': B + "small guard house of stone with a narrow slate roof and a shuttered window, spears leaning by the door",
 'bl_house':  B + "poor patched plank and stone house with a sagging dark slate roof",
 'web_arch':  B + "ruined stone workshop entrance with a dark arched doorway, thick white spider webs covering the walls and roof",
 'red_stall': "wandering merchant's wooden cart stall with a red tiled canopy and a blue cloth awning, trinkets and jars on the counter, seen from slightly above, 16-bit JRPG",
 'stall_n':   "small market stall with a patched brown cloth canopy over a wooden counter of goods, seen from slightly above, 16-bit JRPG",
 'castle_l':  "left half of a huge burned ruined royal castle, jagged broken stone towers and walls, soot-blackened, empty windows, seen from slightly above, 16-bit JRPG",
 'castle_r':  "right half of a huge burned ruined royal castle, jagged broken stone towers and walls with thin smoke, soot-blackened, seen from slightly above, 16-bit JRPG",
 'mausoleum': "small old stone mausoleum shrine with an arched dark doorway and a cross-shaped finial, mossy, seen from slightly above, 16-bit JRPG",
 'fountain':  "round stone fountain in a town square, cracked dry basin with no water, broken tiered top, seen from slightly above, 16-bit JRPG",
}
PALF = os.environ.get('PALFILE', 'palette_32.png')
PAL = {'type': 'base64', 'base64': pl.b64(os.path.join(H, '..', 'felt_grok_layout', PALF)), 'format': 'png'}
SC = 0.8 * 3 * 0.7

MASK = True
def house_mask(size):
    # 집 모양(오각형) 밖은 투명 → PixelLab이 둘레 땅을 그리지 않고 건물만 투명 배경 위에 그림
    from PIL import ImageDraw
    w, h = size; m = Image.new('L', size, 0); d = ImageDraw.Draw(m)
    d.polygon([(w*.06, h*.40), (w*.5, h*.02), (w*.94, h*.40), (w*.94, h*.93), (w*.06, h*.93)], fill=255)
    return m

from shapes import POLY
KEY = Image.open(os.path.join(H, '..', 'felt_grok_layout', 'grok_felt_keyart.png')).convert('RGBA')

def geom(pid):
    # 다각형 둘레 + 여백 2 → 잘라낼 칸, 배율, 크기(4의 배수)
    P = POLY[pid]; x0, y0 = min(p[0] for p in P) - 2, min(p[1] for p in P) - 2
    x1, y1 = max(p[0] for p in P) + 2, max(p[1] for p in P) + 2
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, KEY.width), min(y1, KEY.height)
    s = min(SC, 400 / max(x1 - x0, y1 - y0)); w, h = int((x1 - x0) * s) // 4 * 4, int((y1 - y0) * s) // 4 * 4
    return (x0, y0, x1, y1), s, (w, h)

def mask_of(pid):
    from PIL import ImageDraw
    (x0, y0, x1, y1), s, (w, h) = geom(pid)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).polygon([((x - x0) * w / (x1 - x0), (y - y0) * h / (y1 - y0)) for x, y in POLY[pid]], fill=255)
    return m

def init_img(pid):
    (x0, y0, x1, y1), s, (w, h) = geom(pid)
    bg = KEY.crop((x0, y0, x1, y1)).resize((w, h), Image.LANCZOS)
    bg.putalpha(mask_of(pid))
    buf = io.BytesIO(); bg.save(buf, 'PNG')
    return {'type': 'base64', 'base64': base64.b64encode(buf.getvalue()).decode(), 'format': 'png'}, (w, h)

VARS = {'a': 300, 'b': 600, 'm': 300, 'p': 300, 'q': 300}
TEXT = {  # id: (크기, 설명) — init 없이 글자+색만, 투명 배경
 'watchtower': ((120, 240), "tall wooden watchtower on four stilts with cross braces, small roofed lookout platform with a railing, ladder, seen from slightly above, 16-bit JRPG"),
 'mausoleum':  ((160, 176), SPEC_M := "small old stone mausoleum shrine with an arched dark doorway and a cross-shaped finial, mossy, seen from slightly above, 16-bit JRPG"),
 'tombs':      ((160, 120), "cluster of three old crooked gravestones and a broken stone cross in dry grass, seen from slightly above, 16-bit JRPG"),
 'fence_iron': ((192, 96),  "straight section of an old rusty wrought iron graveyard fence between two stone posts, seen from slightly above, 16-bit JRPG"),
 'barrels':    ((96, 96),   "two old wooden barrels and a sack, seen from slightly above, 16-bit JRPG"),
 'bench':      ((112, 72),  "worn wooden park bench, seen from slightly above, 16-bit JRPG"),
 'woodpile':   ((112, 80),  "stack of chopped firewood logs, seen from slightly above, 16-bit JRPG"),
 'anvil':      ((80, 72),   "blacksmith iron anvil on a tree stump, seen from slightly above, 16-bit JRPG"),
 'well':       ((112, 120), "old stone well with a small wooden roof and a bucket, seen from slightly above, 16-bit JRPG"),
 'herb_rack':  ((96, 96),   "wooden drying rack with bundles of hanging herbs, seen from slightly above, 16-bit JRPG"),
 'rubble':     ((128, 80),  "pile of broken burned stone rubble and charred beams, seen from slightly above, 16-bit JRPG"),
 'sign_post':  ((64, 96),   "wooden signpost with two arrow boards, seen from slightly above, 16-bit JRPG"),
 # 3번방 배치 연구(TOWN_LAYOUT_ko.md) 부탁분: 랜드마크·구역 소품
 'fountain_king':  ((320, 320), "tall broken stone fountain in a town square, cracked dry round basin with no water, on top a weathered stone statue of a crowned king holding a sword, the statue's arm broken off, rubble at the base, seen from slightly above, 16-bit JRPG"),
 'fountain_king2': ((320, 320), "tall ruined town square fountain, dry cracked tiered stone basin, a headless statue of a king with a long cloak and a sword standing on a high pedestal, moss and rubble, seen from slightly above, 16-bit JRPG", 21),
 'south_gate':     ((320, 240), "village entrance gate of rough wooden palisade, two tall log posts with a crossbeam and a hanging wooden sign, open gate doors, short palisade wall on each side, seen from slightly above, 16-bit JRPG"),
 'fence_wood':     ((192, 96),  "straight section of a rough wooden palisade fence of sharpened logs, seen from slightly above, 16-bit JRPG"),
 'string_lights':  ((256, 128), "string of small hanging paper lanterns on a sagging rope between two wooden poles, seen from slightly above, 16-bit JRPG"),
 'candelabra':     ((64, 128),  "tall iron standing candelabra with melted candles and wax drips, seen from slightly above, 16-bit JRPG"),
 'cocoons':        ((128, 160), "cluster of three human-sized white silk spider cocoons hanging from a broken beam, thick webs, seen from slightly above, 16-bit JRPG"),
 'cocoons2':       ((128, 128), "three large white silk cocoons wrapped tightly in spider web, lying in a heap on the ground with web strands, seen from slightly above, 16-bit JRPG", 3),
 'bush_a':         ((128, 96),  "low dry thorny bush with a few withered leaves, dusty brown and olive, seen from slightly above, 16-bit JRPG"),
 'bush_b':         ((160, 112), "cluster of dry scrub bushes and tall dead grass, dusty brown and dark olive, seen from slightly above, 16-bit JRPG", 13),
 'dead_tree':      ((160, 224), "leafless dead tree with twisted dark branches and exposed roots, seen from slightly above, 16-bit JRPG"),
 'stone_low':      ((144, 80),  "low pile of mossy grey roadside stones with dry grass tufts, seen from slightly above, 16-bit JRPG"),
 'ash_tree_a': ((176, 224), "broad deciduous tree with sparse dusty grey-olive leaves dulled by ash, dark twisted trunk, seen from slightly above, 16-bit JRPG"),
 'ash_tree_b': ((160, 208), "round leafy tree with withered ash-grey and faded olive foliage, a few bare branches, seen from slightly above, 16-bit JRPG", 5),
 'burnt_pine_a': ((128, 240), "tall conifer pine tree partly burned, charred black lower trunk, sparse dark grey-green needles, seen from slightly above, 16-bit JRPG"),
 'burnt_pine_b': ((112, 224), "narrow dark pine tree with dull grey-green needles dusted with ash, seen from slightly above, 16-bit JRPG", 9),
 'ash_bush': ((112, 80), "round low bush with dusty grey-olive leaves, seen from slightly above, 16-bit JRPG"),
 'boulder': ((128, 112), "large weathered grey boulder with moss and cracks, seen from slightly above, 16-bit JRPG"),
 'stump': ((80, 64), "old cut tree stump with exposed roots, seen from slightly above, 16-bit JRPG"),
 'pale_mushrooms': ((64, 48), "small cluster of pale sickly white mushrooms, seen from slightly above, 16-bit JRPG"),
 'ruin_pillar': ((80, 160), "broken ruined stone pillar column with a cracked top, moss, seen from slightly above, 16-bit JRPG"),
 'thread_stake': ((64, 128), "wooden stake wrapped tightly in pale white threads and spider silk, strands trailing, seen from slightly above, 16-bit JRPG"),
 'bridge_wood': ((192, 112), "short rustic wooden plank footbridge with rope rails, seen from slightly above, 16-bit JRPG"),
 'dry_reeds': ((96, 80), "clump of tall dry dead reeds and grass, pale tan, seen from slightly above, 16-bit JRPG"),
 'deer_corpse': ((128, 80), "dead deer lying on its side in the grass, stiff and grey like stone, seen from slightly above, 16-bit JRPG"),
 'bridge_wood2': ((224, 128), "wide wooden plank bridge crossing a small stream, planks laid side by side with low log railings on both sides, top-down view slightly from above, 16-bit JRPG", 17),
 'dry_reeds2':   ((96, 96), "large clump of tall dry pale tan reeds and dead grass blades, dense, seen from slightly above, 16-bit JRPG", 17),
 'pale_mushrooms2': ((80, 64), "cluster of six pale sickly white toadstool mushrooms of different sizes on dark soil, seen from slightly above, 16-bit JRPG", 17),
 'd_loom_a': ((192, 176), "large broken wooden weaving loom covered in pale threads and torn cloth, dusty, in a dark ruined workshop, seen from slightly above, 16-bit JRPG"),
 'd_loom_b': ((176, 160), "old wooden tapestry loom with a half-woven grey tapestry and snapped threads hanging, seen from slightly above, 16-bit JRPG", 5),
 'd_spool_rack': ((160, 144), "wooden rack of giant thread spools with pale silver and dark red thread, some unraveled, seen from slightly above, 16-bit JRPG"),
 'd_mannequins': ((176, 160), "three headless tailor dress mannequins in torn royal gowns, wrapped in spider silk, seen from slightly above, 16-bit JRPG"),
 'd_mannequin': ((80, 144), "single headless tailor dress mannequin on a wooden stand, torn dark gown, threads trailing, seen from slightly above, 16-bit JRPG"),
 'd_cut_table': ((192, 128), "long tailor's cutting table with giant shears, measuring tape, bolts of faded fabric and pins, seen from slightly above, 16-bit JRPG"),
 'd_fabric_pile': ((144, 96), "pile of rotting fabric bolts and torn cloth rolls, seen from slightly above, 16-bit JRPG"),
 'd_cocoon_wall': ((224, 224), "mass of many human-sized white silk cocoons stuck to a stone wall with thick webs, eerie, seen from slightly above, 16-bit JRPG"),
 'd_web_sheet': ((192, 160), "large thick spider web sheet stretched between two broken wooden beams, seen from slightly above, 16-bit JRPG"),
 'd_thread_pillar': ((96, 208), "ancient stone pillar tightly wrapped in pale spider silk and red thread, seen from slightly above, 16-bit JRPG"),
 'd_bones': ((112, 80), "small pile of old bones and a skull tangled in white threads, seen from slightly above, 16-bit JRPG"),
 'd_wardrobe': ((128, 176), "broken tall wooden wardrobe with open doors and moth-eaten royal garments, seen from slightly above, 16-bit JRPG"),
 'd_door_arch': ((160, 192), "heavy arched wooden door set in a dark stone wall, iron bands, threads across it, seen from the front slightly above, 16-bit JRPG"),
 'd_stairs_down': ((144, 144), "stone stairway descending into darkness through a square opening in a stone floor, seen from slightly above, 16-bit JRPG"),
 'd_wall_arch': ((240, 192), "section of dark ruined stone dungeon wall with a broken arch and hanging threads, front face, seen from slightly above, 16-bit JRPG"),
 'd_chest': ((96, 80), "old iron-bound wooden treasure chest, closed, seen from slightly above, 16-bit JRPG"),
 'd_waystone': ((80, 144), "ancient carved standing waystone with a faintly glowing pale blue rune, seen from slightly above, 16-bit JRPG"),
 'd_boss_loom': ((320, 304), "enormous ominous loom of souls made of black wood and bone, giant web woven into it with faint ghostly faces in the threads, centerpiece of a spider queen's lair, seen from slightly above, 16-bit JRPG"),
 'd_loom_a2': ((192, 176), "large broken wooden weaving loom filling the frame, big wooden frame with torn pale threads and hanging cloth, seen from slightly above, 16-bit JRPG", 17),
 'd_stairs2': ((160, 160), "large square stone stairwell opening in a stone floor with wide steps going down into darkness, stone rim, filling the frame, seen from slightly above, 16-bit JRPG", 17),
 'd_mannequins2': ((192, 176), "group of three tall headless tailor dress mannequins standing side by side in torn faded royal gowns, wrapped in spider silk, filling the frame, seen from slightly above, 16-bit JRPG", 17),
 'd_fabric_pile2': ((160, 112), "large heap of rotting fabric bolts, rolled cloth and torn curtains, filling the frame, seen from slightly above, 16-bit JRPG", 17),
 'd_boss_loom2': ((320, 304), "isolated enormous black wooden loom frame with a giant spider web woven between its beams, ghostly pale faces caught in the threads, bone decorations, transparent background, seen from slightly above, 16-bit JRPG", 17),
 'd_boss_loom3': ((320, 304), "isolated giant ominous throne-like loom of dark wood and bones with a huge web stretched across it and spools of red thread, transparent background, seen from slightly above, 16-bit JRPG", 29),
 'd_cocoon_s': ((64, 80), "single small white silk cocoon wrapped in spider web lying on the floor, seen from slightly above, 16-bit JRPG"),
 'd_cocoon_m': ((96, 160), "human-sized white silk cocoon hanging from a thick thread strand, slightly swaying, seen from slightly above, 16-bit JRPG"),
 'd_cocoon_l': ((160, 176), "cluster of three large human-sized silk cocoons bound together with thick webs on the floor, seen from slightly above, 16-bit JRPG"),
 'd_spool_tower': ((128, 256), "tall tower of stacked giant wooden thread spools with silver and red thread unraveling down, seen from slightly above, 16-bit JRPG"),
 'd_cocoon_throne': ((256, 256), "isolated eerie throne made of fused white silk cocoons and threads with a high web back, spider queen's seat, transparent background, seen from slightly above, 16-bit JRPG"),
 'd_wall_strip': ((192, 96), "seamless horizontal strip of dark old stone dungeon wall front face, mossy bricks with a few hanging threads, edge to edge, seen from the front slightly above, 16-bit JRPG"),
 'd_thread_curtain': ((96, 128), "curtain of hanging pale spider silk threads in a doorway, seen from slightly above, 16-bit JRPG"),
 'd_fabric_pile3': ((160, 112), "heap of rotting cloth rolls and torn curtains, seen from slightly above, 16-bit JRPG"),
 'ember_rubble':   ((160, 96),  "pile of charred burned stone rubble and black beams with a few glowing orange embers, thin smoke, seen from slightly above, 16-bit JRPG", None, 'palette_32.png'),
}

def gen_text(pid, var='t'):
    out = os.path.join(H, 'out', f'{pid}_{var}.png')
    if os.path.exists(out): print(pid, 'skip'); return
    (w, h), desc, *rest = TEXT[pid]
    seed = (rest[0] if rest and rest[0] else 7)
    pal = {'type': 'base64', 'base64': pl.b64(os.path.join(H, '..', 'felt_grok_layout', rest[1])), 'format': 'png'} if len(rest) > 1 else PAL
    body = {'description': desc + ', ' + STYLE, 'image_size': {'width': w, 'height': h}, 'view': 'low top-down',
            'color_image': pal, 'detail': 'high detail', 'shading': 'detailed shading', 'outline': 'selective outline', 'seed': seed}
    r = pl.submit('/map-objects', body)
    if '_http' in r: print(pid, r); return
    j = pl.wait(r['background_job_id'], every=5); pl.log(f'grok_{pid}_{var}', '/map-objects', j); ims = pl.images(j)
    if ims: open(out, 'wb').write(ims[0]); print(pid, var, 'ok', (w, h))
    else: print(pid, 'no image', json.dumps(j.get('last_response'))[:300])

if __name__ == '__main__' and '--text' in sys.argv:
    for pid in [a for a in sys.argv[1:] if not a.startswith('--')]: gen_text(pid)
    print('felt log total', pl.total()); sys.exit()

if __name__ == '__main__':
    argv = sys.argv[1:]; var = 'a'
    if '--var' in argv: i = argv.index('--var'); var = argv[i + 1]; del argv[i:i + 2]
    args = argv
    for pid in args:
        out = os.path.join(H, 'out', f'{pid}_{var}.png')
        if os.path.exists(out): print(pid, 'skip'); continue
        ii, (w, h) = init_img(pid)
        body = {'description': SPEC[pid] + ', ' + STYLE, 'image_size': {'width': w, 'height': h}, 'view': 'low top-down',
                'color_image': PAL, 'init_image': ii, 'init_image_strength': VARS[var], 'detail': 'high detail',
                'shading': 'detailed shading', 'outline': 'selective outline', 'seed': 7}
        r = pl.submit('/map-objects', body)
        if '_http' in r: print(pid, r); continue
        j = pl.wait(r['background_job_id'], every=5); pl.log(f'grok_{pid}_{var}', '/map-objects', j); ims = pl.images(j)
        if ims: open(out, 'wb').write(ims[0]); print(pid, var, 'ok', (w, h))
        else: print(pid, 'no image', json.dumps(j.get('last_response'))[:600])
    print('felt log total', pl.total())
