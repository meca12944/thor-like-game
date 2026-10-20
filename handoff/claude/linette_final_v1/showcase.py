# Plays a short scripted sequence straight from the atlas (linette8.json + sheets) on a plain field -> MP4. Validates the atlas end to end.
import json,os,sys,subprocess,random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from fx import draw_thrust
from PIL import Image,ImageDraw,ImageFont
H=os.path.dirname(os.path.abspath(__file__)); A=json.load(open(H+'/atlas/linette8.json')); T=sys.argv[1]
SH=[Image.open(H+'/atlas/'+os.path.basename(s)).convert('RGBA') for s in A['sheets']]
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
W,Hh=480,300
bg=Image.new('RGBA',(W,Hh),(86,124,70,255)); g=ImageDraw.Draw(bg); rnd=random.Random(3)
for _ in range(500): x,y=rnd.randrange(W),rnd.randrange(Hh); g.rectangle((x,y,x+1,y),fill=(72,108,58,255) if rnd.random()<.6 else (104,142,82,255))
def cell(e): s,c,_=e; x,y,w,h,ax,ay=A['cells'][s][c]; return SH[s].crop((x,y,x+w,y+h)),ax,ay
def frames(m,d,loop_ticks=None):
    L=A['anims'][f'{m}_{d}']; seq=[]
    for e in L: seq+=[e]*e[2]
    if loop_ticks: seq=[seq[i%len(seq)] for i in range(loop_ticks)]
    return seq
DV={'down':(0,1),'up':(0,-1),'right':(1,0),'left':(-1,0)}
# (motion, dir, ticks or None for one shot, move px/tick, label)
SCRIPT=[('idle','down',60,0,'대기'),('walk','down',70,0.9,'걷기'),('walk','right',90,0.9,'걷기'),('run','right',80,2.2,'달리기'),
        ('dash','right',None,4.0,'대시'),('atk1','right',None,0.4,'1타'),('atk2','right',None,0.4,'2타'),('atk3','right',None,0.6,'3타'),
        ('idle','right',30,0,'대기'),('hurt','right',None,-0.8,'맞기'),('run','up',60,2.2,'달리기'),('walk','left',90,0.9,'걷기'),
        ('run','left',70,2.2,'달리기'),('atk1','left',None,0.4,'1타'),('atk2','left',None,0.4,'2타'),('atk3','left',None,0.6,'3타'),
        ('run','down',50,2.2,'달리기'),('cast','down',None,0,'시전'),('atk1','down',None,0.4,'1타'),('atk2','down',None,0.4,'2타'),('atk3','down',None,0.6,'3타'),('run','up',40,2.2,'달리기'),('atk1','up',None,0.4,'1타'),('atk2','up',None,0.4,'2타'),('atk3','up',None,0.6,'3타'),
        ('death','down',None,0,'사망'),('death','down',40,0,'사망')]
x,y=120.0,200.0; k=0
for m,d,ticks,sp,lab in SCRIPT:
    seq=frames(m,d,ticks) if ticks else frames(m,d)
    if m=='death' and ticks: seq=[A['anims'][f'{m}_{d}'][-1]]*ticks
    lunge_t=None
    for ti,e in enumerate(seq):
        dx,dy=DV[d]; x=min(W-150,max(150,x+dx*sp)); y=min(Hh-20,max(130,y+dy*sp))
        im=bg.copy(); ImageDraw.Draw(im).ellipse((x-24,y-6,x+24,y+5),fill=(0,0,0,60))
        c,ax,ay=cell(e); im.alpha_composite(c,(int(x-ax),int(y-ay)))
        meta=A.get('thrust',{}).get(f'{m}_{d}')
        if meta:
            fi=[q for q in A['anims'][f'{m}_{d}']].index(e) if e in A['anims'][f'{m}_{d}'] else -1
            if lunge_t is None and e==A['anims'][f'{m}_{d}'][meta['frame']]: lunge_t=ti
            if lunge_t is not None: draw_thrust(im,int(x),int(y),meta,ti-lunge_t)
        ImageDraw.Draw(im).text((8,6),f'리네트 · {lab} · {d}',font=F,fill='white')
        im.convert('RGB').resize((W*2,Hh*2),Image.NEAREST).save(f'{T}/f_{k:05d}.png'); k+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{T}/f_%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','20',H+'/linette_showcase.mp4'],check=True)
print('frames',k)
