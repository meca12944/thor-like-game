import sys;sys.path.insert(0,'.')
from fxfind import isfx
def skin(p):
    r,g,b,a=p;return a>40 and r>140 and g>90 and r>b+35
def clean(im):
    im=im.copy();px=im.load();W,H=im.size
    C=set((x,y) for y in range(H) for x in range(W) if isfx(px[x,y]))
    S=[(x,y) for y in range(H) for x in range(W) if skin(px[x,y])]
    near=set()
    for (x,y) in S:
        for dx in range(-3,4):
            for dy in range(-3,4): near.add((x+dx,y+dy))
    rm=[p for p in C if p not in near]
    rms=set(rm);new={}
    for (x,y) in rm:
        tr=0;cols=[]
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                X,Y=x+dx,y+dy
                if (dx or dy) and 0<=X<W and 0<=Y<H and (X,Y) not in rms:
                    q=px[X,Y]
                    if q[3]<=40: tr+=1
                    else: cols.append(q)
        if tr>=len(cols): new[(x,y)]=(0,0,0,0)
        else: new[(x,y)]=tuple(sum(c[i] for c in cols)//len(cols) for i in range(3))+(255,)
    for p,v in new.items(): px[p]=v
    # 몸에서 떨어진 작은 조각 지우기
    from collections import deque
    seen=set();comps=[]
    for y in range(H):
        for x in range(W):
            if px[x,y][3]>40 and (x,y) not in seen:
                q=deque([(x,y)]);seen.add((x,y));c=[]
                while q:
                    a,b=q.popleft();c.append((a,b))
                    for dx in (-1,0,1):
                        for dy in (-1,0,1):
                            X,Y=a+dx,b+dy
                            if 0<=X<W and 0<=Y<H and (X,Y) not in seen and px[X,Y][3]>40: seen.add((X,Y));q.append((X,Y))
                comps.append(c)
    comps.sort(key=len,reverse=True)
    for c in comps[1:]:
        if len(c)<40:
            for p in c: px[p]=(0,0,0,0)
    return im,len(rm)
