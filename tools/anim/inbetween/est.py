# PixelLab /v2/estimate-skeleton. usage: est.py in.png out.json  (key from env, never printed)
import os,sys,json,base64,urllib.request,time
KEY=os.environ['PIXELLAB_API_KEY']
b={'image':{'type':'base64','base64':base64.b64encode(open(sys.argv[1],'rb').read()).decode(),'format':'png'}}
for a in range(5):
    try:
        r=urllib.request.Request('https://api.pixellab.ai/v2/estimate-skeleton',data=json.dumps(b).encode(),method='POST',headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
        with urllib.request.urlopen(r,timeout=300) as f: d=json.loads(f.read()); break
    except Exception as e: print('retry',type(e).__name__); time.sleep(10)
json.dump(d,open(sys.argv[2],'w')); print('ok',d.get('usage'))
