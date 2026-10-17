import sys
from PIL import Image,ImageDraw
fs=sys.argv[2:];c=Image.new('RGB',(960,135*((len(fs)+1)//2)),'white')
for i,f in enumerate(fs):
  im=Image.open(f).convert('RGB').resize((480,135),box=(0,140,1280,580) if Image.open(f).size==(1280,720) else None);ImageDraw.Draw(im).text((4,4),f.split('/')[-1],fill='white');c.paste(im,((i%2)*480,(i//2)*135))
c.save(sys.argv[1])
