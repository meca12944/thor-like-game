from PIL import Image, ImageDraw
import os
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; V=f'{O}/v1_1x_descA'
dirs=['south','south-east','east','north-east','north','north-west','west','south-west']
ref=Image.open(f'{O}/inputs/ref_256_1x.png').convert('RGBA')
ims=[ref]+[Image.open(f'{V}/{d}.png').convert('RGBA') for d in dirs]
labels=['REFERENCE (south)']+dirs
S=2; cw=max(i.width for i in ims)*S; ch=max(i.height for i in ims)*S
sheet=Image.new('RGBA',(cw*len(ims)+10*(len(ims)+1), ch+40),(128,128,128,255)); dr=ImageDraw.Draw(sheet)
for k,(im,l) in enumerate(zip(ims,labels)):
    x=10+k*(cw+10); sheet.alpha_composite(im.resize((im.width*S,im.height*S),Image.NEAREST),(x,30))
    dr.text((x+4,8),l+f'  {im.width}x{im.height}',fill=(255,255,0) if k==0 else (255,255,255))
sheet.save(f'{O}/v3gen_first_sheet.png'); print(sheet.size)
# tight-crop preview for quick viewing
bb=None
