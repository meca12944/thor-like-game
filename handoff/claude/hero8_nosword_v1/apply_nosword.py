"""C안 (사장님 10-24 「C안으로 가자」): 벨 때(검기 0~4틱)만 끼우는 "칼 없는 몸" 그림.
 게임 아틀라스(/*H8*/)의 서기·걷기·달리기(right·dr·down·up·n, 왼쪽 = 뒤집기)를 칸마다 그대로 꺼내 칼만 지움(ns.py, 크레딧 0)
 -> 새 시트 anim/hero8_nosword.webp, anim 이름 = 원래 이름 + '_ns' (칸 수·박자·앵커 같음 = 크기·위치 그대로)
 -> H8.grip[원래 anim] = 칸마다 [dx, dy, 칼 각도(도)] : 칼 쥔 손 자리(앵커 = 발 128,189 기준 그림px), 각도 = 손 -> 칼끝 방향(오른쪽 0, 아래 +)
 그림 확인용: motion_lab/research_v1/hero8/nosword/<anim>/*.png, 표 nosword_sheet.png
   python3 handoff/claude/hero8_nosword_v1/apply_nosword.py"""
import json,os,sys
import numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from ns import remove
from cfg import cfg
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_nosword.webp'
OUT=ROOT+'/motion_lab/research_v1/hero8/nosword'
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
if SHEET in A['sheets']:si=A['sheets'].index(SHEET)
else:A['sheets'].append(SHEET);A['cells'].append([]);si=len(A['sheets'])-1
KS=sorted(k for k in A['anims'] if k.split('_')[0] in('idle','walk','run') and not k.endswith('_left') and not k.endswith('_ns'))
SH={};tiles=[];cells=[];x=y=rowh=0;W=2048;G={};ST={}
for k in KS:
    os.makedirs(f'{OUT}/{k}',exist_ok=True);G[k]=[];ST[k]=[];A['anims'][k+'_ns']=[]
    for q,f in enumerate(A['anims'][k]):
        if f[0] not in SH:SH[f[0]]=Image.open(f'{ROOT}/test128/assets/'+A['sheets'][f[0]]).convert('RGBA')
        cx,cy,w,h,ax,ay=A['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((cx,cy,cx+w,cy+h)),(128-ax,189-ay))
        b,hd,n=remove(np.array(c),**cfg(k,f'{q:03d}'));im=Image.fromarray(b);im.save(f'{OUT}/{k}/{q:03d}.png')
        G[k].append(None if hd is None else [round(hd[0]-128,1),round(hd[1]-189,1),round(hd[2])]);ST[k].append(n)
        bb=im.getbbox();t=im.crop(bb);tw,th=t.size
        if x+tw>W:x=0;y+=rowh+1;rowh=0
        tiles.append((t,x,y));A['anims'][k+'_ns'].append([si,len(cells),f[2]]);cells.append([x,y,tw,th,128-bb[0],189-bb[1]]);x+=tw+1;rowh=max(rowh,th)
sheet=Image.new('RGBA',(W,y+rowh),(0,0,0,0))
for t,x0,y0 in tiles:sheet.paste(t,(x0,y0))
sheet.save(ROOT+'/test128/assets/'+SHEET,lossless=True,method=6)
A['cells'][si]=cells;A['grip']=G
A['_nosword_note']='owner 10-24 plan C (motion lab): *_ns = the same idle/walk/run cells with the sword erased by hand-tuned script (handoff/claude/hero8_nosword_v1), swapped in only while the 검기 swings; grip[anim][i] = [dx, dy, deg] sword hand (art px from the feet anchor 128,189) and the blade direction it held'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:];open(HTML,'w').write(s)
json.dump({'removed_px':ST,'grip':G},open(OUT+'/stats.json','w'),ensure_ascii=False,indent=0)
print('sheet',sheet.size,len(cells),'anims',len(KS));[print(k,len(ST[k]),'지운 칸',min(ST[k]),'~',max(ST[k])) for k in KS]
