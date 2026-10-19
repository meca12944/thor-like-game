from PIL import Image, ImageDraw
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; V2=f'{O}/v2_2x_hires'; V1=f'{O}/v1_1x_descA'
dirs=['south','south-east','east','north-east','north','north-west','west','south-west']
ims=[Image.open(f'{V2}/{d}.png').convert('RGBA') for d in dirs]
for d,im in zip(dirs,ims):
    bb=im.split()[-1].getbbox(); print(d,im.size,bb,f'{bb[2]-bb[0]}x{bb[3]-bb[1]}')
cw=max(i.width for i in ims); ch=max(i.height for i in ims)
sheet=Image.new('RGBA',(cw*8+10*9,ch+40),(128,128,128,255)); dr=ImageDraw.Draw(sheet)
for k,(im,d) in enumerate(zip(ims,dirs)):
    x=10+k*(cw+10); sheet.alpha_composite(im,(x,30)); bb=im.split()[-1].getbbox()
    dr.text((x+4,8),f'{d}  bbox {bb[2]-bb[0]}x{bb[3]-bb[1]}',fill=(255,255,255))
sheet.save(f'{V2}/v2_hires_sheet.png'); print('sheet',sheet.size)
# v1 vs v2: tight crops, scaled (nearest) to same displayed height
H=496; tiles=[]
for tag,V in (('v1',V1),('v2',V2)):
    for d in ('south','south-west'):
        im=Image.open(f'{V}/{d}.png').convert('RGBA'); bb=im.split()[-1].getbbox(); c=im.crop(bb)
        s=H/c.height; tiles.append((f'{tag} {d} ({c.width}x{c.height}) x{s:.2f}',c.resize((round(c.width*s),H),Image.NEAREST)))
W=sum(t.width for _,t in tiles)+20*(len(tiles)+1)
cmp=Image.new('RGBA',(W,H+50),(128,128,128,255)); dr=ImageDraw.Draw(cmp); x=20
for l,t in tiles:
    cmp.alpha_composite(t,(x,40)); dr.text((x,12),l,fill=(255,255,0) if l.startswith('v2') else (255,255,255)); x+=t.width+20
cmp.save(f'{V2}/v2_vs_v1.png'); print('cmp',cmp.size)
