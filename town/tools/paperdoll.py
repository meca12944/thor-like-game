# -*- coding: utf-8 -*-
# 필멸자 페이퍼돌: 기본 몸(검은 머리) → 방어구 → 투구 → 무기 → 보조무기 레이어를 프레임마다 생성하고 합성한다.
# 방식: 회색/원본 램프를 아이템 palette(4색)로 치환하는 팔레트 스왑 + 투구·방패·오브는 머리/손 위치 기준 코드 드로잉.
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(os.path.abspath(__file__)); A=os.path.join(HERE,'..','assets'); OH=os.path.join(A,'..','assets_orig_hair')
sys.path.insert(0,'/workspace/thor-like-game/tools/design')
from towns_data import EQUIP_ITEMS, PALETTES
EQ={e['id']:e for e in EQUIP_ITEMS}
S=json.load(open(os.path.join(A,'sprites.json')))
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SETS=[ # 데모 G 키 순서 (0 = 기본 튜닉)
 dict(id='g1',name='초급 · 시작 마을',items=['w_iron_trainee','b_quilted','h_leather_hood','a_wood_round']),
 dict(id='g2',name='중급 · 바다',items=['w_wave_blade','b_scale_mail','h_nautilus','a_coral_buckler']),
 dict(id='g3',name='후반 · 미스릴',items=['w_mithril','b_mithril_plate','h_knight_plume','a_royal_kite']),
 dict(id='g4',name='최종 · 마룡',items=['w_dragon_tri','b_dragon_scale','h_void_crown','o_dragon_eye']),
]
HERO_KEYS=['hero_walk_down','hero_walk_up','hero_walk_right','hero_atk_r1','hero_atk_up','hero_atk_right','cb_slash','cb_thrust','cb_spin']
FACING={'hero_walk_down':'down','hero_walk_up':'up','hero_atk_up':'up'}   # 나머지는 옆모습(오른쪽)
def hx(c): return np.array([int(c[i:i+2],16) for i in (1,3,5)])
def hsv(a):
    rgb=a[...,:3]/255.0; mx=rgb.max(-1); mn=rgb.min(-1); d=np.maximum(mx-mn,1e-6); r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60; s=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0); return h,s,mx
def ramp(a,mask,pal,lo=0.10,hi=0.75):
    """밝기를 4단 팔레트로 치환 (팔레트 스왑 그룹)."""
    rgb=a[...,:3].astype(float); lum=(0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2])/255
    t=np.clip((lum-lo)/(hi-lo),0,0.999); idx=(t*4).astype(int); P=np.stack([hx(c) for c in pal])
    out=np.zeros_like(a); out[...,:3]=P[idx]; out[...,3]=np.where(mask,a[...,3],0); return out
def frames(key):
    sp=S[key]; base=np.array(Image.open(os.path.join(A,sp['src'])).convert('RGBA')); orig=np.array(Image.open(os.path.join(OH,sp['src'])).convert('RGBA'))
    for i in range(sp['n']):
        x0=i*sp['w']; yield i,base[:,x0:x0+sp['w']].copy(),orig[:,x0:x0+sp['w']].copy()
