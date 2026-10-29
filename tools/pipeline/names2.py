import pickle, collections, math
import shapely.geometry as sg, shapely.affinity as sa
g,texts=pickle.load(open('/home/claude/work/geom.pkl','rb'))
R=pickle.load(open('/home/claude/work/rooms1.pkl','rb'))
X0,X1,Y0,Y1=790,870,383,475
NM=[];AR=[]
for t in texts:
    if not(X0<t[1]<X1 and Y0<t[2]<Y1): continue
    if '@' in t[0] and not t[0].endswith('0.2'): continue
    b=t[0].split(' @')[0]; s=t[3].strip()
    if b=='0-ESTANCIA' and s and not re.match if False else None: pass
    if b=='0-ESTANCIA' and s and not s[0].isdigit() and not s.startswith('t'): NM.append((t[1],t[2],s))
    if b=='0-SUPERFICIES' and s:
        try: AR.append((t[1],t[2],float(s)))
        except: pass
for r in R: r['name']=None; r['src']=None
used=set(); pairs=[]
for (ax,ay,v) in AR:
    if v>40: continue
    # nearest name label
    best=min(NM,key=lambda n:math.hypot(n[0]-ax,n[1]-ay)) if NM else None
    dn=math.hypot(best[0]-ax,best[1]-ay)
    name=best[2] if dn<1.2 else None
    cands=[r for r in R if abs(r['area']-v)<0.12]
    if not cands: continue
    r=min(cands,key=lambda r:r['poly'].distance(sg.Point(ax,ay)))
    if r['poly'].distance(sg.Point(ax,ay))>2.5: continue
    if name and not r['name']: r['name']=name; r['src']='label'
print('labeled',sum(1 for r in R if r['name']))
AXY=428.55
def sig(p):
    b=p.bounds; return (round(p.area,1),tuple(sorted((round(b[2]-b[0],1),round(b[3]-b[1],1)))))
for r in R:
    if r['name']: continue
    m=sa.scale(r['poly'],1,-1,origin=(0,AXY))
    for q in R:
        if q['name'] and q['src']=='label' and abs(q['area']-r['area'])<0.05 and q['poly'].intersection(m).area>0.9*r['area']:
            r['name']=q['name']; r['src']='mirror'; break
for r in R:
    if r['name']: continue
    c=collections.Counter(q['name'] for q in R if q['src']=='label' and sig(q['poly'])==sig(r['poly']))
    if len(c)==1: r['name']=list(c)[0]; r['src']='sig'
print('after prop',sum(1 for r in R if r['name']))
for r in R:
    if not r['name']: print('  unk',r['area'],round(r['poly'].centroid.x,1),round(r['poly'].centroid.y,1),r['fur'])
pickle.dump(R,open('/home/claude/work/rooms2.pkl','wb'))
