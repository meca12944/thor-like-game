# one-shot: register return-slash / per-weapon / run / roll / potion sheets + anims in hero_anim.src.json (idempotent)
import json
P='/workspace/town-demo/tools/anim/hero_anim.src.json';d=json.load(open(P))
S=d['sheets'];A=d['anims']
def sheet(k,f,n=6,ref=5,rf=.93):S[k]=dict(file=f,n=n,ref=ref,refFactor=rf)
for dr in ['right','down','up']:
  sheet('r2'+dr[0],'atk2b_'+dr)
  for w in ['gs','sp','dg','tw']:
    for h in [1,2,3]:
      import os
      if os.path.exists(f'/workspace/town-demo/src/hero/anim_raw/{w}{h}_{dr}.jpg'):sheet(f'{w}{h}{dr[0]}',f'{w}{h}_{dr}')
  sheet('rn'+dr[0],'run_'+dr,8,0,.96)
  pass  # roll sheets dropped: dodge = fast dash + afterimages (user choice)
sheet('rsr','runstart_right',6,5,1.0)
sheet('ptr','potion_right',6,0,1.0)
# fix refs where frame 5 isn't a clean stand
S['gs3u']['ref']=0;S['gs3u']['refFactor']=1.12
S['sp3u']['ref']=5;S['tw3r']['ref']=5
BASE=[0,1,2,3,3,4,5,5];TK=[2,2,2,3,2,3,3,2];OPT=[{},{},{},{},{'dx':1},{},{},{'bob':1}]
def atk(name,sh,dur=19,flip=False,frames=BASE,heavy=False):
  tot=sum(TK);sc=dur/tot;fr=[];acc=0;
  for i,(f,t,o) in enumerate(zip(frames,TK,OPT)):
    nt=max(1,round((acc+t)*sc)-round(acc*sc));acc+=t;o=dict(o)
    if flip:o['flip']=True
    fr.append([sh,f,nt]+([o] if o else []))
  A[name]=dict(loop=False,frames=fr)
D=['right','down','up']
for dr in D: atk('atk2b_'+dr,'r2'+dr[0],19)
W=d['weapons']
def dur(w,i):return W[w]['combo'][i]['dur']+2
for w,p in [('greatsword','gs'),('spear','sp'),('dagger','dg'),('twin','tw')]:
  for i,h in enumerate([1,2,3]):
    for dr in D:
      k=f'{p}{h}{dr[0]}'
      if k in S: atk(f'{p}{h}_{dr}',k,dur(w,i))
      elif h==2: atk(f'{p}{h}_{dr}',f'{p}1{dr[0]}',dur(w,i),flip=True)   # front/back view: mirrored hit1 = sweep from the other side, still across the front
      elif h==3 and p=='dg': # X cut: forward cut then mirrored cut
        k1=f'{p}1{dr[0]}';fr=[[k1,1,2],[k1,2,2],[k1,3,2],[k1,2,2,{'flip':True}],[k1,3,3,{'flip':True}],[k1,4,3],[k1,5,4,{'bob':1}]]
        A[f'{p}{h}_{dr}']=dict(loop=False,frames=fr)
      elif h==3: atk(f'{p}{h}_{dr}',f'{p}1{dr[0]}',dur(w,i))
  for i,h in enumerate([1,2,3]): W[w]['combo'][i]['anim']=f'{p}{h}'
  W[w]['art']='own frames ('+p+'1-3, 3 directions)'
for w in W:
  for c in W[w]['combo']:
    if c['anim']=='atk2s':c['anim']='atk2b'
W['chan']['combo'][0]['anim'],W['chan']['combo'][1]['anim'],W['chan']['combo'][2]['anim']='gs1','gs2','gs3'
W['chan']['art']='greatsword frames (gs1-3)'
for w in ['saber','whip','hidden','demon']:W[w]['art']=W[w]['art'].split(' (')[0]+' (atk1/atk2b/atk3)'
W['sword']['art']='own (atk1 / atk2b return slash / atk3)'
# attack reach: sector hitbox, range = world px from hero centre (town tile = 53.3 world px), arc in degrees
RANGE={'sword':96,'saber':92,'dagger':76,'greatsword':122,'spear':138,'whip':130,'twin':84,'hidden':100,'chan':120,'demon':108}
for w,r in RANGE.items():
  for i,c in enumerate(W[w]['combo']):
    c['range']=round(r*(1.08 if i==2 else 1));c['arc']=130 if c['kind']=='overhead' else 150
# run / roll / run-start / skid / potion
for dr in D:
  A['run_'+dr]=dict(loop=True,frames=[['rn'+dr[0],i,4]+([{'dy':-1}] if i in(3,7) else []) for i in range(8)])
A['runstart_right']=dict(loop=False,frames=[['rsr',0,3,{'bob':1}],['rsr',1,3],['rsr',2,4]])
A['runstart_down']='run_down';A['runstart_up']='run_up'
A['skid_right']=dict(loop=False,frames=[['rsr',3,4],['rsr',4,5],['rsr',5,5]])
A['skid_down']='idle_down';A['skid_up']='idle_up'
A['potion_right']=dict(loop=False,frames=[['ptr',0,5],['ptr',1,6],['ptr',2,6],['ptr',3,10],['ptr',3,6,{'bob':1}],['ptr',4,8],['ptr',5,7]])
A['potion_down']='potion_right';A['potion_up']='potion_right'
d['_weapons_doc']=d['_weapons_doc'].replace('Hits are clipped to the forward arc FEEL.arcDeg (120).','Hitbox = forward SECTOR: radius range (world px from the hero centre; town tile 53.3 px -> sword 96 = 1.8 tiles) and arc degrees (150 slashes / 130 overheads); the swing trail is drawn with exactly that radius and arc. hit2 = dedicated return-slash frames (atk2b / <w>2), sweeping across the FRONT in the opposite direction.')
for k in [k for k in A if k.startswith('atk2s_')]:del A[k]
json.dump(d,open(P,'w'),ensure_ascii=False,indent=1)
print(len(S),'sheets',len(A),'anims')
