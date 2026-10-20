# 3-hit thrust chain in 4 directions with the engine trail, played from the atlas -> MP4 (game speed x2 then 1/3 slow).
import json,os,sys,subprocess
from PIL import Image,ImageDraw,ImageFont
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from fx import draw_thrust
A=json.load(open(H+'/atlas/linette8.json')); SH=[Image.open(H+'/atlas/'+os.path.basename(s)).convert('RGBA') for s in A['sheets']]; T=sys.argv[1]
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
D=[('right','오른쪽'),('left','왼쪽')]; CW,CH=300,260
def seq(m,d):
    s=[]
    for j,e in enumerate(A['anims'][f'{m}_{d}']): s+=[(m,j,e)]*e[2]
    return s
k=0
for slow,lab in [(1,'게임 속도'),(1,'게임 속도'),(3,'1/3 느리게')]:
    chains={d:seq('atk1',d)+seq('atk2',d)+seq('atk3',d)+[('atk3',0,A['anims'][f'atk3_{d}'][0])]*20 for d,_ in D}
    n=max(len(v) for v in chains.values())
    for d in chains: chains[d]+=[chains[d][-1]]*(n-len(chains[d]))
    for t in range(n):
        im=Image.new('RGBA',(CW*2,CH),(86,124,70,255)); g=ImageDraw.Draw(im)
        for q,(d,dk) in enumerate(D):
            ox,oy=(q%2)*CW,(q//2)*CH; m,j,e=chains[d][t]; s,c,_=e; x,y,w,h,ax,ay=A['cells'][s][c]
            rx,ry=ox+(110 if d in ('right',) else 190 if d=='left' else 150),oy+(200 if d!='up' else 210)
            im.alpha_composite(SH[s].crop((x,y,x+w,y+h)),(rx-ax,ry-ay)); g.text((ox+6,oy+4),dk+f'  [{m[-1]}타]',font=F,fill='white')
            meta=A['thrust'][f'{m}_{d}']; first=next(i for i in range(len(chains[d])) if chains[d][i][0]==m and chains[d][i][1]==meta['frame'])
            if j>=meta['frame']: draw_thrust(im,rx,ry,meta,t-first)
        g.text((6,CH-20),lab,font=F,fill='white')
        f=im.convert('RGB').resize((CW*4,CH*2),Image.NEAREST)
        for _ in range(slow): f.save(f'{T}/f_{k:05d}.png'); k+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{T}/f_%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','20',H+'/linette_thrust_trail.mp4'],check=True); print(k)
