import json,os,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',32);F2=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
B,A,lb,la,name=sys.argv[1:6];L=json.load(open(B+'labels.json'));out=name+'_frames/';os.makedirs(out,exist_ok=True);seg={}
for i,l in enumerate(L):
    seg.setdefault(l,0);t=seg[l];seg[l]+=1
    a=Image.open(B+'%05d.png'%i).convert('RGB').resize((960,540),Image.NEAREST);b=Image.open(A+'%05d.png'%i).convert('RGB').resize((960,540),Image.NEAREST)
    c=Image.new('RGB',(1920,620),(20,22,28));c.paste(a,(0,80));c.paste(b,(960,80));d=ImageDraw.Draw(c)
    d.text((20,20),lb,font=F,fill=(255,200,200));d.text((980,20),la,font=F,fill=(200,255,200));d.text((20,590),'%s  %d틱'%(l,t),font=F2,fill=(230,230,230))
    c.save(out+'%05d.png'%i)
for fps,sfx in [(18,'_03x'),(60,'_1x')]:
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',out+'%05d.png','-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-r','36' if fps==18 else '60',name+sfx+'.mp4'],check=True)
