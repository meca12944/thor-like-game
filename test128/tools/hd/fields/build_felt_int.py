"""New Felt interiors (option A): weapon / tool / herb / forge get their own interior map like the inn, chief, chapel, atelier.
bg: PixelLab 512x288 rooms, brightened and scaled x3 nearest to 1536x864 (= 24x14 cells at D=4 art... same as the old ones)."""
import json, os
import numpy as np
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = '/tmp/plwork/out/gi'
def box(g, x0, x1, y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): g[y][x] = '#'
R = {
 'weapon': dict(name='중고 무기점', sub='무기점', boxes=[(0, 3, 0, 13), (21, 23, 0, 13), (0, 23, 0, 4), (10, 14, 6, 8), (17, 20, 7, 9), (4, 5, 9, 12)],
   objs=[dict(type='door', id='fi_weapon_counter', x=12, y=8, name='무기 카운터', shop='f_weapon'),
         dict(type='clue', id='fi_weapon_rack', x=8, y=5, name='녹슨 검 더미', flag='felt_look_fi_weapon_rack', text='전쟁터에서 주워 온 칼들. 손잡이마다 다른 문장이 새겨져 있다.\n…주인은 아무도 돌아오지 않았다.'),
         dict(type='clue', id='fi_weapon_shield', x=7, y=8, name='금 간 방패', flag='felt_look_fi_weapon_shield', text='왕성 근위대의 방패. 한가운데가 안쪽에서 찢겨 있다.')]),
 'tool': dict(name='잡화점', sub='도구점', boxes=[(0, 1, 0, 13), (21, 23, 0, 13), (0, 23, 0, 4), (2, 8, 5, 7), (2, 6, 9, 12), (14, 20, 6, 8), (16, 20, 11, 12)],
   objs=[dict(type='door', id='fi_tool_counter', x=16, y=8, name='잡화 카운터', shop='f_tool'),
         dict(type='clue', id='fi_tool_rope', x=9, y=6, name='밧줄 더미', flag='felt_look_fi_tool_rope', text='튼튼한 삼 밧줄. 끝이 하얗게 엉겨 붙어 있다 — 실이 아니라 거미줄이다.'),
         dict(type='hidden', id='fi_tool_hid', x=7, y=8, loot=[['potion', 1]], find='선반 밑에서 찾았다!')]),
 'herb': dict(name='세라의 약초 오두막', sub='약초점', boxes=[(0, 4, 0, 13), (19, 23, 0, 13), (0, 23, 0, 4), (7, 12, 6, 9), (16, 18, 4, 8), (17, 18, 10, 12)],
   objs=[dict(type='clue', id='fi_herb_jars', x=14, y=5, name='약초 단지', flag='felt_look_fi_herb_jars', text='말린 쑥과 잿빛 이끼. 단지마다 세라의 깔끔한 글씨로 날짜가 적혀 있다.'),
         dict(type='clue', id='fi_herb_book', x=6, y=8, name='약초 도감', flag='felt_look_fi_herb_book', text='「해자 갈대 뿌리 — 열을 내린다.」 여백에 누군가 덧적었다: 「성 쪽으로는 가지 말 것.」', loot=[['riceball', 1]])]),
 'forge': dict(name='롬의 대장간', sub='대장간', boxes=[(0, 5, 0, 13), (21, 23, 0, 13), (0, 23, 0, 3), (11, 14, 4, 6), (7, 10, 7, 8), (16, 20, 4, 8), (16, 18, 10, 12), (6, 7, 10, 12)],
   objs=[dict(type='clue', id='fi_forge_blade', x=9, y=6, name='부러진 칼날', flag='felt_look_fi_forge_blade', text='롬이 다시 벼리려다 그만둔 칼날. 날 끝이 실처럼 가늘게 풀려 있다.'),
         dict(type='clue', id='fi_forge_water', x=15, y=9, name='담금질 물통', flag='felt_look_fi_forge_water', text='검게 식은 물. 표면에 잿가루가 둥둥 떠 있다.')],
   fires=[[12.9, 5.6, 1.7, 'forge'], [12.6, 7.0, .9, 'forge']], lights=[[12.9, 5.4, 110, '#ff7a2a', 1]]),
}
NPC = {'herb': ('f_sera', 14, 7), 'forge': ('f_rom', 12, 9)}
def main():
    felt = json.load(open(os.path.join(ROOT, 'tools/hd/fields/felt_v4_objects.json')))
    OB = {o.get('id'): o for o in felt['objects']}
    for k, r in R.items():
        im = Image.open(f'{SRC}/int_{k}_0.png').convert('RGB'); a = np.array(im).astype(float)
        lum = (a * [.3, .59, .11]).sum(-1, keepdims=True); a = lum + (a - lum) * .9; a = np.clip(a * 1.42 * [1.03, 1, .95], 0, 255)
        im = Image.fromarray(a.astype(np.uint8)).resize((1536, 864), Image.NEAREST)
        bg = f'assets/world/interiors/felt_int_{k}.png'; im.save(os.path.join(ROOT, bg), optimize=True)
        g = [['.'] * 24 for _ in range(14)]
        for b in r['boxes']: box(g, *b)
        for y in (13,): g[y] = ['#'] * 24
        for x in range(24):
            if not 10 <= x <= 13: g[12][x] = '#' if g[12][x] == '#' or x < 6 or x > 18 else g[12][x]
        objs = [{'type': 'exit', 'x': 10, 'y': 12, 'w': 3, 'h': 1, 'to': 'felt', 'spawn': f'{k}_out', 'label': '↓ 마을'}] + r['objs']
        if k in NPC:
            i, x, y = NPC[k]; n = json.loads(json.dumps(OB[i])); n['x'], n['y'] = x, y; n.pop('near', None); objs.append(n)
        m = {'id': f'felt_int_{k}', 'type': 'town', 'area': 1, 'region': 'felt', 'name': r['name'], 'title': {'kicker': '펠트', 'name': r['name'], 'sub': r['sub']},
             'bgm': 'town_ruin', 'tileset': 'field', 'tile': 16, 'w': 24, 'h': 14, 'bg': bg,
             'note': '1장 펠트 실내 (tools/hd/fields/build_felt_int.py). 배경은 실내 그림 한 장이고 칸은 막히는 곳. 아래로 나가면 마을 문 앞.',
             'legend': {'.': 'dirt', '#': {'ground': 'dirt', 'solid': True}}, 'solid': ['#'],
             'spawns': {'default': [11.5, 10.5, 'up'], 'door': [11.5, 10.5, 'up']}, 'ground': [''.join(r_) for r_ in g], 'objects': objs}
        if r.get('fires'): m['fires'] = r['fires']; m['lights'] = r['lights']
        json.dump(m, open(os.path.join(ROOT, f'maps/felt_int_{k}.json'), 'w'), ensure_ascii=False, indent=1)
        print(k); print('\n'.join(m['ground']))
main()
