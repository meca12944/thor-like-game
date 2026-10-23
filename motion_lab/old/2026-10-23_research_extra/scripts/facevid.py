import json,numpy as np
from PIL import Image
from render2 import grid
R='/home/user/thor-like-game/test128/'
def atlas(path):
    s=open(path).read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');return json.loads(s[j:e])
SH={}
def frames(A,k):
    out=[]
    for e in A['anims'][k]:
        p=A['sheets'][e[0]]
        if p not in SH:SH[p]=Image.open(R+'assets/'+p).convert('RGBA')
        x,y,w,h,ax,ay=A['cells'][e[0]][e[1]];c=np.zeros((256,256,4),np.uint8);t=np.array(SH[p].crop((x,y,x+w,y+h)))
        oy,ox=189-ay,128-ax;c[max(0,oy):oy+h,max(0,ox):ox+w]=t[max(0,-oy):256-oy,max(0,-ox):256-ox][:c[max(0,oy):oy+h,max(0,ox):ox+w].shape[0],:c[max(0,oy):oy+h,max(0,ox):ox+w].shape[1]]
        # 얼굴 크게: 머리 둘레만 잘라 3배
        out.append(np.array(Image.fromarray(c).crop((88,55,168,115)).resize((240,180),Image.NEAREST)))
    return out,[e[2] for e in A['anims'][k]]
B=atlas('/tmp/claude-0/-home-user-thor-like-game/07fd8ca2-ea28-5b70-9774-cc61d04fa98a/scratchpad/index_before_face.html');N=atlas(R+'index.html')
def ticks(n,t):return [int((i+1)*t/n)-int(i*t/n) for i in range(n)]
rows=[]
for k,nm,cyc in [('walk_down','정면 걷기',31*2),('run_down','정면 달리기',26*2),('run_right','옆 달리기',26*2),('jump_right','옆 점프',None),('dash_down','정면 회피대시',None)]:
    fb,tb=frames(B,k);fn,tn=frames(N,k)
    t=ticks(len(fb),cyc) if cyc else [max(3,x*2) for x in tb]
    # 원래 그림(256)이 아니라 얼굴 확대본이라 화면에 맞게 놓기
    pad=lambda L:[np.pad(a,((60,16),(8,8),(0,0))) for a in L]
    rows.append((nm,[dict(frames=[np.pad(np.array(Image.fromarray(a).resize((128,96),Image.NEAREST)),((93,67),(64,64),(0,0))) for a in fb],ticks=t,label='전'),dict(frames=[np.pad(np.array(Image.fromarray(a).resize((128,96),Image.NEAREST)),((93,67),(64,64),(0,0))) for a in fn],ticks=t,label='후')]))
grid('hero_face_v1.mp4',rows,secs=6,W=200,H=120,S=3,title='주인공 얼굴 (머리 확대, 천천히) 왼쪽=전, 오른쪽=후')
