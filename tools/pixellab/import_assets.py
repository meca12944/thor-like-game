"""PixelLab 배경 → 게임 저장소 (사장님 11-12 「전부 게임에 올려」).
Reads the box run folder (/workspace/pixellab_bg_20261111: manifest.json, review.json, redo_replaces.json) and copies the chosen pictures to
maps_v2/pixellab/chN/{tiles,props,buildings,rooms,decals,kits}/ with one index.json per chapter.
Rule: OK items; an OK redo replaces the originals of its slot; 보통 only when the slot has nothing OK (flag soso_no_ok_for_slot); 버림 left out.
No API key is read or written here.  python3 tools/pixellab/import_assets.py [src]"""
import json, os, sys, shutil, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sel_common import verdict, slot_of, chapter_of, type_of
from zones_kw import zone_of
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else '/workspace/pixellab_bg_20261111'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'maps_v2', 'pixellab')
TDIR = {'tileset': 'tiles', 'prop': 'props', 'building': 'buildings', 'room': 'rooms', 'decal': 'decals', 'kit': 'kits'}
M = json.load(open(os.path.join(SRC, 'manifest.json'))); R = json.load(open(os.path.join(SRC, 'review.json')))
ZONES = {c: [(z['id'], z['name'], z.get('kind')) for z in json.load(open(os.path.join(ROOT, f'docs_maps/ch{c}/ch{c}_map.json')))['zones']] for c in range(1, 9)}
items = []
for j in M['jobs']:
    if not j.get('files') or j.get('status') != 'completed': continue
    t = type_of(j)
    if t is None: continue
    rv = R.get(j['id'], j.get('review') or '')
    if rv.startswith('참고'): continue
    g = j['group']
    kind = 'redo' if j['id'].startswith('rd_') else 'filler' if (j['id'].startswith('fl_') or g.startswith('filler') or g.endswith('/filler')) else 'test' if g == 'tests' else 'orig'
    items.append(dict(id=j['id'], ch=chapter_of(j), slot=j.get('replaces') or slot_of(j['id']), type=t, verdict=verdict(rv), review=rv, kind=kind, group=g, files=j['files'],
                      item=j.get('item', ''), prompt=(j.get('prompt') or ' / '.join(str(v) for k, v in j.get('params', {}).items() if isinstance(v, str) and k.endswith('description') or k == 'theme'))[:200]))
by = collections.defaultdict(list)
for it in items: by[(it['ch'], it['slot'])].append(it)
chosen = []
for key, L in by.items():
    if any(i['kind'] == 'redo' and i['verdict'] == 'ok' for i in L): pick = [i for i in L if i['verdict'] == 'ok' and i['kind'] != 'orig']
    else: pick = [i for i in L if i['verdict'] == 'ok']
    if not pick:
        pick = [i for i in L if i['verdict'] == 'soso']
        for i in pick: i['flag'] = 'soso_no_ok_for_slot'
    chosen += pick
chosen.sort(key=lambda i: (i['ch'], i['type'], i['id']))
summary = {}
for c in range(1, 9):
    idx = []
    for i in [i for i in chosen if i['ch'] == c]:
        src_dir = os.path.join(SRC, os.path.dirname(i['files'][0]))
        rel_dir = f"{TDIR[i['type']]}"
        e = dict(id=i['id'], type=i['type'], zone=zone_of(c, i['slot'], [z[0] for z in ZONES[c]]), slot=i['slot'], verdict=i['verdict'], review=i['review'], source=i['kind'], item=i['item'], prompt=i['prompt'])
        if i.get('flag'): e['flag'] = i['flag']
        if i['type'] in ('prop', 'building'):
            dst = os.path.join(OUT, f'ch{c}', rel_dir, i['id'] + '.png'); os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(SRC, i['files'][0]), dst)
            im = Image.open(dst).convert('RGBA'); e['file'] = os.path.relpath(dst, OUT); e['size'] = list(im.size); e['bbox'] = list(im.getchannel('A').getbbox() or (0, 0, *im.size))
        else:
            dst = os.path.join(OUT, f'ch{c}', rel_dir, i['id']); shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
            for f in sorted(os.listdir(src_dir)):
                p = os.path.join(src_dir, f)
                if f.endswith('.png') or f == 'tiles.json': shutil.copyfile(p, os.path.join(dst, f))
                elif f == 'kit' and os.path.isdir(p): shutil.copytree(p, os.path.join(dst, 'kit'), ignore=shutil.ignore_patterns('*.zip'))
            e['file'] = os.path.relpath(dst, OUT)
            if i['type'] == 'tileset':
                t0 = Image.open(os.path.join(dst, 'tile_00.png')); meta = json.load(open(os.path.join(dst, 'tiles.json')))
                e['tile'] = t0.size[0]; e['tiles'] = len(meta); e['wang'] = 'corners' if all(m.get('corners') for m in meta) else '?'
                e['transition'] = any(2 in sum(((m.get('pattern') or {}).get(k, []) for k in ('row_0', 'row_1', 'row_2', 'row_3')), []) for m in meta)
            elif i['type'] == 'room': e['size'] = list(Image.open(os.path.join(dst, 'room.png')).size)
            else: e['tiles'] = len([f for f in os.listdir(dst) if f.endswith('.png')])
        idx.append(e)
    json.dump(dict(chapter=c, zones=[dict(id=z[0], name=z[1], kind=z[2]) for z in ZONES[c]], note='PixelLab 배경 (11-11~12). file = maps_v2/pixellab/ 기준 경로. verdict ok/soso (soso = 그 자리에 OK가 없어서 넣음, flag 참고).', items=idx),
              open(os.path.join(OUT, f'ch{c}', 'index.json'), 'w'), ensure_ascii=False, indent=1)
    summary[c] = dict(collections.Counter(e['type'] for e in idx), soso=sum(1 for e in idx if e['verdict'] == 'soso'), total=len(idx))
json.dump(summary, open(os.path.join(OUT, 'summary.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False))
