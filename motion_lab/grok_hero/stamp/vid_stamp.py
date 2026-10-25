# 얼굴 도장 전·후 움직이는 영상 (게임 크기 144, 3배): 줄 = 정면·↘·옆 / 칸 = 걷기 전·후, 달리기 전·후
import glob,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',20)
G='..';S=3;CW=90;CH=110;D=tempfile.mkdtemp()
rows=[('정면','down'),('↘','dr'),('옆','right')]
cols=[('걷기 전','final','walk',6),('걷기 후','final_stamped','walk',6),('달리기 전','final','run',4),('달리기 후','final_stamped','run',4)]
L={}
for _,dn in rows:
    for _,root,m,_ in cols:
        fs=sorted(glob.glob(f'{G}/{root}/{m}_{dn}/*.png'));ims=[Image.open(f).convert('RGBA') for f in fs];b=ims[0].getbbox();cx=(b[0]+b[2])//2
        L[(root,m,dn)]=[im.crop((cx-CW//2,b[1]-6,cx+CW//2,b[1]-6+CH)) for im in ims]
for k in range(30*6):
    can=Image.new('RGB',(CW*S*4,(CH*S+26)*3),(70,74,80));d=ImageDraw.Draw(can)
    for r,(rn,dn) in enumerate(rows):
        for c,(cn,root,m,t) in enumerate(cols):
            fr=L[(root,m,dn)];im=fr[(k*2//t)%len(fr)].resize((CW*S,CH*S),Image.NEAREST);y=r*(CH*S+26)+26
            can.paste(im,(c*CW*S,y),im);d.text((c*CW*S+6,y-24),f'{rn} {cn}',font=F,fill=(255,220,80) if '후' in cn else (255,255,255))
    can.save(f'{D}/{k:04d}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{D}/%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','stamp_before_after.mp4'],check=True);print('ok')
