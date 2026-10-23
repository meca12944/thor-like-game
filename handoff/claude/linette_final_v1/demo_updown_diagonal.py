# Attacking while facing down/up with the diagonal attack art: down-right / down-left / up-right / up-left, picked by the last left/right facing.
import json,os,sys,subprocess,random
from PIL import Image,ImageDraw,ImageFont
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from fx import draw_thrust
A=json.load(open(H+'/atlas/linette8.json')); SH=[Image.open(H+'/atlas/'+os.path.basename(s)).convert('RGBA') for s in A['sheets']]; T=sys.argv[1]
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16); W,Hh=480,300
bg=Image.new('RGBA',(W,Hh),(86,124,70,255)); g=ImageDraw.Draw(bg); rnd=random.Random(3)
for _ in range(500): x,y=rnd.randrange(W),rnd.randrange(Hh); g.rectangle((x,y,x+1,y),fill=(72,108,58,255) if rnd.random()<.6 else (104,142,82,255))
DV={'down':(0,1),'up':(0,-1),'right':(1,0),'left':(-1,0)}
def seq(m,d,n=None):
    s=[];[s.extend([e]*e[2]) for e in A['anims'][f'{m}_{d}']]
    return [s[i%len(s)] for i in range(n)] if n else s
SCRIPT=[('walk','left',40,0.9,'왼쪽으로 걷기'),('walk','down',50,0.9,'아래로 걷기'),('combo','downl',None,0,'아래 공격 (왼쪽 대각선)'),('walk','right',40,0.9,'오른쪽으로 걷기'),('walk','up',50,0.9,'위로 걷기'),('combo','upr',None,0,'위 공격 (오른쪽 대각선)'),('walk','right',50,0.9,'오른쪽으로 걷기'),('walk','down',70,0.9,'아래로 걷기'),('combo','down',None,0,'아래 공격 (오른쪽 대각선)'),('idle','down',30,0,'다시 아래'),
        ('walk','left',50,0.9,'왼쪽으로 걷기'),('walk','up',70,0.9,'위로 걷기'),('combo','up',None,0,'위 공격 (왼쪽 대각선)'),('idle','up',30,0,'다시 위')]
x,y=240.0,150.0; k=0
for m,d,n,sp,lab in SCRIPT:
    ad={'upr':'up'}.get(d,d)
    parts=[('atk1',seq('atk1',ad)),('atk2',seq('atk2',ad)),('atk3',seq('atk3',ad))] if m=='combo' else [(m,seq(m,d,n))]
    for mm,S in parts:
        meta=A['thrust'].get(f'{mm}_{ad}'); lt=None
        for ti,e in enumerate(S):
            dx,dy=DV.get(d,(0,0)); x=min(W-150,max(150,x+dx*sp)); y=min(Hh-30,max(150,y+dy*sp))

            im=bg.copy(); ImageDraw.Draw(im).ellipse((x-24,y-6,x+24,y+5),fill=(0,0,0,60))
            s,c,_=e; cx,cy,w,h,ax,ay=A['cells'][s][c]; im.alpha_composite(SH[s].crop((cx,cy,cx+w,cy+h)),(int(x-ax),int(y-ay)))
            if meta:
                if lt is None and e==A['anims'][f'{mm}_{ad}'][meta['frame']]: lt=ti
                if lt is not None: draw_thrust(im,int(x),int(y),meta,ti-lt)
            ImageDraw.Draw(im).text((8,6),lab,font=F,fill='white')
            im.convert('RGB').resize((W*2,Hh*2),Image.NEAREST).save(f'{T}/f_{k:05d}.png'); k+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{T}/f_%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','20',H+'/linette_updown_diagonal_attack.mp4'],check=True); print(k)