def bodyh(sp,i): return sp['bodyH'][i] if 'bodyH' in sp and i<len(sp['bodyH']) else min(165,sp['ay']*0.98)
def layers(key,i,base,orig,items):
    sp=S[key]; H,W=base.shape[:2]; ax,ay=sp['ax'],sp['ay']; bH=bodyh(sp,i); face=FACING.get(key,'side')
    h,s,v=hsv(base); op=base[...,3]>0
    hair=(np.abs(base[...,:3].astype(int)-orig[...,:3].astype(int)).sum(-1)>0)&op
    L={}
    # 방어구: 파란 튜닉 픽셀 = 몸 레이어의 옷 부분
    e=EQ[items[1]]; tun=op&(h>=190)&(h<=250)&(s>0.30)&(v>0.12)
    L['armor']=ramp(base,tun,PALETTES[e['visual']['palette']],0.06,0.55)
    # 투구: 머리카락 자리를 투구 팔레트로 덮고, 종류별 장식
    e=EQ[items[2]]; pal=PALETTES[e['visual']['palette']]; spr=e['visual']['sprite']
    hl=np.zeros_like(base); ys,xs=np.where(hair)
    if len(ys):
        hm=hair.copy()
        img=Image.fromarray(np.zeros_like(base)); d=ImageDraw.Draw(img)
        top,bot,l,r=ys.min(),ys.max(),xs.min(),xs.max(); cx=(l+r)/2
        if spr in('head_hood','head_turban'):   # 천: 머리 전체 + 아래로 1~2px 늘어짐
            from scipy import ndimage
            hm=ndimage.binary_dilation(hair,iterations=2)&(np.arange(H)[:,None]<=bot+1)
        from scipy import ndimage
        if spr not in('head_hood','head_turban'):   # 금속·껍데기: 곱슬 실루엣을 둥근 돔으로 다듬음
            hm=ndimage.binary_closing(hm,iterations=3); hm=ndimage.binary_fill_holes(hm); hm=ndimage.binary_opening(hm,iterations=1)
            hm&=ndimage.binary_dilation(hair,iterations=2)
        yy=(np.arange(H)[:,None]-top)/max(1,bot-top); xx=np.abs(np.arange(W)[None,:]-cx)/max(1,(r-l)/2)
        rgb=base[...,:3].astype(float); lum=(0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2])/255
        shade=np.clip(0.95-0.75*yy-0.35*xx**2+0.25*(lum-0.15),0,0.999)   # 위쪽·가운데가 밝은 돔 음영
        if spr in('head_hood','head_turban'): shade=np.clip(0.75-0.5*yy+0.6*(lum-0.12),0,0.999)
        P=np.stack([hx(c) for c in pal]); idx=(shade*4).astype(int)
        hl=np.zeros_like(base); hl[...,:3]=P[idx]; hl[...,3]=np.where(hm,255,0)
        edge=hm&~ndimage.binary_erosion(hm); hl[edge,:3]=np.minimum(P[0],40)   # 외곽선
        img=Image.fromarray(hl); d=ImageDraw.Draw(img)
        P=[tuple(hx(c))+(255,) for c in pal]
        if spr=='head_helm_visor':
            if face!='up': d.rectangle([l+2,bot-2,r-2,bot],fill=(20,20,28,255))   # 바이저 틈
            d.line([(cx,top),(cx-6,top-12),(cx-14,top-18)],fill=P[2],width=4); d.line([(cx,top),(cx-8,top-10)],fill=P[3],width=2)  # 깃털
        if spr=='head_crown':
            for k in range(5):
                px=l+(r-l)*(k+0.5)/5; d.polygon([(px-4,top+3),(px+4,top+3),(px,top-9-(4 if k==2 else 0))],fill=P[2],outline=P[0])
            d.ellipse([cx-2,top-2,cx+2,top+2],fill=P[3])
        if spr=='head_shell':
            for k in range(3): d.polygon([(l+6+k*(r-l-12)/2-3,top+2),(l+6+k*(r-l-12)/2+3,top+2),(l+6+k*(r-l-12)/2,top-7)],fill=P[3],outline=P[0])
        if spr=='head_turban':
            d.ellipse([cx-3,top+3,cx+3,top+9],fill=P[3],outline=P[0])
        hl=np.array(img)
    L['helmet']=hl
    # 무기: 검날(채도 낮고 밝은 픽셀, 머리 영역 밖) → 무기 팔레트
    e=EQ[items[0]]; pal=PALETTES[e['visual']['palette']]
    headwin=np.zeros((H,W),bool)
    if len(ys): headwin[max(0,ys.min()-4):ys.max()+int(bH*0.12),max(0,xs.min()-6):xs.max()+6]=True
    blade=op&(s<0.20)&(v>0.50)&~headwin
    L['weapon']=ramp(base,blade,pal,0.45,1.0)
    # 보조무기: 방패(원형/연·대형) 또는 오브
    e=EQ[items[3]]; pal=PALETTES[e['visual']['palette']]; spr=e['visual']['sprite']; P=[tuple(hx(c))+(255,) for c in pal]
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img); behind=False; R=bH*0.115
    if face=='down': cx,cy=ax+bH*0.22,ay-bH*0.44
    elif face=='up': cx,cy=ax-bH*0.22,ay-bH*0.44
    else: cx,cy=ax+bH*0.06,ay-bH*0.47; behind=True
    if spr=='off_orb':
        ox,oy=ax-bH*0.24,ay-bH*0.84
        for rr,al in [(R*1.25,60),(R*0.95,110)]: d.ellipse([ox-rr,oy-rr,ox+rr,oy+rr],fill=P[3][:3]+(al,))
        d.ellipse([ox-R*0.7,oy-R*0.7,ox+R*0.7,oy+R*0.7],fill=P[2],outline=P[0],width=2); d.ellipse([ox-R*0.3,oy-R*0.45,ox,oy-R*0.15],fill=P[3]); behind=False
    elif spr=='off_shield_kite':
        pts=[(cx-R,cy-R*1.1),(cx+R,cy-R*1.1),(cx+R*0.9,cy+R*0.2),(cx,cy+R*1.5),(cx-R*0.9,cy+R*0.2)]
        d.polygon(pts,fill=P[1],outline=(15,15,20,255)); d.polygon([(x*0.8+cx*0.2,y*0.8+cy*0.2) for x,y in pts],fill=P[2])
        d.rectangle([cx-2,cy-R*0.8,cx+2,cy+R*1.0],fill=P[3]); d.rectangle([cx-R*0.6,cy-R*0.3,cx+R*0.6,cy-R*0.3+4],fill=P[3])
    else:  # 원형 방패·버클러
        d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=P[1],outline=(15,15,20,255),width=2); d.ellipse([cx-R*0.78,cy-R*0.78,cx+R*0.78,cy+R*0.78],fill=P[2])
        d.ellipse([cx-R*0.25,cy-R*0.25,cx+R*0.25,cy+R*0.25],fill=P[3],outline=P[0]); d.arc([cx-R*0.7,cy-R*0.7,cx+R*0.7,cy+R*0.7],200,260,fill=P[3],width=2)
    L['offhand']=np.array(img); L['_behind']=behind
    body=base.copy(); L['body']=body
    return L
