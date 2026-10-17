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
open('/workspace/town-demo/index.html','w').write(t)
