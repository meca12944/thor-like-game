import json,subprocess,sys,os
from concurrent.futures import ThreadPoolExecutor
jobs=json.load(open('all/jobs.json'));sel=sys.argv[1:]
if sel: jobs=[j for j in jobs if any(j['out'].endswith(s) for s in sel)]
def go(j):
    if os.path.exists(j['out']+'/000.png'): return j['out']+' skip'
    for t in range(4):
      r=subprocess.run(['python3','all/gen_skel.py',j['first'],j['fkp'],j['kp'],j['dir'],j['out'],'71'],env=dict(os.environ,ACTION=j['act']),capture_output=True,text=True)
      if os.path.exists(j['out']+'/000.png'): break
    return j['out']+' '+(r.stdout.strip().splitlines() or ['?'])[-1]+r.stderr[-200:]
with ThreadPoolExecutor(8) as ex:
    for s in ex.map(go,jobs): print(s,flush=True)
