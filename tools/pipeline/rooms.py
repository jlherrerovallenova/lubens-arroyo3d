import pickle, collections, json
import shapely.geometry as sg
from shapely.ops import unary_union
from shapely.strtree import STRtree
g,texts=pickle.load(open('/home/claude/work/geom.pkl','rb'))
X0,X1,Y0,Y1=790,870,383,475
polys=[]
for pl in g['A-04-SUP_UTILES']:
    if X0<pl[0][0]<X1 and Y0<pl[0][1]<Y1 and len(pl)>=4:
        p=sg.Polygon(pl).buffer(0)
        if p.area<0.3: continue
        if any(abs(p.area-q.area)<0.005 and p.centroid.distance(q.centroid)<0.02 for q in polys): continue
        polys.append(p)
print('rooms',len(polys))
# labels
names=[];areas=[]
for t in texts:
    if not(X0<t[1]<X1 and Y0<t[2]<Y1): continue
    base=t[0].split(' @')[0]
    if '@' in t[0] and not t[0].endswith('0.2'): continue
    s=t[3].strip()
    if base=='0-ESTANCIA' and s: names.append((sg.Point(t[1],t[2]),s))
    if base=='0-SUPERFICIES' and s:
        try: areas.append((sg.Point(t[1],t[2]),float(s.replace(',','.'))))
        except: pass
R=[dict(i=i,poly=p,area=round(p.area,2),name=None,lab_area=None) for i,p in enumerate(polys)]
def inside(pt):
    c=[r for r in R if r['poly'].contains(pt)]
    return min(c,key=lambda r:r['poly'].area) if c else None
for pt,s in names:
    r=inside(pt)
    if r and not r['name']: r['name']=s
for pt,a in areas:
    r=inside(pt)
    if r: r['lab_area']=a if r['lab_area'] is None else r['lab_area']
print('labeled',sum(1 for r in R if r['name']), 'with area label',sum(1 for r in R if r['lab_area']))
# check label area vs computed
d=[(r['area'],r['lab_area'],r['name']) for r in R if r['lab_area']]
bad=[x for x in d if abs(x[0]-x[1])>0.1]
print('area mismatches',len(bad),bad[:20])
pickle.dump(R,open('/home/claude/work/rooms0.pkl','wb'))