def over(dst,src):
    a=src[...,3:4]/255.0; dst[...,:3]=(src[...,:3]*a+dst[...,:3]*(1-a)).astype(np.uint8); dst[...,3]=np.maximum(dst[...,3],src[...,3]); return dst
def compose(L):
    out=np.zeros_like(L['body'])
    if L['_behind']: out=over(out,L['offhand'])
    out=over(out,L['body']); out=over(out,L['armor']); out=over(out,L['helmet']); out=over(out,L['weapon'])
    if not L['_behind']: out=over(out,L['offhand'])
    return out
def build_game_sheets():
    for st in SETS:
        for key in HERO_KEYS:
            sp=S[key]; cols=[]
            for i,b,o in frames(key): cols.append(compose(layers(key,i,b,o,st['items'])))
            Image.fromarray(np.concatenate(cols,1)).save(os.path.join(A,'gear',f"{key}@{st['id']}.png"))
def cell(img,ax,ay,CW=230,CH=200,flip=False,bg=(255,0,255,255)):
    c=Image.new('RGBA',(CW,CH),bg); im=Image.fromarray(img)
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT); ax=im.width-ax
    c.alpha_composite(im,(int(CW/2-ax),int(CH-8-ay))); return c
ROWS=[('아래','hero_walk_down',[0,1],'hero_atk_r1',False),('위','hero_walk_up',[0,1],'hero_atk_up',False),('오른쪽','hero_walk_right',[0,1],'hero_atk_right',False),('왼쪽','hero_walk_right',[0,1],'hero_atk_right',True)]
def sheet(items,title,out,mode='compose',labels=True):
    CW,CH=230,200; cols=5; W=CW*cols+90; Hh=CH*4+70
    c=Image.new('RGBA',(W,Hh),(255,0,255,255)); d=ImageDraw.Draw(c); f=ImageFont.truetype(FONT,22); fs=ImageFont.truetype(FONT,16)
    for r,(nm,wk,wf,ak,fl) in enumerate(ROWS):
        fr=dict((i,(b,o)) for i,b,o in frames(wk)); fa=dict((i,(b,o)) for i,b,o in frames(ak))
        seq=[(wk,j,fr[j]) for j in wf]+[(ak,j,fa[j]) for j in range(3)]
        for k,(key,j,(b,o)) in enumerate(seq):
            L=layers(key,j,b,o,items) if items else None
            img=compose(L) if items else b
            c.alpha_composite(cell(img,S[key]['ax'],S[key]['ay'],CW,CH,fl),(90+k*CW,60+r*CH))
        if labels: d.text((45,60+r*CH+CH/2),nm,font=f,fill='white',anchor='mm',stroke_width=3,stroke_fill=(40,0,30))
    if labels:
        d.text((W/2,28),title,font=f,fill='white',anchor='mm',stroke_width=3,stroke_fill=(40,0,30))
        for k,t in enumerate(['대기','걷기','공격 1','공격 2','공격 3']): d.text((90+k*CW+CW/2,52),t,font=fs,fill='white',anchor='mm',stroke_width=2,stroke_fill=(40,0,30))
    c.convert('RGB').save(out,quality=93)
