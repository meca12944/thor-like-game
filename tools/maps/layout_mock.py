# Mockups for map layout + HUD placement (no credits). usage: python3 layout_mock.py <font_dir> <mood_after.png> <out_dir>
import sys,math
from PIL import Image,ImageDraw,ImageFont
FD,BG,OUT=sys.argv[1:4]
F=lambda s,n='Galmuri11':ImageFont.truetype(f'{FD}/{n}.ttf',s)
OL=(35,25,39);GOLD=(176,138,84);GOLD2=(232,196,120);DARK=(20,15,26)
def frame(d,b,fill=(24,18,30,210)):
    x0,y0,x1,y1=b;d.rectangle(b,fill=fill,outline=OL);d.rectangle((x0+1,y0+1,x1-1,y1-1),outline=GOLD)
    for cx,cy in((x0,y0),(x1,y0),(x0,y1),(x1,y1)):d.rectangle((cx-1,cy-1,cx+1,cy+1),fill=GOLD2)
def bar(d,x,y,w,h,v,col,back=(40,30,46)):
    d.rectangle((x,y,x+w,y+h),fill=back,outline=OL);d.rectangle((x+1,y+1,x+1+int((w-2)*v),y+h-1),fill=col)
    d.line((x+1,y+1,x+int((w-2)*v),y+1),fill=tuple(min(255,c+60) for c in col))
