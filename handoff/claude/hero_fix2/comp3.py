import json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
R='rec3/';L=json.load(open(R+'labels.json'))
segs={}
for i,l in enumerate(L): segs.setdefault(l,[]).append(i)
order=[];
for l,ids in segs.items():
  if l.startswith('맞기'): ids=ids[-76:]
  order.append((l,ids))
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',32);F2=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
out='rec3_out/';os.makedirs(out,exist_ok=True)
for f in os.listdir(out): os.remove(out+f)
n=0
for l,ids in order:
  for t,i in enumerate(ids):
    im=Image.open(R+'%05d.png'%i).convert('RGB').resize((1280,720),Image.NEAREST)
    d=ImageDraw.Draw(im);w=d.textlength(l,font=F)
    d.rectangle((12,12,32+w,60),fill=(0,0,0));d.text((22,18),l,font=F,fill=(255,236,150))
    s='%d틱'%t;d.rectangle((12,668,40+d.textlength(s,font=F2)*1,700),fill=(0,0,0));d.text((22,676),s,font=F2,fill=(200,200,200))
    d.text((1000,684),'새 주인공 fix4 · 2배 (과장·방향 전환)',font=F2,fill=(220,220,220))
    im.save(out+'%05d.png'%n);n+=1
print('frames',n)
for fps,name in [(60,'fix4_hero_169_1x.mp4'),(18,'fix4_hero_169_03x.mp4')]:
  subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',out+'%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-r','60' if fps==60 else '36',name],check=True)
