"""Felt v3 = the Grok composition as the real Felt map (owner 10-23 「그록 그림 대표」 + credits approved; with the town-art room and room 2).
Reads maps/felt_layout.json (building places from the key art) + maps/felt.json (doors, NPCs, clues, waystone, signs = other rooms' data)
and writes maps/felt_v3.json + maps/ch1_v3.json (felt_v3 + field_felt joined at the south exit). Doors / marks move onto the new buildings;
NPCs with "near" follow them (room 2's rule), the rest keep the composition-board spots. hd art = the board's placeholders until the
town-art room's D=3 parts arrive (then only the hd block changes). Test: ?go=ch1_v3
python3 tools/hd/build_felt_v3.py"""
import os, json, copy
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
L = json.load(open(os.path.join(ROOT, 'maps', 'felt_layout.json'))); F = json.load(open(os.path.join(ROOT, 'maps', 'felt.json')))
W, H = L['w'], L['h']; rows = [list(r) for r in L['ground']]
P = {p['id']: p for p in L['hd']['props']}
def foot(pid, dx=0, dy=0): p = P[pid]; return [int(p['x']) + dx, int(p['y'] - .01) + dy]   # foot-row tile of a building (+ offset)
DOOR = {'f_door_chief': 's_house', 'f_door_smith': 'se_house', 'f_door_herb': 'e_row', 'f_door_inn': 'inn', 'f_door_chapel': 'chapel',
        'f_door_atelier': 'linette', 'f_arachne_gate': 'web_arch', 'f_door_guard': 'watchtower', 'f_door_weapon': 'west_a', 'f_door_tool': 'shop_sign'}
EX = [43, H - 1]                                              # [17] south exit (3 tiles wide) -> 잿빛 들판
objs = []
for o in F['objects']:
    o = copy.deepcopy(o); t, i = o['type'], o.get('id')
    if t == 'door' and i in DOOR: o['x'], o['y'] = foot(DOOR[i])
    elif t == 'exit': o.update(x=EX[0] - 1, y=EX[1], w=3, h=1)
    elif t == 'waystone': o['x'], o['y'] = foot('web_arch', -5, 1)                       # 폐공방 앞 비석
    elif t == 'clue' and i == 'f_clue_felix': o['x'], o['y'] = foot('web_arch', -3, 2)
    elif t == 'clue' and i == 'f_clue_bell': o['x'], o['y'] = foot('chapel', 2, 0)
    elif t == 'sign': o['x'], o['y'] = EX[0] + 2, EX[1] - 3
    elif t == 'mark':
        o['x'], o['y'] = {'f_mark_fountain': foot('fountain', 0, -2), 'f_mark_stall': foot('red_stall'), 'f_mark_gate': [EX[0], EX[1] - 1]}.get(i, [o['x'], o['y']])
    objs.append(o)
# NPC spots = room 2's rule (near:[reference id, dx, dy], claude/felt-npc-place): resolved here too, so it works before their world.js lands
NEAR = {'f_rom': ['f_door_smith', -1, 1], 'f_bart': ['f_door_chief', -2, 2], 'f_oswald': ['f_door_chapel', 0, 1], 'f_martha': ['f_door_inn', 0, 1],
        'f_sera': ['f_door_herb', 0, 1], 'f_ben': ['f_mark_stall', -3, 1], 'f_linette': ['f_door_atelier', -3, 1], 'f_luca': ['f_mark_fountain', 6.5, 1.5],
        'f_toby': ['f_mark_fountain', 2, 4], 'f_gas': ['f_mark_gate', -1, -4]}
if not any(o['type'] == 'mark' for o in objs):   # main's felt.json has no marks yet -> add room 2's three
    objs += [{'type': 'mark', 'id': 'f_mark_fountain', 'x': foot('fountain', 0, -2)[0], 'y': foot('fountain', 0, -2)[1]},
             {'type': 'mark', 'id': 'f_mark_stall', 'x': foot('red_stall')[0], 'y': foot('red_stall')[1]}, {'type': 'mark', 'id': 'f_mark_gate', 'x': EX[0], 'y': EX[1] - 1}]
by = {o.get('id'): o for o in objs}
for o in objs:
    if o['type'] == 'npc':
        n = o.get('near') or NEAR.get(o['id'])
        if n and n[0] in by: o['near'] = n; r = by[n[0]]; o['x'], o['y'] = min(W - 2, max(1, r['x'] + n[1])), min(H - 2, max(1, r['y'] + n[2]))
for x in range(EX[0] - 1, EX[0] + 2): rows[H - 1][x] = '.'   # open the bottom edge at the exit
for o in objs:                                               # doors stand in the building's foot row: keep the tile below walkable; NPC tiles walkable
    if o['type'] == 'door': rows[o['y'] + 1][o['x']] = '.'
    if o['type'] == 'npc': rows[int(o['y'])][int(o['x'])] = '.'