def layer_sheet(st,out):
    """한 세트의 레이어 분해: 몸 / 방어구 / 투구 / 무기 / 보조무기 / 합성 (4방향 대기)."""
    CW,CH=200,190; names=['기본 몸 (검은 머리)','방어구','투구','무기','보조무기','합성']
    W=CW*6+90; Hh=CH*4+80; c=Image.new('RGBA',(W,Hh),(255,0,255,255)); d=ImageDraw.Draw(c); f=ImageFont.truetype(FONT,18)
    for r,(nm,wk,_,_,fl) in enumerate(ROWS):
        i,b,o=next(frames(wk)); L=layers(wk,0,b,o,st['items'])
        for k,img in enumerate([L['body'],L['armor'],L['helmet'],L['weapon'],L['offhand'],compose(L)]):
            c.alpha_composite(cell(img,S[wk]['ax'],S[wk]['ay'],CW,CH,fl),(90+k*CW,70+r*CH))
        d.text((45,70+r*CH+CH/2),nm,font=f,fill='white',anchor='mm',stroke_width=3,stroke_fill=(40,0,30))
    for k,t in enumerate(names): d.text((90+k*CW+CW/2,55),t,font=f,fill='white',anchor='mm',stroke_width=3,stroke_fill=(40,0,30))
    ttl=f"{st['name']} — "+' / '.join(EQ[i]['name'] for i in st['items'])
    d.text((W/2,22),ttl,font=f,fill='white',anchor='mm',stroke_width=3,stroke_fill=(40,0,30)); c.convert('RGB').save(out,quality=93)
def variety(out):
    """무기 팔레트 16종 + 보조무기 8종 (오른쪽 대기 프레임)."""
    weps=['w_iron_trainee','w_bronze_long','w_crystal_edge','w_desert_crescent','w_sun_sigil','w_wave_blade','w_obsidian','w_forge_great','w_frost_crystal','w_mithril','w_royal_knight','w_kraken_whip','w_hellfire','w_storm_spear','w_shadow_twin','w_dragon_tri']
    offs=['a_wood_round','o_moss_shield','a_coral_buckler','o_crab_claw','o_shark_fin','a_royal_kite','o_shell_orb','o_ember_orb','o_holy_orb','o_dragon_eye']
    CW,CH=210,200; cols=8; W=CW*cols; rows=2+((len(offs)+cols-1)//cols); Hh=CH*rows+60
    c=Image.new('RGBA',(W,Hh),(255,0,255,255)); d=ImageDraw.Draw(c); f=ImageFont.truetype(FONT,15); ft=ImageFont.truetype(FONT,22)
    key='hero_atk_r1'; frs=list(frames(key)); i,b,o=frs[1]
    for k,w in enumerate(weps):
        L=layers(key,1,b,o,[w,'b_cloth_tunic','h_leather_hood','a_wood_round']); L['helmet'][:]=0; L['armor'][:]=0; L['offhand'][:]=0
        x,y=(k%cols)*CW,50+(k//cols)*CH; c.alpha_composite(cell(compose(L),S[key]['ax'],S[key]['ay'],CW,CH),(x,y))
        d.text((x+CW/2,y+CH-14),EQ[w]['name'],font=f,fill='white',anchor='mm',stroke_width=2,stroke_fill=(40,0,30))
    key='hero_walk_down'; i,b,o=next(frames(key))
    for k,w in enumerate(offs):
        L=layers(key,0,b,o,['w_iron_trainee','b_cloth_tunic','h_leather_hood',w]); L['helmet'][:]=0; L['armor'][:]=0; L['weapon'][:]=0
        x,y=(k%cols)*CW,50+(2+k//cols)*CH; c.alpha_composite(cell(compose(L),S[key]['ax'],S[key]['ay'],CW,CH),(x,y))
        d.text((x+CW/2,y+CH-14),EQ[w]['name'],font=f,fill='white',anchor='mm',stroke_width=2,stroke_fill=(40,0,30))
    d.text((W/2,24),'무기 · 보조무기 팔레트 스왑 견본 (필멸자, 검은 머리)',font=ft,fill='white',anchor='mm',stroke_width=3,stroke_fill=(40,0,30))
    c.convert('RGB').save(out,quality=93)
if __name__=='__main__':
    outs=sys.argv[1:] or ['/workspace/town-demo/src/hero/paperdoll']
    build_game_sheets()
    for od in outs:
        os.makedirs(od,exist_ok=True)
        sheet(None,'필멸자 기본 몸 레이어 (검은 머리 · 기본 튜닉)',os.path.join(od,'hero_base_body.jpg'))
        for st in SETS:
            sheet(st['items'],f"{st['name']} — "+' / '.join(EQ[i]['name'] for i in st['items']),os.path.join(od,f"hero_gear_{st['id']}.jpg"))
            layer_sheet(st,os.path.join(od,f"hero_layers_{st['id']}.jpg"))
        variety(os.path.join(od,'hero_weapon_offhand_variety.jpg'))
    print('ok')
