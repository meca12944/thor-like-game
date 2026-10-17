import os, sys, time
from PIL import Image, ImageDraw
A='/cursor/stores/store-795156a0-7465-4f60-aac0-5ea8cd38a231/grok-bot/agents/4fedc784-0420-4bf1-b51b-e98cbd24f667/attachments/'
n=int(sys.argv[1]); fs=sorted(os.listdir(A), key=lambda f: os.path.getmtime(A+f))[-n:]
out=Image.new('RGB',(256*min(n,5),170*((n+4)//5)),'black'); d=ImageDraw.Draw(out)
for i,f in enumerate(fs):
  x,y=(i%5)*256,(i//5)*170
  out.paste(Image.open(A+f).convert('RGB').resize((256,144)),(x,y)); d.text((x+4,y+150),f[:8],fill='white')
p=f'/workspace/town-demo/style_sample/work/thumb_{int(time.time())}.png'; out.save(p); print(p)
