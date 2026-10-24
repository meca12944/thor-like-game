"""C안 (사장님 10-24 「C안으로 가자」): 벨 때(검기 0~4틱)만 끼우는 "칼 없는 몸" 그림.
 게임 아틀라스(/*H8*/)의 서기·걷기·달리기(right·dr·down·up·n, 왼쪽 = 뒤집기)를 칸마다 그대로 꺼내 칼만 지움(ns.py, 크레딧 0)
 -> 칼 든 시트마다 칸 배치·크기·앵커가 같은 칼 없는 사본 anim/ns/<같은 이름>.webp + H8.nsSheets {시트번호: 경로} (= 크기·위치 그대로)
 -> H8.grip["시트:칸"] = [dx, dy, 칼 각도(도)] : 칼 쥔 손 자리(앵커 = 발 128,189 기준 그림px), 각도 = 손 -> 칼끝 방향(오른쪽 0, 아래 +)
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
KS=sorted(k for k in A['anims'] if k.split('_')[0] in('idle','walk','run') and not k.endswith('_left') and not k.endswith('_ns'))
# 효과 담당 코드(nsSrc/gkGrip) 형식: 칼 든 시트마다 칸 배치·크기·앵커가 같은 칼 없는 사본 anim/ns/<같은 이름>.webp + H8.nsSheets{시트번호: 경로}, H8.grip["시트:칸"]
for k in list(A['anims']):
    if k.endswith('_ns'):del A['anims'][k]          # 예전 판(_ns anim + hero8_nosword.webp) 지움 = 인게임 최신만
if SHEET in A['sheets']:
    si=A['sheets'].index(SHEET);A['sheets'].pop(si);A['cells'].pop(si)
    for L in A['anims'].values():
        for f in L:
            if f[0]>si:f[0]-=1
    if os.path.exists(ROOT+'/test128/assets/'+SHEET):os.remove(ROOT+'/test128/assets/'+SHEET)
A.pop('_nosword_note',None)
SH={};NS={};G={};ST={}
for k in KS:
    os.makedirs(f'{OUT}/{k}',exist_ok=True);ST[k]=[]
    for q,f in enumerate(A['anims'][k]):
        if f[0] not in SH:SH[f[0]]=Image.open(f'{ROOT}/test128/assets/'+A['sheets'][f[0]]).convert('RGBA');NS[f[0]]=SH[f[0]].copy()
        cx,cy,w,h,ax,ay=A['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((cx,cy,cx+w,cy+h)),(128-ax,189-ay))
        b,hd,n=remove(np.array(c),**cfg(k,f'{q:03d}'));im=Image.fromarray(b);im.save(f'{OUT}/{k}/{q:03d}.png');ST[k].append(n)
        NS[f[0]].paste(im.crop((128-ax,189-ay,128-ax+w,189-ay+h)),(cx,cy))   # 같은 칸 자리에 칼 없는 몸 (투명 포함 통째로)
        if hd is not None:G[f'{f[0]}:{f[1]}']=[round(hd[0]-128,1),round(hd[1]-189,1),round(hd[2])]
os.makedirs(ROOT+'/test128/assets/anim/ns',exist_ok=True);NSS={}
for i,im in NS.items():
    pth=A['sheets'][i].replace('anim/','anim/ns/');im.save(ROOT+'/test128/assets/'+pth,lossless=True,method=6);NSS[str(i)]=pth
A['nsSheets']=NSS;A['grip']=G
A['_nosword_note']='owner 10-24 plan C (motion lab): nsSheets = sword-free copies of the idle/walk/run sheets (same cell layout; sword erased by hand-tuned script handoff/claude/hero8_nosword_v1, 0 credits), drawn only while the 검기 swings; grip["sheet:cell"] = [dx, dy, deg] sword fist (art px from the feet anchor 128,189) and the blade direction it held (right 0, down +)'
s=s[:j]+json.dumps(A,separators=(',',':'),ensure_ascii=False)+s[e:];open(HTML,'w').write(s)
json.dump({'removed_px':ST,'grip':G},open(OUT+'/stats.json','w'),ensure_ascii=False,indent=0)
print('ns sheets',NSS,'grip',len(G));[print(k,len(ST[k]),'지운 칸',min(ST[k]),'~',max(ST[k])) for k in KS]
