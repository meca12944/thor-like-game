# 주인공 새 걷기·달리기(보폭 넓게) + 점프 착지 땅 맞춤 + 쓰러지기 중력 박자를 게임 아틀라스(/*H8*/)에 넣음.
# 그림: motion_lab/research_v1/hero8/frames (256 캔버스, 발 기준 128,189). 새 시트 anim/hero8_move2.webp.
# 사장님 10-23 "인게임 적용해라". 다시 돌려도 같은 결과(이미 들어가 있으면 그 시트를 교체).
import json,os,numpy as np
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
SRC=ROOT+'/motion_lab/research_v1/hero8';HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_move2.webp'
C=json.load(open(SRC+'/clips.json'))
CLIPS=['walk_right','walk_down','walk_up','run_right','run_down','run_up','jump_up','jump_right']
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
if SHEET in A['sheets']:si=A['sheets'].index(SHEET)
else:A['sheets'].append(SHEET);A['cells'].append([]);si=len(A['sheets'])-1
# 잘라서 시트에 차례로 놓기(12칸씩 줄)
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
# 쓰러지기: 그림 그대로, 박자만 (비틀 → 중력처럼 빨라짐 → 쿵 → 멈춤)
A['anims']['death_right']=[[a[0],a[1],t]+a[3:] for a,t in zip(A['anims']['death_right'],C['death_right']['ticks'])]
A['gait']={'walkCyc':112,'runCyc':174}   # 새 보폭에 맞춘 다리 빠르기: 발 미끄러짐 3.7배·2배 -> 약 1배
A['_move2_note']=('owner 10-23 motion lab: walk/run right·down·up redrawn with long strides (handoff/claude/hero8_move_v2, motion_lab/research_v1), '
 'sheet anim/hero8_move2.webp; gait walkCyc 155->112, runCyc 228->174 (feet no longer slide); jump_up/jump_right landing frames lifted out of the ground; death_right gravity ticks')
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:]
open(HTML,'w').write(s);print('sheet',sheet.size,'cells',len(cells))
