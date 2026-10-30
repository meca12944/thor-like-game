# 그록 이매진에 넣을 그림: 서기 그림(원본 키, 예 218)을 정수 3배(NEAREST)로 키워 1024×1024 초록(#00FF00) 바탕에 (가로 가운데, 머리끝 225)
# 쓰는 법: python3 grokin.py <서기 그림 png> <출력 png> [배수=3]
import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
im = Image.open(src).convert('RGBA'); bb = im.getbbox(); c = im.crop(bb)
c = c.resize((c.width * k, c.height * k), Image.NEAREST)
g = Image.new('RGB', (1024, 1024), (0, 255, 0)); g.paste(c, ((1024 - c.width) // 2, 225), c); g.save(out)
print('크기', c.size, '자리', ((1024 - c.width) // 2, 225), '→', out)
