import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
bal = lambda: pl.req('GET', '/balance')['subscription']['generations']
j = pl.wait('7254dfc1-ca74-4aab-b5fb-d2cabd24b05e', every=2); rec = pl.log('prop_barrel', '/map-objects', j); ims = pl.images(j)
for i, b in enumerate(ims): open(f'out/props/barrel_{i}.png', 'wb').write(b)
print('map-object', rec, 'imgs', len(ims), 'balance', bal(), 'lr keys', list((j.get('last_response') or {}).keys()))
