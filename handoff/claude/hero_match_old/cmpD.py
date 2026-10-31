import json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',32);F2=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
def segs(R):
    L=json.load(open(R+'labels.json'));d={}
    for i,l in enumerate(L): d.setdefault(l,[]).append(i)
    for l in d:
        if l.startswith('맞기'): d[l]=d[l][-76:]
    return d
O=segs('recD_b/');N=segs('recD_a/')
ORD=['서기','걷기','달리기 ','출발','제자리','달리며','걷기→','대각선','회피대시','점프','달리기 점프','맞기']
def rank(l):
    if l.startswith('달리기 점프'): return ORD.index('달리기 점프')
    for i,k in enumerate(ORD):
        if l.startswith(k): return i
    return 99
labs=[l for l in dict.fromkeys(json.load(open('recD_a/labels.json'))) if l in O];out='recD_cmp/';os.makedirs(out,exist_ok=True);n=0
for l in labs:
    a,b=O[l],N[l];m=max(len(a),len(b))
    for t in range(m):
        ia=a[min(t,len(a)-1)];ib=b[min(t,len(b)-1)]
        c=Image.new('RGB',(1920,1080),(20,22,28));d=ImageDraw.Draw(c)
        c.paste(Image.open('recD_b/%05d.png'%ia).convert('RGB').resize((960,540),Image.NEAREST),(0,250))
        c.paste(Image.open('recD_a/%05d.png'%ib).convert('RGB').resize((960,540),Image.NEAREST),(960,250))
        d.text((20,190),'전: 8방향 그림 (대각선 그림)',font=F,fill=(255,210,160));d.text((980,190),'후: 4방향 그림 (대각선 = 옆 그림)',font=F,fill=(170,255,190))
        d.text((20,40),l,font=F,fill=(255,236,150));d.text((20,830),'%d틱'%t,font=F2,fill=(220,220,220))
        c.save(out+'%05d.png'%n);n+=1
print(n)
for fps,sfx in [(60,'_1x'),(18,'_03x')]:
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',out+'%05d.png','-c:v','libx264','-crf','27','-preset','slow','-pix_fmt','yuv420p','-r','60' if fps==60 else '36','dir4'+sfx+'.mp4'],check=True)
