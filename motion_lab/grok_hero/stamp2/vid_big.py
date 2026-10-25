# 원래 / v2 / A 나란히 (걷기 ↓ ↘ →, 100%와 300% 머리 확대) 6틱
import glob,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
from common import load,face
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',18)
G='..';roots=[('원래','final'),('v2','final_stamped2'),('A','final_stampedA')];dirs=['down','dr','right'];D=tempfile.mkdtemp()
fr={(r,d):[Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'{G}/{r}/walk_{d}/*.png'))] for _,r in roots for d in dirs}
fc={d:face(load(f'{G}/final/walk_{d}/000.png')) for d in dirs}
for k in range(30*4):
    can=Image.new('RGB',(3*(100+160)+20,3*170+30),(70,74,80));dr=ImageDraw.Draw(can)
    for j,(lab,r) in enumerate(roots):
        dr.text((j*(260)+10,4),lab+' 100% | 300%',font=F,fill=(255,220,80) if j else (255,255,255))
        for i,d in enumerate(dirs):
            im=fr[(r,d)][(k*2//6)%8];b=fr[('final',d)][0].getbbox();cx=(b[0]+b[2])//2
            body=im.crop((cx-50,b[1]-6,cx+50,b[1]+160));bg=Image.new('RGBA',body.size,(70,74,80,255));bg.alpha_composite(body)
            y=30+i*170;x=j*260;can.paste(bg.convert('RGB'),(x,y))
            cy,cxx=fc[d][0],fc[d][1];hd=im.crop((cxx-13,cy-15,cxx+13,cy+11));bg=Image.new('RGBA',hd.size,(70,74,80,255));bg.alpha_composite(hd)
            can.paste(bg.convert('RGB').resize((156,156),Image.NEAREST),(x+102,y))
    can.save(f'{D}/{k:04d}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{D}/%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','face_big_compare.mp4'],check=True);print('ok')
