# stick-figure preview of the designed skeletons (side / se / ne) over the faint rotation image -> mp4. no API calls.
import json,sys,math,subprocess,os
from PIL import Image,ImageDraw,ImageFont
FT=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',20)
d,rot,out=sys.argv[1:4]
V=[('side','east'),('se','south-east'),('ne','north-east')]
KP={v:json.load(open(f'{d}/{v}_kp.json')) for v,_ in V};SW=json.load(open(f'{d}/side_sword.json'))
B=[('NECK','RIGHT SHOULDER'),('NECK','LEFT SHOULDER'),('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),
   ('NECK','LEFT HIP'),('NECK','RIGHT HIP'),('LEFT HIP','RIGHT HIP'),('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG'),('NECK','NOSE')]
SC=3;CW,CH=150,130;OX,OY=55,60
fd='/tmp/claude-0/-home-user-thor-like-game/4298454f-7792-57d3-97c3-1442667121ee/scratchpad/atk3/pv';os.makedirs(fd,exist_ok=True)
bg={v:Image.open(f'{rot}/rot_{r}.png').convert('RGBA').crop((OX,OY,OX+CW,OY+CH)).resize((CW*SC,CH*SC),Image.NEAREST) for v,r in V}
for v in bg: a=bg[v].split()[3].point(lambda x:x*0.3);bg[v].putalpha(a)
seq=[(n,i) for n in ('h1','h2','h3') for i in range(len(KP['side'][n]))]
for f,(n,i) in enumerate(seq):
    im=Image.new('RGB',(CW*SC*3,CH*SC+30),(24,26,32));g=ImageDraw.Draw(im)
    for c,(v,_) in enumerate(V):
        im.paste(bg[v],(c*CW*SC,30),bg[v]);J={k['label']:((k['x']*256-OX)*SC+c*CW*SC,(k['y']*256-OY)*SC+30) for k in KP[v][n][i]}
        for a,b in B:
            col=(255,120,90) if ('LEFT' if v=='se' else 'RIGHT') in a+b else (110,170,255) if ('RIGHT' if v=='se' else 'LEFT') in a+b else (230,230,230)
            g.line([J[a],J[b]],fill=col,width=5)
        g.ellipse([J['NOSE'][0]-14,J['NOSE'][1]-14,J['NOSE'][0]+14,J['NOSE'][1]+14],outline=(230,230,230),width=4)
        a=math.radians(SW[n][i]['sw']);dx,dy=math.sin(a)*40,math.cos(a)*40
        if v!='side': sg=1 if v=='se' else -1;dx,dy=0.71*dx,dy+sg*0.41*dx
        h=J['LEFT ARM' if v=='se' else 'RIGHT ARM'];g.line([h,(h[0]+dx*SC,h[1]+dy*SC)],fill=(255,230,80),width=6)
        g.text((c*CW*SC+8,6),{'side':'→ 옆','se':'↘ 앞대각','ne':'↗ 뒤대각'}[v],fill=(255,255,255),font=FT)
    g.text((CW*SC*3-120,6),f'{n[1]}타 {i+1:02d}',fill=(255,255,255),font=FT)
    im.save(f'{fd}/{f:03d}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','10','-i',f'{fd}/%03d.png','-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2','-pix_fmt','yuv420p','-c:v','libx264',out],check=True);print('ok',len(seq),out)
