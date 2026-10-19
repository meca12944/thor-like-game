import json,os,urllib.request
A='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/atk1_v1'
for f in sorted(os.listdir(A+'/_raw')):
    if not f.startswith('job_'): continue
    d=f[4:-5]; r=json.load(open(A+'/_raw/'+f))
    if r.get('status')!='completed': print(d,'FAILED',str(r)[:300]); continue
    os.makedirs(f'{A}/{d}',exist_ok=True)
    for i,u in enumerate(r['last_response']['storage_urls']['frames']):
        open(f'{A}/{d}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})).read())
    print(d,len(r['last_response']['storage_urls']['frames']),'gens',r.get('usage'))
