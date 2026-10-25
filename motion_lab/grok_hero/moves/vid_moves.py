# PC 16:9 비교 영상(사장님 10-25 「PC용, 1080p 100%」): 1920×1080, 칸마다 [서기 0.5초 → 동작 → 서기 0.5초] 반복. 8방향(왼쪽 = 뒤집기), 배율 S
import sys,glob,json,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont,ImageOps
kind=sys.argv[1];S=int(sys.argv[2]) if len(sys.argv)>2 else 2
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',28);M=json.load(open('moves.json'))
D8=[('down','↓',0),('dr','↘',0),('right','→',0),('ur','↗',0),('up','↑',0),('ur','↖',1),('right','←',1),('dr','↙',1)]
def seq(d,fl):
    k=f'{kind}_{d}'
    if k not in M: return None
    ims=[Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'{k}/*.png'))];idle=Image.open(f'idle_{d}.png').convert('RGBA')
    out=[idle]*30
    for im,t in zip(ims,M[k]['ticks']): out+= [im]*t
    out+=[idle]*30
    return [ImageOps.mirror(i) if fl else i for i in out]
cells=[(lab,seq(d,fl)) for d,lab,fl in D8];cells=[c for c in cells if c[1]]
D=tempfile.mkdtemp();N=max(len(c[1]) for c in cells)*2
cw,ch=1920//4,1080//2
for k in range(0,N,2):   # 60틱 → 30fps
    can=Image.new('RGB',(1920,1080),(62,66,72));dr=ImageDraw.Draw(can)
    for i,(lab,fr) in enumerate(cells):
        x,y=(i%4)*cw,(i//4)*ch;im=fr[k%len(fr)].crop((28,10,228,200)).resize((200*S,190*S),Image.NEAREST)
        can.paste(im,(x+(cw-200*S)//2,y+ch-190*S-20),im);dr.text((x+12,y+8),f'{kind} {lab}',font=F,fill=(255,230,120))
        dr.line([(x,y+ch-20-190*S+179*S),(x+cw,y+ch-20-190*S+179*S)],fill=(90,140,90))
    can.save(f'{D}/{k//2:04d}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{D}/%04d.png','-c:v','libx264','-pix_fmt','yuv420p',f'{kind}_8dir.mp4'],check=True);print(kind,'ok')
