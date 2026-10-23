# Motion check board: every motion x direction of a character atlas (hero8 format) looping in a numbered grid, missing
# directions shown as grey "없음" cells, so the owner can answer "3번 이상해". Renders mp4 pages (portrait, phone-friendly).
# usage: board.py <test128 dir> <out dir>
import sys,os,json,subprocess
from PIL import Image,ImageDraw,ImageFont
G,O=sys.argv[1:3];os.makedirs(O,exist_ok=True)
F=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',n)
def hero_atlas():
    s=open(f'{G}/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);return json.JSONDecoder().raw_decode(s[j:])[0]
KO={'idle':'서 있기','walk':'걷기','run':'달리기','dash':'대시','jump':'점프','rjump':'달리며 점프','hit1':'베기 1','hit2':'베기 2','hit3':'베기 3','atk1':'찌르기 1','atk2':'찌르기 2','atk3':'찌르기 3',
    'hurt':'맞기','hurtys':'맞기(크게)','death':'죽기','hold':'힘 모으기','rec1':'베기1 뒤 멈춤','rec2':'베기2 뒤 멈춤','cast':'스킬','cast_s1':'스킬 1','cast_s2':'스킬 2','cast_s3':'스킬 3'}
AR={'down':'↓ 앞','up':'↑ 뒤','right':'→ 오른쪽','left':'← 왼쪽','downl':'↙ 왼앞','upl':'↖ 왼뒤'}
def page(A,sheets,motions,dirs,title,out,start,CW=170,CH=200,LW=150,ar=AR):
    IM=[Image.open(f'{G}/assets/{p}').convert('RGBA') for p in sheets];cells=A['cells']
    W,H=LW+CW*len(dirs),70+CH*len(motions)+40;n=start;grid=[]
    for r,mo in enumerate(motions):
        for c,d in enumerate(dirs):
            L=A['anims'].get(f'{mo}_{d}');grid.append((r,c,mo,d,L,n if L else None));n+=1 if L else 0
    T=max(sum(f[2] for f in g[4]) for g in grid if g[4]);T=max(T,120);frames=[]
    sc=min(1.0,(CH-40)/130)
    def blit(img,sh,ci,x,y):
        cx,cy,w,h,ax,ay=cells[sh][ci];cr=IM[sh].crop((cx,cy,cx+w,cy+h));cr=cr.resize((max(1,round(w*sc)),max(1,round(h*sc))),Image.LANCZOS);img.alpha_composite(cr,(round(x-ax*sc),round(y-ay*sc)))
    for t in range(0,T*2,2):
        img=Image.new('RGBA',(W,H),(30,32,40,255));d=ImageDraw.Draw(img);d.text((14,14),title,font=F(26),fill=(255,214,140));d.text((14,46),'번호를 보고 "3번 이상해" 처럼 말해 주세요 · 회색 = 그 방향 그림 없음',font=F(15),fill=(170,170,180))
        for c,dd in enumerate(dirs):d.text((LW+c*CW+8,H-34),ar.get(dd,dd),font=F(16),fill=(200,200,210))
        for r,c,mo,dd,L,num in grid:
            x0,y0=LW+c*CW,70+r*CH
            if c==0:d.text((10,y0+CH//2-12),KO.get(mo,mo),font=F(19),fill=(235,225,210))
            if not L:d.rectangle((x0+4,y0+4,x0+CW-4,y0+CH-4),fill=(52,52,58));d.text((x0+CW//2-18,y0+CH//2-10),'없음',font=F(18),fill=(120,120,128));continue
            d.rectangle((x0+4,y0+4,x0+CW-4,y0+CH-4),fill=(44,58,40))
            tot=sum(f[2] for f in L);q=t%tot;i=0
            while q>=L[i][2]:q-=L[i][2];i+=1
            f=L[i];fx,fy=x0+CW//2,y0+CH-24
            if len(f)>=5 and f[3] is not None and f[3]>=0:blit(img,f[3],f[4],fx,fy)
            blit(img,f[0],f[1],fx,fy)
            if len(f)>=7 and f[5] is not None and f[5]>=0:blit(img,f[5],f[6],fx,fy)
            d.ellipse((x0+8,y0+8,x0+38,y0+38),fill=(255,214,120));d.text((x0+23-len(str(num))*5,y0+13),str(num),font=F(17),fill=(30,24,10))
        frames.append(img.convert('RGB'))
    tmp=out+'_f';os.makedirs(tmp,exist_ok=True)
    for k,im in enumerate(frames):im.save(f'{tmp}/{k:04d}.png')
    subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','30','-i',f'{tmp}/%04d.png','-vf','loop=2:size=%d,pad=ceil(iw/2)*2:ceil(ih/2)*2'%len(frames),'-c:v','libx264','-pix_fmt','yuv420p','-crf','20',out+'.mp4'],check=True)
    return n
H=hero_atlas();HD=['down','up','right','left']
n=page(H,H['sheets'],['idle','walk','run','dash','jump','rjump','hold','rec1','rec2'],HD,'주인공 모션 점검표 1 — 움직이기',f'{O}/hero_move',1)
n=page(H,H['sheets'],['hit1','hit2','hit3','hurt','hurtys','death','cast_s1','cast_s2','cast_s3'],HD,'주인공 모션 점검표 2 — 싸우기',f'{O}/hero_fight',n)
L=json.load(open(f'{G}/assets/anim/linette8.json'));LD=['down','downl','up','upl','right','left']
page(L,L['sheets'],['idle','walk','run','dash','jump','rjump','atk1','atk2','atk3','cast','hurt','death'],LD,'리네트 모션 점검표',f'{O}/linette',1,CW=150,CH=190,ar={'down':'↘ 오른앞','downl':'↙ 왼앞','up':'↗ 오른뒤','upl':'↖ 왼뒤','right':'→ 오른쪽','left':'← 왼쪽'})  # Linette has no straight front/back: down/up are diagonals
print('ok')
