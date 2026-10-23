# 주인공 뒷모습(↑): 서기·대시·맞기·점프에서 머리 옆에 칼끝만 보이고 손에 칼이 없던 것 → 칼끝 지우고, 서기는 오른손에 칼(jump_up 5번 칼).
# 걷기·달리기(손에 칼)와 바꿔 갈 때 칼이 머리 뒤↔손으로 순간이동하던 것을 없앰. 새 시트 anim/hero8_upfix.webp. (사장님 10-23 "계속 점검해")
import json,os,sys,numpy as np
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,D)
import faces
from upsword import sword_layer,fix
ROOT=os.path.abspath(D+'/../../..');HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_upfix.webp';H=faces.H
if SHEET in H['sheets']:sys.exit('already applied')
S,G=sword_layer();H['sheets'].append(SHEET);H['cells'].append([]);si=len(H['sheets'])-1;done={};tiles=[];anc=[]
for k,sw in [('idle_up',True),('dash_up',False),('hurt_up',False),('jump_up',False)]:
    for e in H['anims'][k]:
        key=(e[0],e[1])
        if key not in done:
            a,ax,ay=faces.cell(e);o,n,_=fix(a,ax,ay,S,G,sw)
            if n==0 and o.shape==a.shape and (o==a).all():done[key]=None
            else:
                im=Image.fromarray(o);b=im.getbbox();tiles.append(im.crop(b));anc.append((ax-b[0],ay-b[1]));done[key]=len(tiles)-1
        if done[key] is not None:e[0],e[1]=si,done[key]
W=2048;x=y=rowh=0;cells=[];pos=[]
for t in tiles:
    w,h=t.size
    if x+w>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=w+1;rowh=max(rowh,h)
sh=Image.new('RGBA',(W,y+rowh),(0,0,0,0))
for t,(x0,y0),(ax,ay) in zip(tiles,pos,anc):sh.paste(t,(x0,y0));cells.append([x0,y0,t.size[0],t.size[1],ax,ay])
sh.save(ROOT+'/test128/assets/'+SHEET,lossless=True,method=6);H['cells'][si]=cells
H['_upfix_note']='owner 10-23: back (up) idle/dash/hurt/jump: stray sword tip beside the head removed, idle_up holds the sword in the right hand like walk/run (handoff/claude/hero8_face_v1/upsword_apply.py)'
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/')
open(HTML,'w').write(s[:j]+json.dumps(H,separators=(',',':'),ensure_ascii=False)+s[e:]);print('바꾼 장',len(tiles))
