"""Town layout check (owner 10-23 「어떤 마을배치가 가장 좋을지 연구해서 최고의 배치」). Measures a map the way the player meets it:
- run time from the entrance to every service / story place (shortest walkable path, running speed),
- landmark sight: from how much of the walkable town each landmark is on screen (game view 24 x 13.5 tiles round the hero),
- dead ends (walkable tiles with one walkable neighbour) and the share of the town that is street.
python3 tools/hd/town_metrics.py <map.json> [out.png]   (map must carry hd props with ids: castle, chapel, web_arch, fountain ...)"""
import sys, json
from collections import deque
from PIL import Image, ImageDraw
m = json.load(open(sys.argv[1])); W, H = m['w'], m['h']; G = m['ground']; T = m['tile']
solid = lambda x, y: G[y][x] == '#'
objs = {o.get('id'): o for o in m['objects'] if o.get('id')}
props = {p['id']: p for p in m['hd']['props']}; D = m['hd']['D']
start = tuple(int(v) for v in m['spawns']['default'][:2])
def bfs(src):
    q = deque([src]); dist = {src: 0}
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and not solid(*n) and n not in dist: dist[n] = dist[(x, y)] + 1; q.append(n)
    return dist
dist = bfs(start); RUN = 82 * 1.9 / T   # tiles per second
def door_time(i):
    o = objs.get(i); 
    if not o: return None
    t = min((dist.get((o['x'] + dx, o['y'] + dy), 1e9) for dx in (-1, 0, 1) for dy in (-1, 0, 1, 2)), default=1e9)
    return None if t >= 1e9 else round(t / RUN, 1)
PLACES = [('대장간', 'f_door_smith'), ('잡화점', 'f_door_tool'), ('무기점', 'f_door_weapon'), ('여관', 'f_door_inn'), ('약초', 'f_door_herb'), ('이장', 'f_door_chief'),
          ('리네트', 'f_door_atelier'), ('예배당', 'f_door_chapel'), ('폐공방', 'f_arachne_gate')] + [(o.get('name', i), i) for i, o in objs.items() if o['type'] == 'waystone']
times = {n: door_time(i) for n, i in PLACES}
# landmark sight: the landmark's picture box (world tiles) overlaps the view round the hero standing on a tile
VW, VH, CY = 24, 13.5, 10 / T
def box(p): d = p.get('D', D); x0 = p['x'] - p['ax'] / d / T; return (x0, p['y'] - p['ay'] / d / T, x0 + p.get('w', p['ax'] * 2) / d / T, p['y'])
walk = list(dist.keys()); sight = {}
for lm in ('castle', 'chapel', 'web_arch', 'fountain', 'smoke_castle'):
    if lm not in props: continue
    bx0, by0, bx1, by1 = box(props[lm]); n = 0
    for (x, y) in walk:
        vx0, vy0 = x + .5 - VW / 2, y + .5 - CY - VH / 2
        if bx1 > vx0 and bx0 < vx0 + VW and by1 > vy0 and by0 < vy0 + VH: n += 1
    sight[lm] = round(100 * n / len(walk))
dead = sum(1 for (x, y) in walk if sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, y + dy) in dist) == 1)
res = {'walkable_tiles': len(walk), 'street_share_%': round(100 * len(walk) / (W * H)), 'dead_end_tiles': dead, 'run_s_from_entrance': times, 'landmark_on_screen_%': sight}
print(json.dumps(res, ensure_ascii=False, indent=1))
if len(sys.argv) > 2:   # heat map: run time from the entrance (dark = near, bright = far), landmarks boxed
    im = Image.new('RGB', (W * 8, H * 8), (20, 16, 24)); d = ImageDraw.Draw(im); mx = max(dist.values())
    for (x, y), v in dist.items(): k = v / mx; d.rectangle((x * 8, y * 8, x * 8 + 7, y * 8 + 7), fill=(int(60 + 180 * k), int(140 - 60 * k), int(200 - 150 * k)))
    for lm in sight: bx0, by0, bx1, by1 = box(props[lm]); d.rectangle((bx0 * 8, by0 * 8, bx1 * 8, by1 * 8), outline=(255, 230, 120), width=2)
    for n, i in PLACES:
        o = objs.get(i)
        if o: d.ellipse((o['x'] * 8 - 5, o['y'] * 8 - 5, o['x'] * 8 + 5, o['y'] * 8 + 5), fill=(255, 255, 255))
    im.save(sys.argv[2])
