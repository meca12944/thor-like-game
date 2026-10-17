import json
A='/workspace/town-demo/assets/'
t=open('/workspace/town-demo/tools/game.template.html').read()
spr=json.load(open(A+'sprites.json')); lvl=json.load(open(A+'level.json'))
t=t.replace('/*SPRITES*/',json.dumps(spr,separators=(',',':'))).replace('/*LEVEL*/',json.dumps(lvl,separators=(',',':')))
import os
it=A+'icons/items_demo.json'
t=t.replace('/*ITEMS*/',json.dumps(json.load(open(it)),ensure_ascii=False,separators=(',',':')) if os.path.exists(it) else 'null')
an=A+'anim/hero.json'
t=t.replace('/*ANIM*/',json.dumps(json.load(open(an)),ensure_ascii=False,separators=(',',':')) if os.path.exists(an) else 'null')
import base64,glob
sfx={os.path.basename(f)[:-4]:'data:audio/ogg;base64,'+base64.b64encode(open(f,'rb').read()).decode() for f in sorted(glob.glob(A+'sfx/*.ogg'))}
t=t.replace('/*SFX*/',json.dumps(sfx,separators=(',',':')) if sfx else 'null')
# Lv/EXP/MP: compact slice of data/levels.json (level worker's design data)
lj='/workspace/town-demo/data/levels.json'
if os.path.exists(lj):
    L=json.load(open(lj));a1=next((a for a in L['monster_exp'] if a['area']==1),None)
    mob=lambda n,dv:next((m['exp'] for m in (a1['mobs'] if a1 else []) if n in m['name']),dv)
    LV={'level_cap':L['level_cap'],'exp_table':[{'level':e['level'],'next':e['next']} for e in L['exp_table']],
        'mp':{k:L['growth']['stats']['mp'][k] for k in ('base','steps')},
        'difficulty':[{k:d[k] for k in ('id','name','enemy_hp','enemy_dmg','telegraph','aggression','tokens','champ_extra','potion_cap','mp_regen','perfect_ticks','iframe_bonus','ult_cap','telegraph_floor')} for d in L['difficulty']['levels']] if 'difficulty' in L else None,
        'tokenCd':(L.get('difficulty') or {}).get('behavior',{}).get('tokens',{}).get('token_cd',0.6),
        'demo_exp':{'slime':mob('슬라임',6),'champion':(a1['champions'][0]['exp'] if a1 and a1.get('champions') else 42)}}
else: LV=None
t=t.replace('/*LEVELS*/',json.dumps(LV,ensure_ascii=False,separators=(',',':')))
open('/workspace/town-demo/index.html','w').write(t)
