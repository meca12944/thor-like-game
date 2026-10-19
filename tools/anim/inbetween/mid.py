import json,math
def load(n):
    K=json.load(open(f'inb/{n}_kp.json'))['keypoints']
    return {k['label']:k for k in K}
def sw(l): return l.replace('LEFT','#').replace('RIGHT','LEFT').replace('#','RIGHT')
def cost(A,B,swap):
    return sum(math.hypot(A[l]['x']-B[sw(l) if swap else l]['x'],A[l]['y']-B[sw(l) if swap else l]['y']) for l in A if 'LEG' in l or 'KNEE' in l or 'ARM' in l)
def clean(k,label=None): return {'x':k['x'],'y':k['y'],'label':label or k['label'],'z_index':int(k.get('z_index',0))}
for pre in 'du':
    for i in range(4):
        a,b=f'{pre}{i}',f'{pre}{(i+1)%4}';A,B=load(a),load(b)
        s=cost(A,B,True)<cost(A,B,False)
        if s: print(a,b,'L/R swapped by estimator, fixing')
        Bm={l:B[sw(l) if s else l] for l in A}
        fa=[clean(A[l]) for l in A]; fb=[clean(Bm[l],l) for l in A]
        fm=[{'x':(A[l]['x']+Bm[l]['x'])/2,'y':(A[l]['y']+Bm[l]['y'])/2,'label':l,'z_index':int(A[l].get('z_index',0))} for l in A]
        json.dump([fa,fm,fb],open(f'inb/seq_{a}.json','w'))
