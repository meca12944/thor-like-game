import sys,json,subprocess,os
j=json.loads(sys.argv[1]);D=os.path.dirname(os.path.abspath(__file__));py=sys.executable
if j[0]=='walk':
    _,n,d,base,key,ep,cp=j
    if not os.path.exists(f'{D}/{key}'):subprocess.run([py,f'{D}/edit_pose.py',f'{D}/{base}',f'{D}/{key}',f'{n}{d[0]}',ep,'5'])
    if os.path.exists(f'{D}/{key}') and not os.path.isdir(f'{D}/tw8_{n}_{d[0]}'):subprocess.run([py,f'{D}/tween.py',f'{D}/{key}',f'{D}/{key}',f'{D}/tw8_{n}_{d[0]}','8',cp,'11'])
else:
    _,n,d,base,ip=j
    if not os.path.isdir(f'{D}/idle_{n}_{d[0]}'):subprocess.run([py,f'{D}/tween.py',f'{D}/{base}',f'{D}/{base}',f'{D}/idle_{n}_{d[0]}','4',ip,os.environ.get('SEED','7')])
