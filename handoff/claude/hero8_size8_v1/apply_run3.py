# 주인공 달리기 4방향 다시(사장님 10-24 "달리기 다시 그려", 팀장 기준 키 ±3%·팔 흔들기): 옆·↘·↗ 새 그림(팔이 다리 반대로 장마다 움직임, 같은 웅크림), ↑ 는 지금 그림 다리만 줄임.
# 새 시트 anim/hero8_run3.webp, 그림 motion_lab/research_v1/hero8/frames (assemble_run3.py). 이어서 run_steady.py가 달리기 머리 덜컥을 다시 맞춤.
import json,os,subprocess,sys
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
SRC=ROOT+'/motion_lab/research_v1/hero8';HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_run3.webp'
C=json.load(open(SRC+'/clips.json'));CLIPS=['run_right','run_dr','run_up','run_n']
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
A['_run3_note']='owner 10-23 motion lab: walk_dr / run_dr / run_up redrawn with longer strides (sheet anim/hero8_run3.webp); foot slip 2.0->1.6 / 2.5->2.05 / 6.1->3.75'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:];open(HTML,'w').write(s)
subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'run_steady.py')],check=True);print('sheet',sheet.size,len(cells))
