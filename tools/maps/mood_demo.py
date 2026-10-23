import sys;sys.path.insert(0,'/home/user/thor-like-game/tools/maps')
import mood as M,harmonize as Hm
from PIL import Image,ImageDraw
S=sys.argv[1];base=Image.open(S+'/harm_after.png').convert('RGB');W,H=base.size
img=M.mute_ground(base).convert('RGB')
L=M.lightmap(img.size,[(420,330,330,(255,170,90),.9),(1120,330,330,(255,170,90),.9),(W//2,H//2,300,(120,170,255),.45),(700,520,420,(255,200,150),.55)])
img=M.apply_light(img,L).convert('RGBA')
sh=M.shafts(img.size);glow=Image.new('RGBA',img.size,(255,214,160,0));glow.putalpha(sh);img=Image.alpha_composite(img,glow)
ov=Image.new('RGBA',img.size);d=ImageDraw.Draw(ov)
for x,y,s in M.dust(img.size):d.rectangle((x,y,x+s-1,y+s-1),fill=(255,226,180,170))
for x,y in ((420,330),(1120,330)):d.rectangle((x-2,y-2,x+1,y+1),fill=(255,240,200,255))
img=Image.alpha_composite(img,ov);img=Image.alpha_composite(img,M.foreground(img))
img=Hm.grade(img.convert('RGB'),amount=.1,vignette=.35);img.save(S+'/mood_after.png')
c=(150,180,1400,896);a=base.crop(c);b=img.convert('RGB').crop(c);w,h=a.size
cmp=Image.new('RGB',(w,h*2+8),(10,8,14));cmp.paste(a,(0,0));cmp.paste(b,(0,h+8))
cmp.resize((int(w*.6),int((h*2+8)*.6)),Image.NEAREST).save(S+'/mood_compare.png')
