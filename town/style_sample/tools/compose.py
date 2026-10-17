"""Build the comparison PNGs + GIF from capture output."""
import json, glob, subprocess
from PIL import Image, ImageDraw, ImageFont
D='/workspace/town-demo/'; O=D+'style_sample/'
F=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf', s)
def label(img, xy, t, s=26, fill=(255,255,255)):
    d=ImageDraw.Draw(img); x,y=xy
    for dx in (-2,0,2):
        for dy in (-2,0,2): d.text((x+dx,y+dy),t,font=F(s),fill=(0,0,0))
    d.text(xy,t,font=F(s),fill=fill)
# 1) full screenshot
shot=Image.open(O+'work/shot_1920.png').convert('RGB'); shot.save(O+'sample_scene_1920x1080.png')
Image.open(O+'work/fps_overlay_1920.png').convert('RGB').save(O+'sample_scene_fps_overlay.png')
# 2) old vs new
old=Image.open(D+'shot.png').convert('RGB').resize((1280,720),Image.NEAREST); new=shot.resize((1280,720),Image.LANCZOS)
W=1280*2+30; cmp=Image.new('RGB',(W,720+60+520),(24,24,30))
cmp.paste(old,(0,60)); cmp.paste(new,(1310,60))
label(cmp,(10,12),'OLD  (live game: pixel-art bg, 384x216 grid, diagonal 3/4 view)',28,(255,200,160))
label(cmp,(1320,12),'NEW  (painted bg at screen res + 768x432 pixel sprites, front-facing)',28,(170,255,170))
# zoom row: same on-screen area around the hero, 3x
oc=Image.open(D+'shot.png').convert('RGB').crop((520,300,760,450)).resize((720,450),Image.NEAREST)
h=json.load(open(O+'fps_measure.json'))  # noqa (exists)
ns=Image.open(O+'work/shot_1920.png').convert('RGB')
nc=ns.crop((1050,690,1410,915)).resize((720,450),Image.NEAREST)   # 1920-space crop with same relative size (240/1280*1920=360)
cmp.paste(oc,(280,800)); cmp.paste(nc,(1310+280,800))
label(cmp,(290,770),'OLD zoom x3 (1280x720 capture)',22,(255,200,160)); label(cmp,(1600,770),'NEW zoom x2 (1920x1080 capture, same area)',22,(170,255,170))
cmp.save(O+'compare_old_vs_new.png')
# 3) sprite close-up sheet: old at 8x, new at 4x -> same on-screen size, shows the detail difference
A=json.load(open(D+'assets/anim/hero.json')); hp=Image.open(D+'assets/anim/hero.png').convert('RGBA')
def oldcell(i):
    x,y,w,hh,ax,ay=A['cells'][i]; return hp.crop((x,y,x+w,y+hh))
nh=Image.open(O+'assets/hero_hd.png'); nj=json.load(open(O+'assets/hero_hd.json'))['cells']
nf=Image.open(O+'assets/fem_hd.png'); fj=json.load(open(O+'assets/fem_hd.json'))['cells']
def nc_(img,c): x,y,w,hh,ax,ay=c; return img.crop((x,y,x+w,y+hh))
def oldfem(id_, hgt=20):
    im=Image.open(D+'assets/npcs/'+id_+'.png').convert('RGBA'); w=max(1,round(im.width*hgt/im.height)); return im.resize((w,hgt),Image.LANCZOS)
BG=(84,108,74); sheet=Image.new('RGB',(2200,1700),(30,30,36)); d=ImageDraw.Draw(sheet)
def row(y, items, mag, title, col):
    label(sheet,(20,y),title,24,col); x=20; base=y+40+70*8 if mag==8 else y+40+70*4
    tile=Image.new('RGB',(2160,  (30*8 if mag==8 else 70*4)+20),BG)
    sheet.paste(tile,(20,y+36))
    bottom=y+36+tile.height-10
    for im in items:
        if im is None: x+=40; continue
        b=im.resize((im.width*mag,im.height*mag),Image.NEAREST); sheet.paste(b,(x+10,bottom-b.height),b); x+=b.width+24
row(20,[oldcell(i) for i in (15,16,17,18)]+[None]+[oldcell(i) for i in (9,10,11,12)]+[None]+[oldcell(i) for i in (21,22)]+[None,None]+[oldfem('a_tool'),oldfem('g_tool')],8,
    'OLD  (current game, 384x216 grid) - hero 28px walk down / right / up, female NPC 20px (a_tool 미소, g_tool 사프란) - shown x8',(255,200,160))
row(330,[nc_(nh,c) for c in nj['down']]+[None]+[nc_(nh,c) for c in nj['right'][:4]]+[None]+[nc_(nh,c) for c in nj['up'][:2]]+[None]+[nc_(nf,c) for c in fj['down']],4,
    'NEW  (768x432 grid) - hero 56px walk down / right / up, adult female NPC 68px walk (7.9 heads, legs 0.50) - shown x4 (= same screen size as x8 above)',(170,255,170))
# 1:1 in-game size strip
label(sheet,(20,680),'Actual in-game size on a 1920x1080 screen (OLD x5 nearest, NEW x2.5 sharp-bilinear):',22,(220,220,220))
strip=Image.new('RGB',(2160,200),BG); sheet.paste(strip,(20,716)); x=40
for im,m in [(oldcell(15),5),(oldfem('a_tool'),5)]:
    b=im.resize((im.width*m,im.height*m),Image.NEAREST); sheet.paste(b,(x,900-b.height),b); x+=b.width+40
x+=120
for im in [nc_(nh,nj['down'][0]),nc_(nf,fj['down'][1])]:
    b=im.resize((im.width*3,im.height*3),Image.NEAREST).resize((round(im.width*2.5),round(im.height*2.5)),Image.BILINEAR); sheet.paste(b,(x,900-b.height),b); x+=b.width+40
# big detail close-up
label(sheet,(20,940),'Detail x8: NEW hero / NEW female (palette 40 / 48 colours, 1px selective outline, stray-pixel cleanup)',22,(170,255,170))
cl=Image.new('RGB',(2160,720),BG); sheet.paste(cl,(20,976)); x=40
for im in [nc_(nh,nj['down'][1]),nc_(nh,nj['right'][2]),nc_(nf,fj['down'][1])]:
    b=im.resize((im.width*10,im.height*10),Image.NEAREST); sheet.paste(b,(x,1690-b.height),b); x+=b.width+60
sheet.save(O+'sprites_closeup_old_vs_new.png')
print('ok')
