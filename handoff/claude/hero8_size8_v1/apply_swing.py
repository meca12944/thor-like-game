# 주인공 옆모습 때리기 1~3타 그림(당김·휘두름·마무리)을 게임 아틀라스에 넣음 (사장님 10-24 「가안으로 가자」). 새 시트 anim/hero8_swing.webp, 그림 motion_lab/research_v1/hero8/frames/swing*_right (assemble_atk.py).
import json,os,subprocess,sys
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
SRC=ROOT+'/motion_lab/research_v1/hero8';HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_swing.webp'
C=json.load(open(SRC+'/clips.json'));CLIPS=['swing1_right','swing2_right','swing3_right']
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
if SHEET in A['sheets']:si=A['sheets'].index(SHEET)
else:A['sheets'].append(SHEET);A['cells'].append([]);si=len(A['sheets'])-1
cells=[];tiles=[];x=y=rowh=0;W=2048
for k in CLIPS:
    for f in sorted(os.listdir(f'{SRC}/frames/{k}')):
        im=Image.open(f'{SRC}/frames/{k}/{f}').convert('RGBA');b=im.getbbox();t=im.crop(b);w,h=t.size
        if x+w>W:x=0;y+=rowh+1;rowh=0
        tiles.append((t,x,y));cells.append([x,y,w,h,128-b[0],189-b[1]]);x+=w+1;rowh=max(rowh,h)
sheet=Image.new('RGBA',(W,y+rowh),(0,0,0,0))
for t,x0,y0 in tiles:sheet.paste(t,(x0,y0))
sheet.save(ROOT+'/test128/assets/'+SHEET,lossless=True,method=6)
A['cells'][si]=cells;n=0
for k in CLIPS:
    m=C[k]['frames'];A['anims'][k]=[[si,n+q,C[k]['ticks'][q]] for q in range(m)];n+=m
    if k in A.get('_steady_src',{}):A['_steady_src'][k]=[list(f) for f in A['anims'][k]]
A['_swing_note']='owner 10-24 motion lab: side attack bodies for hits 1-3 (pull -> swing -> finish), sheet anim/hero8_swing.webp; world.js plays them over the 검기 timing (side views only)'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:];open(HTML,'w').write(s)
print('sheet',sheet.size,len(cells))
