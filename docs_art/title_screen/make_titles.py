from PIL import Image, ImageDraw, ImageFont, ImageFilter
G='/usr/share/fonts/truetype/sand-box/google/'
EN=G+'Cormorant SC/CormorantSC-Bold.ttf'
KO=G+'Nanum Myeongjo/NanumMyeongjo-Bold.ttf'
KOR=G+'Nanum Myeongjo/NanumMyeongjo-Regular.ttf'
SUB='\uC0AC\uBA78\uC758 \uADA4\uC801'  # 사멸의 궤적
assert SUB=='사멸의 궤적' and ord(SUB[4])==0xADA4
MENU=['새 게임','이어하기','설정']
W,H=1920,1080
TXT=(240,228,200); DIM=(200,186,158); ACC=(176,64,52)

def tw(d,s,f,sp=0):
    return sum(d.textlength(c,font=f) for c in s)+sp*(len(s)-1)
def draw_spaced(d,xy,s,f,fill,sp):
    x,y=xy
    for c in s:
        d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp

def layer_text(size, items):
    # items: (x,y,text,font,fill,spacing)
    txt=Image.new('RGBA',size,(0,0,0,0)); sh=Image.new('RGBA',size,(0,0,0,0))
    dt=ImageDraw.Draw(txt); ds=ImageDraw.Draw(sh)
    for x,y,s,f,fill,sp in items:
        draw_spaced(ds,(x+3,y+4),s,f,(15,8,4,210),sp)
        draw_spaced(dt,(x,y),s,f,fill,sp)
    return txt, sh.filter(ImageFilter.GaussianBlur(6))

def make(name, cx, ty, align, menu_cx, menu_align):
    bg=Image.open(f'bg_{name}.png').convert('RGBA')
    ovl=build_overlay(cx, ty, align, menu_cx, menu_align)
    ovl.save(f'title_{name}_overlay.png')
    Image.alpha_composite(bg,ovl).convert('RGB').save(f'title_{name}.png')

def build_overlay(cx, ty, align, menu_cx, menu_align):
    # transparent RGBA layer: logo + menu + legibility shading; composite over bg (still or video)
    bg=Image.new('RGBA',(W,H),(0,0,0,0))
    # bottom gradient for menu legibility + soft vignette behind logo
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for y in range(int(H*0.72)+1,H):
        a=int(170*((y-H*0.72)/(H*0.28))**1.4); od.line([(0,y),(W,y)],fill=(18,10,6,a))
    glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([cx-560,ty-120,cx+560,ty+300],fill=(20,12,8,95))
    glow=glow.filter(ImageFilter.GaussianBlur(90))
    bg=Image.alpha_composite(Image.alpha_composite(bg,glow),ov)
    d=ImageDraw.Draw(bg)
    fen1=ImageFont.truetype(EN,58); fen2=ImageFont.truetype(EN,128)
    fko=ImageFont.truetype(KO,64); fm=ImageFont.truetype(KOR,40); fmb=ImageFont.truetype(KO,40)
    l1='Trail of'; l2='Extinction'
    w1=tw(d,l1,fen1,10); w2=tw(d,l2,fen2,6); wk=tw(d,SUB,fko,22)
    def X(w): return cx-w/2 if align=='c' else cx
    items=[(X(w1),ty,l1,fen1,TXT,10),(X(w2),ty+52,l2,fen2,TXT,6)]
    ly=ty+52+150
    items.append((X(wk),ly+34,SUB,fko,TXT,22))
    # menu
    my=H-118; mi=[]
    if menu_align=='row':
        gap=90; ws=[tw(d,m,fm,6) for m in MENU]; tot=sum(ws)+gap*2; x=menu_cx-tot/2
        pos=[]
        for m,w in zip(MENU,ws): pos.append((x,my,m,w)); x+=w+gap
    else:
        pos=[(menu_cx,H-260+i*62,m,tw(d,m,fm,6)) for i,m in enumerate(MENU)]
    for i,(x,y,m,w) in enumerate(pos):
        mi.append((x,y,m,fmb if i==0 else fm,TXT if i==0 else DIM,6))
    t,s=layer_text((W,H),items+mi)
    bg=Image.alpha_composite(Image.alpha_composite(bg,s),t)
    d=ImageDraw.Draw(bg)
    # rule line under English title, with small crimson diamond (core motif)
    rw=max(w2,wk)+40; rx=X(w2)-20 if align=='c' else cx; 
    if align=='c': rx=cx-rw/2
    d.line([(rx,ly+10),(rx+rw,ly+10)],fill=(220,205,175,255),width=2)
    mx=rx+rw/2; d.polygon([(mx,ly+1),(mx+9,ly+10),(mx,ly+19),(mx-9,ly+10)],fill=ACC,outline=(230,210,170))
    # selection marker before first menu item
    x,y,m,w=pos[0]; d.polygon([(x-30,y+22),(x-21,y+13),(x-12,y+22),(x-21,y+31)],fill=ACC)
    return bg

make('a',1230,90,'c',W/2,'row')
make('b',90,110,'l',110,'col')
make('c',W/2,60,'c',1360,'row')

ims=[Image.open(f'title_{n}.png').resize((960,540),Image.LANCZOS) for n in 'abc']
sheet=Image.new('RGB',(960*3+40*4,540+120),(24,18,14)); sd=ImageDraw.Draw(sheet)
lf=ImageFont.truetype(KO,30)
for i,(im,lab) in enumerate(zip(ims,['A  절벽 위 뒷모습 · 폐허 왕도','B  검을 내린 주인공 · 핵 문장 · 재','C  고성으로 향하는 외길'])):
    x=40+i*1000; sheet.paste(im,(x,80)); sd.text((x,28),lab,font=lf,fill=TXT)
sheet.save('title_v2_sheet.png')
