import sys
from PIL import Image, ImageDraw
ids=sys.argv[2:]; out=sys.argv[1]
EX=['neutral','smile','angry','sad','surprised','blush']
tw,th=256,320
S=Image.new('RGB',(tw*6,(th+20)*len(ids)),(40,44,52)); d=ImageDraw.Draw(S)
for r,c in enumerate(ids):
  for i,e in enumerate(EX):
    bg=Image.new('RGBA',(tw,th),(70,80,100,255) if (i%2) else (90,60,70,255))
    im=Image.open(f'/workspace/thor-like-game/docs_art/bust/{c}/{e}.png').resize((tw,th),Image.LANCZOS)
    bg.alpha_composite(im); S.paste(bg.convert('RGB'),(i*tw,r*(th+20)+20)); d.text((i*tw+4,r*(th+20)+4),f'{c}/{e}',fill='white')
S.save(out)
