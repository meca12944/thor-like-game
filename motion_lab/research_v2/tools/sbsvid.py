# 전·후 나란히 영상: python3 sbsvid.py <전 폴더> <후 폴더> <이름(앞)>  -> <이름>_slow.mp4 (12fps), <이름>_real.mp4 (60fps)
import os,sys,subprocess,shutil,tempfile
from PIL import Image,ImageDraw,ImageFont
A,B,N=sys.argv[1:4];S=tempfile.mkdtemp();F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
for i,f in enumerate(sorted(os.listdir(A))):
    a=Image.open(f'{A}/{f}').convert('RGB');b=Image.open(f'{B}/{f}').convert('RGB')
    W=Image.new('RGB',(648,292),(20,20,20));W.paste(a,(0,32));W.paste(b,(328,32));d=ImageDraw.Draw(W)
    d.text((10,8),'전 (지금 게임)',fill=(255,200,120),font=F);d.text((338,8),'후 (새 때리기)',fill=(140,230,255),font=F)
    W.resize((1296,584),Image.NEAREST).save(f'{S}/{i:04d}.png')
for fps,t in((12,'slow'),(60,'real')):subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',f'{S}/%04d.png','-pix_fmt','yuv420p',f'{N}_{t}.mp4'])
shutil.copy(f'{S}/0020.png',f'{N}_peek.png');shutil.rmtree(S)
