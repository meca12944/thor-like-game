# 주인공 대각선 위(↑·↗·↖) 점프: 착지 뒤 그림(10~14장)이 서기보다 6칸 크게 그려져 착지하면 몸이 커졌다가 서면 줄어듦
# (모션연구방 10-23 연구에서 찾음, 사장님 10-23 "오늘 연구 결과 전부 저장하고 인게임 적용").
# -> 그 5장만 한 배율(서기 키 126 / 착지 키 131 = 0.962)로 발 기준 줄임(pxscale). 새 시트 anim/hero8_jumpup2.webp. 다시 돌려도 같은 결과.
import json,os,sys
from PIL import Image
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'));sys.path.insert(0,ROOT+'/handoff/claude/hero8_front_v1')
from pxscale import pxscale
HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_jumpup2.webp';FR=range(10,15);S=126/131
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
src=A.get('_jumpup_src') or [list(f) for f in A['anims']['jump_up']];A['_jumpup_src']=src   # 고치기 전 칸(다시 돌릴 때 원본에서)
SH={}
def frame(f):
    if f[0] not in SH:SH[f[0]]=Image.open(ROOT+'/test128/assets/'+A['sheets'][f[0]]).convert('RGBA')
    x,y,w,h,ax,ay=A['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((x,y,x+w,y+h)),(128-ax,189-ay));return c
if SHEET in A['sheets']:si=A['sheets'].index(SHEET)
else:A['sheets'].append(SHEET);A['cells'].append([]);si=len(A['sheets'])-1
tiles=[];cells=[];X=0
for q in FR:
    im=frame(src[q]);sm=pxscale(im,S);c=Image.new('RGBA',(256,256));c.paste(sm,(round(128-128*S),round(189-189*S)),sm)
    b=c.getbbox();t=c.crop(b);tiles.append((t,X));cells.append([X,0,t.width,t.height,128-b[0],189-b[1]]);X+=t.width+1
sheet=Image.new('RGBA',(X,max(t.height for t,_ in tiles)))
for t,x in tiles:sheet.paste(t,(x,0))
sheet.save(ROOT+'/test128/assets/'+SHEET,lossless=True,method=6);A['cells'][si]=cells
A['anims']['jump_up']=[list(f) for f in src]
for n,q in enumerate(FR):A['anims']['jump_up'][q]=[si,n,src[q][2]]+src[q][3:]
A['_jumpup_note']='owner 10-23 motion lab: jump_up landing frames 10-14 were drawn 6px taller than idle_up -> scaled 0.962 about the feet (sheet anim/hero8_jumpup2.webp, original cells in _jumpup_src)'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:];open(HTML,'w').write(s);print('ok',cells)
