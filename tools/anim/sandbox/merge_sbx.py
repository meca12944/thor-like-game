# add the new 3-hit (sandbox/dnf/hero_lr.*) to room 1's hero sandbox atlas as sheet 4: nhit1..3_right (+ _left = same cells, flip flag 1)
import json,sys
a=json.load(open(sys.argv[1]));n=json.load(open(sys.argv[2]))
s=len(a['sheets']);a['sheets'].append('hero_lr.png');a['cells'].append(n['cells'])
for k in ('hit1','hit2','hit3'):
    a['anims']['n'+k+'_right']=[[s,c,t] for c,t in n['anims'][k]];a['anims']['n'+k+'_left']=[[s,c,t,1] for c,t in n['anims'][k]]
a['_doc']+=' | sheet 4 = new 3-hit (skeleton slash, horizontal slash h2b, Linette-style thrust), left = flip flag'
json.dump(a,open(sys.argv[1],'w'));print('sheets',a['sheets'])
