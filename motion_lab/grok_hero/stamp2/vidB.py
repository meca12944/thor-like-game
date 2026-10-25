# 얼굴 도장 v2 전·후 영상: ① 8방향 원 배치(가운데 비움) ② 제자리 돌기(45°씩 0.5초). 걷기 6틱·달리기 4틱(60틱/초). 왼쪽 = 오른쪽 뒤집기. 배율 S(1 = 100%)
import glob,subprocess,tempfile,sys,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
S=int(sys.argv[1]) if len(sys.argv)>1 else 1;F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',12*max(1,S//2)+4)
G='..'
D8=[('down',None),('dr',None),('right',None),('ur',None),('up',None),('ur','f'),('right','f'),('dr','f')]  # ↓ ↘ → ↗ ↑ ↖ ← ↙
def L(root,m,d,flip):
    ims=[Image.open(f).convert('RGBA').crop((78,30,178,194)) for f in sorted(glob.glob(f'{G}/{root}/{m}_{d}/*.png'))]
    return [ImageOps.mirror(i) for i in ims] if flip else ims
CW,CH=100,164
def frame_circle(k,root,m,t):
    can=Image.new('RGBA',(CW*3,CH*3),(70,74,80,255))
    pos=[(1,2),(2,2),(2,1),(2,0),(1,0),(0,0),(0,1),(0,2)]
    for (d,fl),(cx,cy) in zip(D8,pos):
        fr=L(root,m,d,fl);can.alpha_composite(fr[(k*2//t)%len(fr)],(cx*CW,cy*CH))
    return can
CACHE={}
def Lc(root,m,d,fl):
    key=(root,m,d,fl)
    if key not in CACHE: CACHE[key]=L0(root,m,d,fl)
    return CACHE[key]
L0=L;L=Lc
for kind in ('circle','turn'):
    D=tempfile.mkdtemp();N=30*8
    for k in range(N):
        cols=[]
        for m,t in (('walk',6),('run',4)):
            for lab,root in (('전','final'),('후','final_stampedB')):
                if kind=='circle': im=frame_circle(k,root,m,t)
                else:
                    d,fl=D8[(k//15)%8];fr=L(root,m,d,fl);im=Image.new('RGBA',(CW,CH),(70,74,80,255));im.alpha_composite(fr[(k*2//t)%len(fr)])
                cols.append((f'{"걷기" if m=="walk" else "달리기"} {lab}',im))
        w=sum(c[1].width for c in cols)+10*len(cols);h=cols[0][1].height+20
        can=Image.new('RGB',(w,h),(70,74,80));x=0;dr=ImageDraw.Draw(can)
        for lab,im in cols: can.paste(im.convert('RGB'),(x,20));dr.text((x+2,2),lab,font=F,fill=(255,220,80) if '후' in lab else (255,255,255));x+=im.width+10
        if S>1: can=can.resize((can.width*S,can.height*S),Image.NEAREST)
        can.save(f'{D}/{k:04d}.png')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{D}/%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2',f'faceB_{kind}_x{S}.mp4'],check=True);print(kind,S,'ok')
