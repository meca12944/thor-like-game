# 주인공 ↘(아래 오른쪽) 서기·걷기·달리기·대시·점프를 게임 아틀라스(/*H8*/)에 넣음. ↙ 은 ↘ 를 뒤집어 씀.
# 전: 아래 대각선으로 움직여도 정면(아래) 그림이 나옴. 후: ↘/↙ 를 보면 비스듬한 그림.
# 그림: motion_lab/research_v1/hero8/frames/*_dr (256 캔버스, 발 기준 128,189). 새 시트 anim/hero8_dr.webp.
# 사장님 10-23 "주인공 아래좌측 아래우측 방향 모션이 없나". 다시 돌려도 같은 결과.
import json,os
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
SRC=ROOT+'/motion_lab/research_v1/hero8';HTML=ROOT+'/test128/index.html';WJ=ROOT+'/test128/world.js';SHEET='anim/hero8_dr.webp'
C=json.load(open(SRC+'/clips.json'))
CLIPS=['idle_dr','walk_dr','run_dr','dash_dr','jump_dr']
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
A['jumpPh']['jump_dr']=[[0,1,2,3],[4,5,6,7,8],[9,11,13,14]]
A['_dr_note']='owner 10-23 motion lab: hero ↘ idle/walk/run/dash/jump (sheet anim/hero8_dr.webp, ↙ = mirrored); facing a down diagonal uses *_dr, straight down keeps *_down'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:]
a="const pick=k=>{if(vert&&DIAG8.test(k)&&H8.anims[k+'_'+sd0]){fl=hl;d=sd0;}"
b="const pick=k=>{const dk=sd0==='down'&&f8!=='down'&&H8.anims[k+'_dr']?'dr':sd0; /* ↘/↙ = *_dr art (mirrored for ↙), motion lab 10-23 */if(vert&&DIAG8.test(k)&&H8.anims[k+'_'+dk]){fl=hl;d=dk;}"
if b not in s:assert s.count(a)==1;s=s.replace(a,b)
open(HTML,'w').write(s)
w=open(WJ).read()
a="pick = k => { if (vert && DIAG8.test(k) && H.anims[k + '_' + fc]) { fl = hl; d = fc; }"
b="pick = k => { const dk = fc === 'down' && f8 !== 'down' && H.anims[k + '_dr'] ? 'dr' : fc; /* ↘/↙ = *_dr art (mirrored for ↙), motion lab 10-23 */ if (vert && DIAG8.test(k) && H.anims[k + '_' + dk]) { fl = hl; d = dk; }"
if b not in w:assert w.count(a)==1;w=w.replace(a,b)
open(WJ,'w').write(w);print('sheet',sheet.size,'cells',len(cells))
