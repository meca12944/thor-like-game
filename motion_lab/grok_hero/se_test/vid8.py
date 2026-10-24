# 8방향 표 영상: 위 걷기 / 아래 달리기, 칸 ↓ ↘ → ↗ ↑ (새로 그린 것 = 노란 글씨). 걷기 6틱, 달리기 4틱 (60틱/초)
import glob,os,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',24)
G='..'
def L(p): return [Image.open(f).convert('RGBA').crop((40,0,216,200)) for f in sorted(glob.glob(p+'/*.png'))]
rows=[('걷기',6,[('↓',f'{G}/frames/walk_down',0),('↘',f'walk_se',1),('→',f'{G}/frames/walk_right',0),('↗','walk_ne',1),('↑',f'{G}/frames/walk_up',0)]),
      ('달리기',4,[('↓','run_s',1),('↘','run_se',1),('→',f'{G}/frames/run_right',0),('↗','run_ne',1),('↑','run_n',1)])]
rows=[(n,t,[(a,L(p),new) for a,p,new in cs]) for n,t,cs in rows]
S=2;CW=176*S;CH=200*S;D=tempfile.mkdtemp()
for k in range(30*8):
    can=Image.new('RGB',(CW*5,(CH+30)*2),(70,74,80));d=ImageDraw.Draw(can)
    for r,(n,t,cs) in enumerate(rows):
        for c,(a,fr,new) in enumerate(cs):
            if not fr: continue
            im=fr[(k*2//t)%len(fr)].resize((CW,CH),Image.NEAREST);y=r*(CH+30)+30
            can.paste(im,(c*CW,y),im);d.text((c*CW+10,y-28),f'{n} {a}'+(' 새' if new else ' 그록'),font=F,fill=(255,220,80) if new else (255,255,255))
            d.line([(c*CW,y+189*S),(c*CW+CW,y+189*S)],fill=(120,200,120))
    can.save(f'{D}/{k:04d}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{D}/%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','dir8_walkrun.mp4'],check=True);print('ok')
