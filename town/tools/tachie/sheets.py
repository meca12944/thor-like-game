# lineup + per-character expression sheets for review (outdir arg)
import sys,os
from PIL import Image,ImageDraw,ImageFont
A=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../assets/tachie/')
O=sys.argv[1];os.makedirs(O,exist_ok=True)
ids=['hero','a_tailor','h_mystic','g_dancer','f_diver','e_tailor','c_priest','d_yuna']
names={'hero':'필멸자','a_tailor':'나비','h_mystic':'운','g_dancer':'방울','f_diver':'숨비','e_tailor':'루비','c_priest':'설화','d_yuna':'유나'}
EX=['neutral','smile','angry','sad','surprised','blush']
fp=[f for f in ['/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'] if os.path.exists(f)]
import glob
if not fp: fp=glob.glob('/usr/share/fonts/**/*CJK*',recursive=True)+glob.glob('/usr/share/fonts/**/*Nanum*',recursive=True)
F=ImageFont.truetype(fp[0],34) if fp else ImageFont.load_default()
def bg(w,h):
    im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im)
    for y in range(h):c=int(58+40*y/h);d.line([(0,y),(w,y)],fill=(c,c+8,c+28,255))
    return im
W,H=750,2150;s=.5
L=bg(int(W*s)*8,int(H*s)+70);d=ImageDraw.Draw(L)
for i,c in enumerate(ids):
    im=Image.open(A+f'{c}_neutral.png').resize((int(W*s),int(H*s)),Image.LANCZOS);L.alpha_composite(im,(i*int(W*s),0))
    d.text((i*int(W*s)+int(W*s)//2,int(H*s)+30),names[c],font=F,fill='white',anchor='mm')
L.convert('RGB').save(O+'/lineup_full_body.png');print('lineup')
for c in ids:
    s2=.42;cw,ch=int(W*s2),int(H*s2);fw=360
    S=bg(cw+3*fw,max(ch,2*(fw+50))+60);d=ImageDraw.Draw(S)
    S.alpha_composite(Image.open(A+f'{c}_neutral.png').resize((cw,ch),Image.LANCZOS),(0,40))
    d.text((10,6),f'{names[c]} ({c})',font=F,fill='white')
    for i,e in enumerate(EX):
        im=Image.open(A+f'{c}_{e}.png');fc=im.crop((175,40,575,490)).resize((fw,int(fw*450/400)),Image.LANCZOS)
        x=cw+(i%3)*fw;y=50+(i//3)*(fc.height+50);S.alpha_composite(fc,(x,y));d.text((x+fw//2,y+fc.height+20),e,font=F,fill='white',anchor='mm')
    S.convert('RGB').save(O+f'/expressions_{c}.png');print(c)
