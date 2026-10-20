# hero side hit2 = thrust v3 (owner OK 2026-10-20): hit2 is rebuilt only from hit1 cells (recover -> pull back -> thrust -> hold -> recover)
# so head/shoulder/body size is identical to hit1 (the separately drawn hit2 had a bigger, front-turned upper body). No new pixels;
# 18 ticks as before and the thrust frame lands on tick 5-7, so H8.combo hit2 timing (tick 6) stays.
import json
T='/home/user/thor-like-game/test128/'
d=json.load(open(T+'assets/anim/hero8.json'))
PLAN=[(7,2),(2,2),(3,1),(4,3),(5,3),(6,3),(7,4)]   # (hit1 frame index, ticks)
for side in ['right','left']:
    h1=d['anims'][f'hit1_{side}'];d['anims'][f'hit2_{side}']=[[h1[i][0],h1[i][1],t] for i,t in PLAN]
d['src']['thrust_v3']='hit2 side = hit1 cells re-timed (tools/anim/apply_thrust_v3.py)'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s);print('ok',d['anims']['hit2_right'],sum(e[2] for e in d['anims']['hit2_right']))
