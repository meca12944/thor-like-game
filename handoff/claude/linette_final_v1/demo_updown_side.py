# What attacking while facing down/up looks like when only side attacks exist: the attack uses the last left/right facing
# (common in top-down action games), then she turns back to the walking direction.
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
SCRIPT=[('walk','right',50,0.9,'오른쪽으로 걷기'),('walk','down',70,0.9,'아래로 걷기'),('combo','right',None,0,'아래 보는 중 공격 → 마지막 좌우(오른쪽) 공격'),('idle','down',30,0,'다시 아래'),
        ('walk','left',50,0.9,'왼쪽으로 걷기'),('walk','up',70,0.9,'위로 걷기'),('combo','left',None,0,'위 보는 중 공격 → 마지막 좌우(왼쪽) 공격'),('idle','up',30,0,'다시 위')]
x,y=240.0,150.0; k=0
for m,d,n,sp,lab in SCRIPT:
    parts=[('atk1',seq('atk1',d)),('atk2',seq('atk2',d)),('atk3',seq('atk3',d))] if m=='combo' else [(m,seq(m,d,n))]
    for mm,S in parts:
        meta=A['thrust'].get(f'{mm}_{d}'); lt=None
        for ti,e in enumerate(S):
            dx,dy=DV[d]; x=min(W-150,max(150,x+dx*sp)); y=min(Hh-30,max(150,y+dy*sp))
            if mm.startswith('atk'): x=min(W-150,max(150,x+DV[d][0]*0.35))
            im=bg.copy(); ImageDraw.Draw(im).ellipse((x-24,y-6,x+24,y+5),fill=(0,0,0,60))
            s,c,_=e; cx,cy,w,h,ax,ay=A['cells'][s][c]; im.alpha_composite(SH[s].crop((cx,cy,cx+w,cy+h)),(int(x-ax),int(y-ay)))
            if meta:
                if lt is None and e==A['anims'][f'{mm}_{d}'][meta['frame']]: lt=ti
                if lt is not None: draw_thrust(im,int(x),int(y),meta,ti-lt)
            ImageDraw.Draw(im).text((8,6),lab,font=F,fill='white')
            im.convert('RGB').resize((W*2,Hh*2),Image.NEAREST).save(f'{T}/f_{k:05d}.png'); k+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{T}/f_%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','20',H+'/linette_updown_uses_side_attack.mp4'],check=True); print(k)
