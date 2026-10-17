import json
A='/workspace/town-demo/assets/'
t=open('/workspace/town-demo/tools/game.template.html').read()
spr=json.load(open(A+'sprites.json')); lvl=json.load(open(A+'level.json'))
t=t.replace('/*SPRITES*/',json.dumps(spr,separators=(',',':'))).replace('/*LEVEL*/',json.dumps(lvl,separators=(',',':')))
open('/workspace/town-demo/index.html','w').write(t)
