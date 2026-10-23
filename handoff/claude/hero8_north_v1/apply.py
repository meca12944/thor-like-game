# 주인공 곧장 위(↑) 똑바른 뒷모습 서기·걷기·달리기를 게임 아틀라스(/*H8*/)에 넣음 (사장님 10-23 "위로달리는 모션은?" → "맞아" 똑바른 뒷모습).
# 전: ↑ 를 보면 비스듬한 뒷모습(↗) 그림. 후: 곧장 위만 *_n (좌우 뒤집지 않음, 칼은 오른손), ↗↖ 는 그대로 비스듬한 뒷모습. 회피대시·점프는 아직 비스듬한 그림.
# 그림: motion_lab/research_v1/hero8/frames/*_n (assemble_n.py). 새 시트 anim/hero8_n.webp. 다시 돌려도 같은 결과.
import json,os
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
SRC=ROOT+'/motion_lab/research_v1/hero8';HTML=ROOT+'/test128/index.html';WJ=ROOT+'/test128/world.js';SB=ROOT+'/tools/sandbox/build_hero_game.py';SHEET='anim/hero8_n.webp'
C=json.load(open(SRC+'/clips.json'));CLIPS=['idle_n','walk_n','run_n']
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
A['_n_note']='owner 10-23 motion lab: straight-up (↑) back view idle/walk/run (sheet anim/hero8_n.webp, never mirrored); ↗↖ keep the 3/4 back *_up art'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:]
a="const pick=k=>{const dk=sd0==='down'&&f8!=='down'&&H8.anims[k+'_dr']?'dr':sd0; /* ↘/↙ = *_dr art (mirrored for ↙), motion lab 10-23 */if(vert&&DIAG8.test(k)&&H8.anims[k+'_'+dk]){fl=hl;d=dk;}"
b="const pick=k=>{const dk=sd0==='down'&&f8!=='down'&&H8.anims[k+'_dr']?'dr':sd0==='up'&&f8==='up'&&H8.anims[k+'_n']?'n':sd0; /* ↘/↙ = *_dr art (mirrored for ↙), ↑ = *_n straight back (never mirrored), motion lab 10-23 */if(vert&&DIAG8.test(k)&&H8.anims[k+'_'+dk]){fl=dk==='n'?false:hl;d=dk;}"
if b not in s:assert s.count(a)==1;s=s.replace(a,b)
open(HTML,'w').write(s)
w=open(WJ).read()
a="const dk = fc === 'down' && f8 !== 'down' && H.anims[k + '_dr'] ? 'dr' : fc; /* ↘/↙ = *_dr art (mirrored for ↙), motion lab 10-23 */ if (vert && DIAG8.test(k) && H.anims[k + '_' + dk]) { fl = hl; d = dk; }"
b="const dk = fc === 'down' && f8 !== 'down' && H.anims[k + '_dr'] ? 'dr' : fc === 'up' && f8 === 'up' && H.anims[k + '_n'] ? 'n' : fc; /* ↘/↙ = *_dr art (mirrored for ↙), ↑ = *_n straight back (never mirrored), motion lab 10-23 */ if (vert && DIAG8.test(k) && H.anims[k + '_' + dk]) { fl = dk === 'n' ? false : hl; d = dk; }"
if b not in w:assert w.count(a)==1;w=w.replace(a,b)
open(WJ,'w').write(w)
sb=open(SB).read()
a="    if d in ('down', 'downl') and f'{base}_dr' in AN: return (f'{base}_dr', d == 'downl')  # ↘ art, ↙ = mirrored (motion lab 10-23)\n"
b=a+"    if d == 'n' and f'{base}_n' in AN: return (f'{base}_n', False)  # ↑ straight back (motion lab 10-23)\n"
if b not in sb:assert sb.count(a)==1;sb=sb.replace(a,b)
open(SB,'w').write(sb);print('sheet',sheet.size,'cells',len(cells))
