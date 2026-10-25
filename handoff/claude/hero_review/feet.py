import sys,json;sys.path.insert(0,sys.argv[1]+'/handoff/claude/hero_fix2');import h8lib
s,j,k,H=h8lib.load(sys.argv[1]);A=H['anims']
names=[n for n in A if any(n.startswith(p) for p in ('idle_','walk_','run_','dash_','hurt_','hit1_','jump_')) and not n.endswith('_left')]
for n in names:
  bots=[]
  for fr in A[n]:
    sh,c=fr[0],fr[1]; im,ax,ay=h8lib.cell(sys.argv[1],H,sh,c)
    a=im.split()[3].point(lambda v:255 if v>40 else 0);b=a.getbbox(); bots.append(b[3]-ay if b else None)
  print(n.ljust(10),bots)
