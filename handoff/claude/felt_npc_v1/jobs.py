# Felt NPC idle + walk for 9 people x 3 views (south/east/north; west = mirrored east). walk = key pose (edit 10) -> key->key 8-frame cycle (8);
# idle = base->base 4 frames (4). Writes one shell line per job to stdout for xargs -P. Key from env only (scripts read it).
import json,os
P={'martha':'the dented wooden tankard','oswald':'the rusty hand bell and prayer beads','sera':'the small herb basket','bart':'the gnarled walking stick (he leans on it as he walks)',
   'rom':'the heavy forging hammer','gas':'the spear and the helmet under his arm','luca':'the cracked lute','toby':'the small cloth ball','ben':'the old ledger book, the big backpack stays on his back'}
V={'south':('Front view, walking toward the camera.','seen from the front, walking toward the camera'),
   'east':('Side view facing right, walking to the right.','strict side view facing right the whole time, walking to the right'),
   'north':('Back view, walking away from the camera, we see the back.','seen from behind the whole time, walking away from the camera, never turns to the side')}
T='Keep the exact same character design, colors, face, outfit, props and size, full body, no effects, same facing direction.'
for n,prop in P.items():
    for d,(kv,cv) in V.items():
        if not (n=='martha' and d=='south'):
            key=f'k_{n}_{d[0]}.png'
            edit=f"Walking pose mid-stride: one foot forward with the heel down, the other foot behind on the toes, feet clearly apart, knees slightly bent, arms swing naturally opposite to the legs, still holding {prop}."
            cyc=f"one complete natural human walking cycle {cv} at a calm pace: from this pose the back leg swings forward past the standing leg, then the other leg does the same, ending back in this exact starting pose; legs alternate cleanly, gentle arm swing, {prop} stays in the hands, same character and size in every frame, no effects"
            print(json.dumps(['walk',n,d,f'{n}_s11/{d}.png',key,f'{kv} {edit} {T}',cyc]))
        print(json.dumps(['idle',n,d,f'{n}_s11/{d}.png',f"subtle breathing idle, {cv.split(',')[0]}, standing still in place: the chest rises and falls slightly, tiny head and shoulder movement, feet do not move, {prop} stays in the hands, same character and size in every frame, no effects"]))