# ---- best-layout pass (town_metrics.py + hub design research, 0 credits) ----
# 1) the plaza fountain is the town's save / warp stone (Ys village crystal, Dirtmouth's stag station): node + landmark + function in one place
fx, fy = foot('fountain', 0, 1); objs.append({'type': 'waystone', 'id': 'ws_felt_plaza', 'x': fx, 'y': fy, 'name': '광장 분수', 'walk': True})
# 2) districts read by their light (spawn-anywhere test): S entrance = forge orange, W market = warm lanterns, N royal ruin = embers,
#    NE chapel = violet candles, E web quarter = pale cold mist
def lp(pid, dx, dy, r, col, a): x, y = P[pid]['x'] + dx, P[pid]['y'] + dy; return [x, y, r, col, a]
LIGHTS = [l for l in L['hd'].get('lights', [])] + [
 lp('se_house', -1, -2, 70, '#ff7a2a', 1), lp('s_house', 0, -1, 50, '#ffb060', .6),
 lp('west_a', 0, -1, 55, '#ffc070', .8), lp('west_b', 0, -1, 55, '#ffc070', .8), lp('stall_n', 0, -1, 50, '#ffcc80', .7), lp('shop_sign', 0, -1, 50, '#ffc070', .6),
 lp('castle', -4, -1, 60, '#ff5a2a', .7), lp('castle', 5, -1, 60, '#ff5a2a', .7), lp('linette', 0, 0, 55, '#ffd0a0', .6),
 lp('chapel', 0, 0, 55, '#b080ff', .8), lp('yard_fence', -3, -1, 60, '#9a70e0', .6), lp('inn', 0, -1, 60, '#ffb060', .8),
 lp('e_row', 0, -1, 55, '#cfe0d8', .5), lp('web_arch', 0, -1, 70, '#c8d8ff', .7), lp('red_stall', 0, -1, 45, '#ffb070', .6),
 lp('fountain', 0, -1, 60, '#9fd8ff', .5)]
# 3) threads creep from the plaza along the east road and thicken toward the Arachne gate (foreshadowing; hide & reveal)
ax0, ay0 = P['fountain']['x'] + 4, P['fountain']['y'] - 1; ax1, ay1 = P['web_arch']['x'] - 2, P['web_arch']['y'] - 2; WEBS = []
for i in range(14):
    t = (i / 13) ** .7; x = ax0 + (ax1 - ax0) * t; y = ay0 + (ay1 - ay0) * t; n = 1 + int(t * 3)
    for j in range(n): dx = (j - n / 2) * 1.3; WEBS.append([x + dx, y - 2.5 - (j % 2), x + dx + 1.4 + t, y - .2, .6 + t, .25 + .5 * t])
m = {k: F[k] for k in ('type', 'area', 'region', 'title', 'bgm', 'battleBgm', 'tileset', 'tile') if k in F}
m.update(id='felt_v3', name='펠트', w=W, h=H, legend=L['legend'], solid=L['solid'], ground=[''.join(r) for r in rows], objects=objs,
         spawns={'default': [EX[0] + .5, EX[1] - 1.5, 'up'], 'world': [EX[0] + .5, EX[1] - 1.5, 'up'], 'field': [EX[0] + .5, EX[1] - 1.5, 'up']},
         hd=dict(L['hd'], lights=LIGHTS, webs=WEBS, grade='dusk'), viewZoom=0.85,   # town only: a little wider view (no combat here; landmarks on screen 16 -> 24 %)
          note='GENERATED by tools/hd/build_felt_v3.py from felt_layout.json (places) + felt.json (doors / NPCs / clues)')
json.dump(m, open(os.path.join(ROOT, 'maps', 'felt_v3.json'), 'w'), ensure_ascii=False, indent=1)
FF = json.load(open(os.path.join(ROOT, 'maps', 'field_felt.json')))
top = [x for x, c in enumerate(FF['ground'][0]) if c in ".'=,"]; fx = EX[0] - (top[0] + top[-1]) // 2   # field's top opening under the exit
json.dump({'id': 'ch1_v3', 'note': 'test: Felt v3 (Grok layout) + 잿빛 들판. switch ch1.json to this when the D=3 parts are in', 'region': 'ch1', 'area': 1,
           'dropExits': ['felt'], 'compose': [{'map': 'felt_v3', 'x': 0, 'y': 0}, {'map': 'field_felt', 'x': fx, 'y': H}]}, open(os.path.join(ROOT, 'maps', 'ch1_v3.json'), 'w'), ensure_ascii=False, indent=1)
print('ok felt_v3', W, 'x', H, len(objs), 'objects; field_felt at x', fx)
