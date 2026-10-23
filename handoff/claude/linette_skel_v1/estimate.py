# usage: estimate.py <img.png> <out_kp.json>   (PixelLab /estimate-skeleton, ~0.1 gen). Key from env only.
import os,sys,json,base64,subprocess,time
K=os.environ['PIXELLAB_API_KEY']
body={'image':{'type':'base64','base64':base64.b64encode(open(sys.argv[1],'rb').read()).decode(),'format':'png'}}
r=subprocess.run(['curl','-sS','--retry','4','--retry-all-errors','-X','POST','-H','Authorization: Bearer '+K,'-H','Content-Type: application/json','--data-binary','@-','https://api.pixellab.ai/v2/estimate-skeleton'],input=json.dumps(body),capture_output=True,text=True)
j=json.loads(r.stdout); json.dump(j,open(sys.argv[2],'w'),indent=1)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'run.log'),'a').write(time.strftime('%F %T ')+f"estimate {sys.argv[1]} usage {json.dumps(j.get('usage'))} keys {list(j.keys())}\n")
print(list(j.keys()), j.get('usage'), len(j.get('keypoints',[])))