# ---------- HUD over arena (drawn at half res, x2 nearest = chunky pixels) ----------
a=Image.open(BG).convert('RGB');a=a.resize((int(a.width*1.25),int(a.height*1.25)),Image.NEAREST)
scr=Image.new('RGB',(1920,1080),DARK);scr.paste(a,((1920-a.width)//2,(1080-a.height)//2))
def hud(notes):
    h=Image.new('RGBA',(960,540));d=ImageDraw.Draw(h)
    # top-left: dew-gem badge + HP/MP/EXP
    frame(d,(8,8,168,44));d.ellipse((12,12,40,40),fill=(30,22,38),outline=GOLD);d.ellipse((20,17,32,29),fill=(110,170,235),outline=OL)
    d.text((17,30),'12',font=F(8,'Galmuri9'),fill=GOLD2)
    bar(d,46,13,116,7,.72,(196,52,60));bar(d,46,24,96,5,.55,(70,120,220));bar(d,46,33,116,2,.4,(230,200,80))
    d.text((120,12),'86/120',font=F(8,'Galmuri9'),fill=(240,230,220))
    # top-center: champion / boss bar (only in fights)
    d.text((480,10),"챔피언 · 돌엄니",font=F(11),fill=(240,206,150),anchor='mt');bar(d,330,26,300,6,.64,(170,40,48));d.line((330,34,630,34),fill=GOLD)
    # top-right: minimap, faded in combat pockets
    mm=Image.new('RGBA',(120,84));md=ImageDraw.Draw(mm);frame(md,(0,0,119,83),fill=(24,18,30,160))
    for b in((14,30,44,54),(44,38,76,46),(76,20,106,62)):md.rectangle(b,fill=(90,80,100,170))
    md.rectangle((58,10,62,38),fill=(90,80,100,170));md.point([(90,40)],fill=(255,255,255));md.rectangle((89,39,91,41),fill=GOLD2)
    md.line((29,42,60,42,90,40),fill=(120,200,255,200));mm.putalpha(mm.getchannel('A').point(lambda v:int(v*.55)))
    h.alpha_composite(mm,(832,8))
    # right-middle: combo
    d.text((936,200),'12',font=F(22),fill=(250,214,90),anchor='rm');d.text((936,222),'HITS',font=F(11),fill=(250,214,90),anchor='rm');d.rectangle((880,232,936,233),fill=(250,214,90))
    # bottom-left: skills 1 2 3 Q + potion E
    for i,(k,cd) in enumerate((('1',0),('2',.6),('3',0),('Q',.3))):
        x=10+i*30;frame(d,(x,500,x+26,526));d.rectangle((x+5,505,x+21,521),fill=[(90,150,220),(220,140,60),(140,200,120),(170,110,220)][i])
        if cd:d.rectangle((x+2,503,x+24,503+int(21*cd)),fill=(0,0,0,150))
        d.text((x+24,524),k,font=F(8,'Galmuri9'),fill=(255,255,255),anchor='rb')
    frame(d,(134,500,160,526));d.rectangle((143,505,151,519),fill=(200,50,60),outline=OL);d.text((158,524),'×3',font=F(8,'Galmuri9'),fill=(255,255,255),anchor='rb');d.text((136,502),'E',font=F(8,'Galmuri9'),fill=GOLD2)
    # bottom-center: ultimate gauge
    bar(d,380,522,200,4,.62,(232,196,120));d.text((480,518),'필살 62%',font=F(8,'Galmuri9'),fill=(232,196,120),anchor='mb')
    # hit enemy only: tiny bar over head
    bar(d,646,316,26,2,.4,(200,60,60))
    if notes:
        d.rectangle((192,108,768,432),outline=(255,255,255,90));d.text((480,112),'가운데 60% — UI 없음 (적 예고만)',font=F(11),fill=(255,255,255,140),anchor='mt')
        for n,(x,y) in enumerate(((172,10),(632,8),(826,92),(940,240),(166,500),(584,516),(676,314)),1):
            d.ellipse((x-1,y-1,x+11,y+11),fill=(230,60,70));d.text((x+5,y+6),str(n),font=F(8,'Galmuri9'),fill=(255,255,255),anchor='mm')
    return h.resize((1920,1080),Image.NEAREST)
for name,n in(('hud_mock',0),('hud_mock_notes',1)):Image.alpha_composite(scr.convert('RGBA'),hud(n)).convert('RGB').save(f'{OUT}/{name}.png')
# ---------- region layout diagram ----------
W,H=960,540;im=Image.new('RGB',(W,H),(16,12,22));d=ImageDraw.Draw(im)
N={'town':(70,440,'마을 문'),'p1':(210,440,'전투 포켓'),'hub':(380,330,'비석 (거점)'),'p2':(250,200,'전투 포켓'),'p3':(520,190,'전투 포켓'),
   'cA':(130,90,'챔피언 A'),'cB':(700,90,'챔피언 B'),'door':(560,370,'보스 문 (봉인 2)'),'boss':(780,420,'보스 방'),'dive':(470,470,'잠수 지점 (나중)'),'p4':(640,280,'전투 포켓')}
def edge(a,b,col=(120,110,130),w=6,dash=False):
    (x0,y0,_),(x1,y1,_)=N[a],N[b]
    if not dash:d.line((x0,y0,x1,y1),fill=col,width=w);return
    L=math.hypot(x1-x0,y1-y0);k=int(L//14)
    for i in range(0,k,2):d.line((x0+(x1-x0)*i/k,y0+(y1-y0)*i/k,x0+(x1-x0)*(i+1)/k,y0+(y1-y0)*(i+1)/k),fill=col,width=w-2)
for a,b in(('town','p1'),('p1','hub'),('hub','p2'),('p2','cA'),('hub','p3'),('p3','p4'),('p4','cB'),('hub','door'),('door','boss')):edge(a,b)
edge('p4','door',(110,200,120),6,True);edge('p2','town',(110,200,120),6,True);edge('hub','dive',(110,160,230),5,True)
def node(k,r,col,txt=GOLD2):
    x,y,t=N[k];d.ellipse((x-r,y-r,x+r,y+r),fill=col,outline=OL,width=2);d.text((x,y+r+4),t,font=F(11),fill=txt,anchor='mt')
for k in('p1','p2','p3','p4'):node(k,22,(200,120,60))
node('town',14,(150,140,160));node('hub',16,(240,200,120));node('cA',26,(190,50,60));node('cB',26,(190,50,60))
node('door',16,(120,80,170));node('boss',30,(90,40,140));node('dive',10,(80,140,220),(150,190,240))
for dx in(-6,6):d.ellipse((560+dx-3,366,560+dx+3,372),fill=(255,90,90))
d.text((16,12),'한 지역 = 고리 + 가지 2개 + 보스 문',font=F(11),fill=(240,230,220))
for i,(c,t) in enumerate((((200,120,60),'전투 포켓: 한 화면 안, 가운데 비움, 출구 2개'),((190,50,60),'챔피언: 가지 끝, 순서 자유 → 보스 문 봉인 1개씩'),((110,200,120),'점선 초록: 지름길 (안쪽에서 열림)'),((80,140,220),'점선 파랑: 능력 얻고 다시 오는 길'))):
    d.rectangle((600,470+i*16,608,478+i*16),fill=c);d.text((614,468+i*16),t,font=F(8,'Galmuri9'),fill=(220,210,220))
im.resize((1920,1080),Image.NEAREST).save(f'{OUT}/region_layout.png')
