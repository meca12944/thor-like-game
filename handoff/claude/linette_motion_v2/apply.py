# 리네트 모션연구방 결과를 게임 아틀라스(test128/assets/anim/linette8.json)에 넣음. 사장님 10-23 "리네트도 게임에 넣어주고".
# 걷기 8방향·달리기 6방향: 발이 안 미끄러지게 장마다 박자 다르게 + 몸 오르내림·좌우 몸무게 옮김(그림 0크레딧, motion_lab/research_v1/linette)
# 대각선 서기 숨쉬기, 쓰러지기 중력 박자(그림 그대로). 새 시트 anim/linette8_lab.webp. 다시 돌려도 같은 결과.
import json,os
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
SRC=ROOT+'/motion_lab/research_v1/linette';J=ROOT+'/test128/assets/anim/linette8.json';SHEET='anim/linette8_lab.webp'
C=json.load(open(SRC+'/clips.json'));A=json.load(open(J))
if SHEET in A['sheets']:si=A['sheets'].index(SHEET)
else:A['sheets'].append(SHEET);A['cells'].append([]);si=len(A['sheets'])-1
clips=sorted(os.listdir(SRC+'/frames'));cells=[];tiles=[];x=y=rowh=0;W=2048;start={}
for k in clips:
    start[k]=len(cells)
    for f in sorted(os.listdir(f'{SRC}/frames/{k}')):
        im=Image.open(f'{SRC}/frames/{k}/{f}').convert('RGBA');b=im.getbbox();t=im.crop(b);w,h=t.size
        if x+w>W:x=0;y+=rowh+1;rowh=0
        tiles.append((t,x,y));cells.append([x,y,w,h,128-b[0],189-b[1]]);x+=w+1;rowh=max(rowh,h)
sheet=Image.new('RGBA',(W,y+rowh),(0,0,0,0))
for t,x0,y0 in tiles:sheet.paste(t,(x0,y0))
sheet.save(ROOT+'/test128/assets/'+SHEET,lossless=True,method=6);A['cells'][si]=cells
for k in clips:A['anims'][k]=[[si,start[k]+q,C[k]['ticks'][q]] for q in range(C[k]['frames'])]
for k in C:
    if k.startswith('death_'):A['anims'][k]=[[e[0],e[1],t]+e[3:] for e,t in zip(A['anims'][k],C[k]['ticks'])]
A['_lab_note']=('owner 10-23 motion lab (handoff/claude/linette_motion_v2): walk 8 dirs / run 6 dirs re-timed per frame so the planted foot does not slide, '
 'body bob + side weight shift; idle_down(l) breathing; death gravity ticks; sheet anim/linette8_lab.webp. Moving frames must be picked by cumulative ticks.')
json.dump(A,open(J,'w'),ensure_ascii=False,separators=(',',':'));print('sheet',sheet.size,'cells',len(cells))
