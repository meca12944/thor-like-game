# 그록 대표 그림에서 마을 색 목록 뽑기 (하늘 빼고) → palette_32.png (PixelLab color_image용), palette.json
# 바탕 24색(넓은 면적) + 강조 8색(물빛·차양·불빛·이끼처럼 채도 높은 작은 면적)
from PIL import Image
import json, colorsys
im = Image.open('grok_felt_keyart.png').convert('RGB')
body = im.crop((0, 150, im.width, im.height))          # 하늘 빼기

def quant(img, n):
    q = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT, kmeans=4)
    pal = q.getpalette()
    return [tuple(pal[i*3:i*3+3]) for _, i in q.getcolors()]

base = quant(body, 24)
# 그록 그림은 거의 세피아(채도 0.2 넘는 점의 99.8%가 갈색)라 강조색은 그림 속 작은 점들(분수 물, 차양, 보라 옷)에서
# 고른 색을 조금 더 또렷하게 올려 직접 정한다. 불빛은 코드 조명이 덧칠하므로 2색만.
ACC = ['#2f4a52', '#4f7f86', '#3a4f6b', '#7a3a2c', '#5a3550', '#4d5a2c', '#e08a3a', '#ffd08a']
acc = [tuple(int(h[i:i+2], 16) for i in (1, 3, 5)) for h in ACC]
key = lambda c: colorsys.rgb_to_hls(*[x/255 for x in c])[1]
cols = sorted(base, key=key) + acc
hexs = ['#%02x%02x%02x' % c for c in cols]
json.dump({'src': 'grok_felt_keyart.png (하늘 제외)', 'base24': hexs[:24], 'accent8': hexs[24:]},
          open('palette.json', 'w'), indent=1, ensure_ascii=False)
sw = Image.new('RGB', (len(cols) * 8, 8))
for i, c in enumerate(cols): sw.paste(c, (i * 8, 0, i * 8 + 8, 8))
sw.save('palette_32.png')
sw.resize((len(cols) * 40, 80), Image.NEAREST).save('palette_view.png')
pimg = Image.new('P', (1, 1)); pimg.putpalette(sum(cols, ()) + (0,) * (768 - 3 * len(cols)))
body.quantize(palette=pimg, dither=Image.Dither.NONE).convert('RGB').save('keyart_in_palette.png')
print(hexs)
