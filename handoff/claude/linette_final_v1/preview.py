# Render the whole Linette set (manifest ticks, 60fps) as one grid MP4: 2 panels x 5 motions, 4 directions each.
import json,glob,subprocess,os,sys
from PIL import Image,ImageDraw,ImageFont
H=os.path.dirname(os.path.abspath(__file__)); T=sys.argv[1]
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
man=json.load(open(H+'/manifest.json'))['motions']
M=[('idle','대기'),('walk','걷기'),('run','달리기'),('dash','대시'),('hurt','맞기'),('death','사망'),('cast','시전'),('atk1','1타'),('atk2','2타'),('atk3','3타')]
D=[('down','아래'),('up','위'),('left','왼쪽'),('right','오른쪽')]
fr={(m,d):[Image.open(f).convert('RGBA').crop((38,40,218,200)) for f in sorted(glob.glob(f'{H}/frames_polished/{m}/{d}/*.png'))] for m,_ in M for d,_ in D if d in man[m]}
def seq(m,d):
    s=[];[s.extend([i]*t) for i,t in enumerate(man[m][d]['ticks'])]
    if m in('death','hurt','dash','cast') or m.startswith('atk'): s+= [len(man[m][d]['ticks'])-1]*20 if m=='death' else [s[-1]]*8
    return s
CW,CH=180,160;LW=56;TH=24;PW=LW+CW*4;W=PW*2+10;Hh=TH+CH*5+8
for t in range(600):
    im=Image.new('RGBA',(W,Hh),(150,150,155,255));g=ImageDraw.Draw(im)
    for p in range(2):
        x0=p*(PW+10)
        for j,(d,dk) in enumerate(D): g.text((x0+LW+j*CW+70,4),dk,font=F,fill='black')
        for r,(m,mk) in enumerate(M[p*5:p*5+5]):
            g.text((x0+4,TH+r*CH+70),mk,font=F,fill='black')
            for j,(d,_) in enumerate(D):
                if d not in man[m]: continue   # attacks: side only
                q=seq(m,d); im.alpha_composite(fr[(m,d)][q[t%len(q)]],(x0+LW+j*CW,TH+r*CH))
    im.convert('RGB').resize((W*3//2//2*2,Hh*3//2//2*2),Image.NEAREST).save(f'{T}/f_{t:04d}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{T}/f_%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','22',H+'/linette_all_motions_v1.mp4'],check=True)
print('ok')
