#!/usr/bin/env python3
"""각 방의 배치 가이드 그림 생성 (그림 생성/채색 시 참고용, 충돌 위치와 맞추기 위함).
assets_src/guides/<room>_layout.png  : 기본 타일 그래픽 (1280x960)
assets_src/guides/<room>_collision.png: 충돌 도식 (벽=회색, 물=파랑, 구멍=검정, 나무=초록, 바닥=베이지)
필요: pip install playwright && playwright install chromium"""
import os, base64
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'assets_src','guides');os.makedirs(OUT,exist_ok=True)
COL={'#':(90,90,96),'S':(90,90,96),'Q':(90,90,96),'K':(120,100,96),'D':(150,90,40),'H':(170,60,50),'n':(150,110,70),'~':(40,110,220),'_':(10,10,10),'v':(30,60,20),
     'T':(30,130,40),'o':(130,130,130),'C':(230,180,40),'B':(160,120,80),'L':(255,140,0),'t':(160,100,40),'A':(80,200,255),'F':(255,80,0),'>':(250,250,250),'=':(140,100,60),'f':(240,120,200)}
with sync_playwright() as pw:
    b=pw.chromium.launch();p=b.new_page(viewport={'width':960,'height':720})
    p.goto('file://'+os.path.join(ROOT,'index.html')+'?noassets');p.wait_for_timeout(500);p.keyboard.press('KeyZ');p.wait_for_timeout(300)
    D='window.__dbg';p.evaluate(D+'.skipDlg()')
    for r in p.evaluate(D+'.rooms()'):
        p.evaluate(f"{D}.warp('{r}',1,1)");p.wait_for_timeout(50);p.evaluate(D+'.skipDlg()')
        url=p.evaluate(D+'.layout()');im=Image.open(__import__('io').BytesIO(base64.b64decode(url.split(',')[1]))).resize((1280,960),Image.NEAREST);im.save(f'{OUT}/{r}_layout.png')
        g=p.evaluate(D+'.grid()');c=Image.new('RGB',(1280,960),(225,210,170));d=ImageDraw.Draw(c)
        for y,row in enumerate(g):
            for x,ch in enumerate(row):
                if ch in COL:d.rectangle([x*64,y*64,x*64+63,y*64+63],fill=COL[ch])
        for i in range(21):d.line([i*64,0,i*64,960],fill=(0,0,0),width=1)
        for i in range(16):d.line([0,i*64,1280,i*64],fill=(0,0,0),width=1)
        c.save(f'{OUT}/{r}_collision.png');print(r)
    b.close()
