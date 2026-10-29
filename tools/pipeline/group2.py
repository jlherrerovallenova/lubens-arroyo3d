import pickle, collections, sys
from shapely.ops import unary_union
R,_,_=pickle.load(open('/home/claude/work/groups.pkl','rb'))
pairs=pickle.load(open('/home/claude/work/pairs.pkl','rb'))
TH=float(sys.argv[1]) if len(sys.argv)>1 else 0.13
COMMON=('Rellano','Escalera','Instalaciones','INSTALACIONES','INSTAL.','PORTAL')
isc=lambda r:(r['name'] or '').strip().startswith(COMMON)
par=list(range(len(R)))
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for (a,b),(t,L) in pairs.items():
    if t<=TH and not isc(R[a]) and not isc(R[b]): par[f(a)]=f(b)
G=collections.defaultdict(list)
for r in R:
    if not isc(r): G[f(r['i'])].append(r['i'])
out=[]
for k,ids in G.items():
    A=sum(R[i]['area'] for i in ids); c=unary_union([R[i]['poly'] for i in ids]).centroid
    out.append((A,ids,c))
out.sort(key=lambda o:(-o[0]))
for A,ids,c in out:
    print(f"{A:7.2f} n={len(ids):2d} ({c.x:.1f},{c.y:.1f})",dict(collections.Counter((R[i]['name'] or '?') for i in ids)))
pickle.dump(out,open('/home/claude/work/dw.pkl','wb'))
# ambiguous pairs
for (a,b),(t,L) in pairs.items():
    if 0.14<t<0.21: print('amb',t,round(L,2),R[a]['name'],R[b]['name'],round(R[a]['poly'].centroid.x,1),round(R[a]['poly'].centroid.y,1))
