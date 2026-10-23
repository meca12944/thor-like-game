# 주인공 정면(↓) 세트 크기를 다른 방향과 같게 (사장님 10-23 "8방향 달리거나 걸을때 크기 및 비율 주인공의 크기가 일정하지 않은데").
#  정면 세트만 10-23 hero8_front_v1에서 96%로 줄였었음 -> 서기 키 118 (옆 123·↘ 124·뒤 126), 머리~어깨받이 길이도 다른 방향보다 4% 작음.
#  -> 정면 동작 6개(서기·걷기·달리기·대시·점프·맞기)를 1/0.96 = 1.042배로 되돌림(pxscale, 발 기준). 새 시트 anim/hero8_front2.webp. 다시 돌려도 같은 결과.
import json,os,sys
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));sys.path.insert(0,ROOT+'/handoff/claude/hero8_front_v1')
from pxscale import pxscale
HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_front2.webp';S=1/0.96;DX=6   # 정면 그림이 왼쪽으로 8칸 치우쳐 있어 좌우 뒤집힐 때 머리가 16칸 튐 -> 6칸 오른쪽으로(발 가운데 -4 -> +2)
CL=['idle_down','walk_down','run_down','dash_down','jump_down','hurt_down']
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
src=A.get('_front2_src') or {k:[list(f) for f in A['anims'][k]] for k in CL};A['_front2_src']=src
SH={}
def frame(f):
    if f[0] not in SH:SH[f[0]]=Image.open(ROOT+'/test128/assets/'+A['sheets'][f[0]]).convert('RGBA')
    x,y,w,h,ax,ay=A['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((x,y,x+w,y+h)),(128-ax,189-ay));return c
if SHEET in A['sheets']:si=A['sheets'].index(SHEET)
else:A['sheets'].append(SHEET);A['cells'].append([]);si=len(A['sheets'])-1
cells=[];tiles=[];idx={};X=Y=rowh=0
for k in CL:
    for f in src[k]:
        key=(f[0],f[1])
        if key in idx:continue
        sm=pxscale(frame(f),S);c=Image.new('RGBA',(256,256));c.paste(sm,(round(128-128*S)+DX,round(189-189*S)),sm)
        b=c.getbbox();t=c.crop(b)
        if X+t.width>2048:X=0;Y+=rowh+1;rowh=0
        tiles.append((t,X,Y));idx[key]=len(cells);cells.append([X,Y,t.width,t.height,128-b[0],189-b[1]]);X+=t.width+1;rowh=max(rowh,t.height)
sheet=Image.new('RGBA',(2048,Y+rowh))
for t,x,y in tiles:sheet.paste(t,(x,y))
sheet.save(ROOT+'/test128/assets/'+SHEET,lossless=True,method=6);A['cells'][si]=cells
for k in CL:A['anims'][k]=[[si,idx[(f[0],f[1])],f[2]]+f[3:] for f in src[k]]
A['_front2_note']='owner 10-23 motion lab: front (down) set was 96% -> back to 100% like the other directions (sheet anim/hero8_front2.webp, original cells in _front2_src)'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:];open(HTML,'w').write(s);print('ok',sheet.size,len(cells))
