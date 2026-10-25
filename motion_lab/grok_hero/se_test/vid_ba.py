# 고치기 전·후 8방향(↓↘→↗↑) 걷기·달리기: 위 2줄 = 전, 아래 2줄 = 후(해결안 B). 노란 글씨 = 바뀐 칸
import glob,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',22)
G='../frames'
def L(p): return [Image.open(f).convert('RGBA').crop((40,0,216,200)) for f in sorted(glob.glob(p+'/*.png'))]
BEFORE=[('전 걷기',6,[f'{G}/walk_down','walk_se',f'{G}/walk_right','walk_ne',f'{G}/walk_up']),('전 달리기',4,['run_s','run_se',f'{G}/run_right','run_ne','run_n'])]
AFTER=[('후 걷기',6,['walk_s2','walk_se','walk_r2','walk_ne',f'{G}/walk_up']),('후 달리기',4,['run_s2_leg','run_se3','run_r3','run_ne2','run_n'])]
rows=[(n,t,[L(p) for p in ps],[a!=b for a,b in zip(ps,ref)]) for (n,t,ps),(_,_,ref) in zip(BEFORE+AFTER,BEFORE+BEFORE)]
A='↓↘→↗↑';S=2;CW=176*S;CH=200*S;D=tempfile.mkdtemp()
for k in range(30*8):
    can=Image.new('RGB',(CW*5,(CH+30)*4),(70,74,80));d=ImageDraw.Draw(can)
    for r,(n,t,cs,ch) in enumerate(rows):
        y=r*(CH+30)+30
        for c,fr in enumerate(cs):
            im=fr[(k*2//t)%len(fr)].resize((CW,CH),Image.NEAREST);can.paste(im,(c*CW,y),im)
            d.text((c*CW+8,y-28),f'{n} {A[c]}',font=F,fill=(255,220,80) if ch[c] else (255,255,255));d.line([(c*CW,y+189*S),(c*CW+CW,y+189*S)],fill=(120,200,120))
        if r==2: d.line([(0,y-31),(CW*5,y-31)],fill=(255,255,255),width=3)
    can.save(f'{D}/{k:04d}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{D}/%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','before_after_8dir.mp4'],check=True);print('ok')
