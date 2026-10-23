# 주인공 얼굴 도장 (사장님 10-23 "주인공 얼굴이 모션마다 일정치 않아"): 서기 얼굴(정면 idle_down 0번, 옆 idle_right 0번)을
# 걷기·달리기·대시·점프·시전 모든 장의 얼굴 자리에 찍음(얼굴 + 앞머리 2칸). 맞기·쓰러지기는 표정이라 그대로.
# 찍은 장은 새 시트 anim/hero8_face.webp에 따로 넣고 anims가 그 칸을 가리키게 함(옛 시트는 그대로). 다시 돌려도 같은 결과.
import json,os,sys,numpy as np
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,D)
import faces
from facefix import ref_head,place2
ROOT=os.path.abspath(D+'/../../..');HTML=ROOT+'/test128/index.html';SHEET='anim/hero8_face.webp'
H=faces.H;cell=faces.cell
CLIPS={'down':['idle_down','walk_down','run_down','dash_down','jump_down'],
       'right':['idle_right','walk_right','run_right','dash_right','jump_right','cast_s1_right','cast_s2_right','cast_s3_right']}
if SHEET in H['sheets']:sys.exit('already applied')
H['sheets'].append(SHEET);H['cells'].append([]);si=len(H['sheets'])-1
done={};tiles=[];log={}
for d,clips in CLIPS.items():
    P,M=ref_head(cell(H['anims']['idle_'+d][0])[0])
    for k in clips:
        L=H['anims'][k];log[k]=[]
        for e in L:
            key=(e[0],e[1])
            if key not in done:
                a,ax,ay=cell(e);pad=8;big=np.zeros((a.shape[0]+2*pad,a.shape[1]+2*pad,4),np.uint8);big[pad:-pad,pad:-pad]=a
                o,sc=place2(big,P,M,thr=0.3)
                if sc is None or sc<0.3:done[key]=None
                else:
                    b=Image.fromarray(o).getbbox();t=Image.fromarray(o).crop(b)
                    tiles.append(t);done[key]=(len(tiles)-1,ax+pad-b[0],ay+pad-b[1])
            log[k].append(done[key] is not None)
            if done[key]:e[0],e[1]=si,done[key][0]
# 시트 만들기
W=2048;x=y=rowh=0;cells=[];pos=[]
for t in tiles:
    w,h=t.size
    if x+w>W:x=0;y+=rowh+1;rowh=0
    pos.append((x,y));x+=w+1;rowh=max(rowh,h)
sh=Image.new('RGBA',(W,y+rowh),(0,0,0,0))
for t,(x0,y0) in zip(tiles,pos):sh.paste(t,(x0,y0))
inv={v[0]:v for v in done.values() if v}
for i,(t,(x0,y0)) in enumerate(zip(tiles,pos)):cells.append([x0,y0,t.size[0],t.size[1],inv[i][1],inv[i][2]])
sh.save(ROOT+'/test128/assets/'+SHEET,lossless=True,method=6);H['cells'][si]=cells
H['_face_note']='owner 10-23: hero face stamped from idle_down/idle_right frame 0 onto walk/run/dash/jump/cast frames (handoff/claude/hero8_face_v1), sheet anim/hero8_face.webp; hurt/death keep their expressions'
s=open(HTML).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/')
open(HTML,'w').write(s[:j]+json.dumps(H,separators=(',',':'),ensure_ascii=False)+s[e:])
for k,v in log.items():print(k,''.join('O' if q else '.' for q in v))
