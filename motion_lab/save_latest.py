# 모션연구방 저장 (사장님 10-23 "항상 저장하면 이전버전은 따로 모아두도록 하고 최신 버전만 저장해")
#  게임이 실제로 읽는 그림(주인공 /*H8*/ 아틀라스, 리네트 linette8.json)을 motion_lab/hero8, motion_lab/linette 에 최신본으로 뽑는다.
#  바뀐 동작이 있으면 그 전 최신본 전체를 motion_lab/old/<날짜_시각>_<캐릭터>/ 로 옮겨 모아 두고 새로 쓴다(바뀐 게 없으면 그대로).
#    python3 motion_lab/save_latest.py
import json,os,re,shutil,subprocess,time,hashlib
from PIL import Image,ImageDraw
R=os.path.dirname(os.path.abspath(__file__));G=os.path.join(R,'..','test128')
def hero():
    s=open(f'{G}/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');A=json.loads(s[j:e])
    return A,lambda k:not re.match(r'(hit|rec|hold)',k) and not k.endswith('_left')   # 칼 베기 몸동작은 안 씀, 왼쪽 = 오른쪽 뒤집기
def linette():
    return json.load(open(f'{G}/assets/anim/linette8.json')),lambda k:not k.startswith('atk')   # atk = 바늘 끝 데이터용
def export(name,A,keep):
    SH={};C={};F={}
    for k in sorted(A['anims']):
        if not keep(k):continue
        fr=[]
        for f in A['anims'][k]:
            if f[0] not in SH:SH[f[0]]=Image.open(f'{G}/assets/'+A['sheets'][f[0]]).convert('RGBA')
            x,y,w,h,ax,ay=A['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((x,y,x+w,y+h)),(128-ax,189-ay));fr.append(c)
        F[k]=fr;C[k]={'frames':len(fr),'ticks':[f[2] for f in A['anims'][k]]}
    D=f'{R}/{name}';sig=lambda fr:hashlib.md5(b''.join(im.tobytes() for im in fr)).hexdigest()
    old={}
    if os.path.exists(f'{D}/clips.json'):
        oc=json.load(open(f'{D}/clips.json'))
        for k in oc:
            p=f'{D}/frames/{k}'
            if os.path.isdir(p):old[k]=(sig([Image.open(f'{p}/{f}').convert('RGBA') for f in sorted(os.listdir(p))]),oc[k]['ticks'])
    changed=[k for k in F if old.get(k)!=(sig(F[k]),C[k]['ticks'])]+[k for k in old if k not in F]
    if not changed:print(name,'바뀐 것 없음');return
    if os.path.isdir(D):
        dst=f'{R}/old/{time.strftime("%Y-%m-%d_%H%M")}_{name}';os.makedirs(f'{R}/old',exist_ok=True);shutil.move(D,dst)
        open(f'{dst}/WHY.txt','w').write('이 다음 최신본에서 바뀐 동작: '+', '.join(changed)+'\n')
        print(name,'이전 최신본 ->',os.path.relpath(dst,R),'바뀐 동작',changed)
    os.makedirs(f'{D}/frames')
    for k,fr in F.items():
        os.makedirs(f'{D}/frames/{k}')
        for i,im in enumerate(fr):im.save(f'{D}/frames/{k}/{i:03d}.png')
    json.dump(C,open(f'{D}/clips.json','w'),ensure_ascii=False,indent=1)
    # sheet.png: 동작마다 첫 장 / preview.mp4: 모든 동작을 게임 속도로 (3초)
    ks=list(F);n=8;cw,ch=150,160;rows=(len(ks)+n-1)//n
    def grid(pick):
        W=Image.new('RGB',(cw*n,ch*rows),(70,110,60));d=ImageDraw.Draw(W)
        for q,k in enumerate(ks):
            im=pick(k);x,y=(q%n)*cw,(q//n)*ch;W.paste(im.crop((53,45,203,195)),(x,y),im.crop((53,45,203,195)));d.text((x+3,y+147),k,fill=(255,255,255))
        return W
    grid(lambda k:F[k][0]).save(f'{D}/sheet.png')
    tmp=f'{D}/_pv';os.makedirs(tmp)
    for t in range(0,180,2):
        def at(k):
            T=t%max(1,sum(C[k]['ticks']))
            for im,tk in zip(F[k],C[k]['ticks']):
                if T<tk:return im
                T-=tk
            return F[k][-1]
        grid(at).save(f'{tmp}/{t//2:03d}.png')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{tmp}/%03d.png','-pix_fmt','yuv420p','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2',f'{D}/preview.mp4']);shutil.rmtree(tmp)
    print(name,'최신본 저장',len(F),'동작')
if __name__=='__main__':
    export('hero8',*hero());export('linette',*linette())
