import json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',28);F2=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
def segs(R):
    L=json.load(open(R+'labels.json'));d={}
    for i,l in enumerate(L): d.setdefault(l,[]).append(i)
    for l in d:
        if l.startswith('맞기'): d[l]=d[l][-76:]
    return d
P=[('recR_old/','옛 주인공'),('recR_A/','달리기 A: 옛 빠르기 174 (미끄러짐) + 숙임'),('recR_B/','달리기 B: 중간 96 (미끄럼 10% 안) + 숙임')]
S=[segs(r) for r,_ in P]
ORD=['서기','걷기','달리기 ','출발','제자리','달리며','걷기→','대각선','회피대시','점프','달리기 점프','맞기']
def rank(l):
    if l.startswith('달리기 점프'): return ORD.index('달리기 점프')
    for i,k in enumerate(ORD):
        if l.startswith(k): return i
    return 99
labs=sorted([l for l in S[0] if all(l in s for s in S)],key=rank);out='recRAB_cmp/';os.makedirs(out,exist_ok=True);n=0
for l in labs:
    m=max(len(s[l]) for s in S)
    for t in range(m):
        c=Image.new('RGB',(1920,1080),(20,22,28));d=ImageDraw.Draw(c)
        for j,((r,lab),s) in enumerate(zip(P,S)):
            ids=s[l];im=Image.open(r+'%05d.png'%ids[min(t,len(ids)-1)]).convert('RGB').resize((960,540),Image.NEAREST);x=(j%2)*960 if j<2 else 480;y=(j//2)*540;c.paste(im,(x,y))
            d.rectangle((x+6,y+6,x+14+d.textlength(lab,font=F),y+42),fill=(0,0,0));d.text((x+10,y+10),lab,font=F,fill=(255,236,150))
        lt='%s  %d틱'%(l,t);d.rectangle((820,1040,1100,1074),fill=(0,0,0));d.text((830,1048),lt,font=F2,fill=(230,230,230))
        c.save(out+'%05d.png'%n);n+=1
print(n)
for fps,sfx in [(60,'_1x'),(18,'_03x')]:
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',out+'%05d.png','-c:v','libx264','-crf','30','-preset','slow','-pix_fmt','yuv420p','-r','60' if fps==60 else '36','run_AB_lean'+sfx+'.mp4'],check=True)
