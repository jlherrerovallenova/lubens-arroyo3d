import pickle, json, math, collections
import shapely.geometry as sg
from shapely.ops import unary_union
g,texts=pickle.load(open('/home/claude/work/geom.pkl','rb'))
RT,UT=pickle.load(open('/home/claude/work/units_tipo.pkl','rb'))
RP,UP=pickle.load(open('/home/claude/work/units_pb2.pkl','rb'))
R0=pickle.load(open('/home/claude/work/rooms2.pkl','rb'))
OX,OY=795.5,471.0
def T(x,y): return [round((x-OX)*100), round((OY-y)*100)]
def poly_pts(p): 
    p=p.simplify(0.02); return [T(x,y) for x,y in list(p.exterior.coords)[:-1]]
# portals in tipo frame
PORT={'09':(808,459),'10':(831,459),'11':(851,456),'12':(851,441),'13':(851,418),'14':(851,401),'15':(830,398),'16':(808,398)}
COMMON=('Rellano','Escalera','Instalaciones','INSTALACIONES','INSTAL.','PORTAL')
commons=[r for r in RT if (r['name'] or '').startswith(COMMON)]
# building outline (tipo)
allp=unary_union([r['poly'] for r in RT]).buffer(0.5,join_style=2).buffer(-0.5,join_style=2)
outline=max(getattr(allp,'geoms',[allp]),key=lambda p:p.area)
COURT=sg.box(797,406,845.5,451)
from shapely.strtree import STRtree
def envelope(polys):
    e=unary_union(polys).buffer(0.7,join_style=2).buffer(-0.7,join_style=2)
    return e
def facades(P,envall,dx=0):
    env=max(getattr(envall,'geoms',[envall]),key=lambda q:q.intersection(P).area)
    ring=list(env.exterior.coords); bsegs=list(zip(ring,ring[1:]))
    segs=[]
    for gg in getattr(P,'geoms',[P]):
        cs=list(gg.exterior.coords)
        for a,b in zip(cs,cs[1:]):
            L=math.dist(a,b)
            if L<0.5: continue
            m=sg.Point((a[0]+b[0])/2,(a[1]+b[1])/2)
            if env.exterior.distance(m)>0.6: continue
            # nearest boundary segment
            bs=min(bsegs,key=lambda s:sg.LineString(s).distance(m))
            ea=math.atan2(b[1]-a[1],b[0]-a[0]); ba=math.atan2(bs[1][1]-bs[0][1],bs[1][0]-bs[0][0])
            d=abs((ea-ba+math.pi/2)%math.pi-math.pi/2)
            if d>math.radians(12): continue
            Lb=math.dist(*bs); nx,ny=(bs[1][1]-bs[0][1])/Lb,-(bs[1][0]-bs[0][0])/Lb
            q=sg.Point(m.x+nx*1.5,m.y+ny*1.5)
            if env.contains(q): nx,ny=-nx,-ny; q=sg.Point(m.x+nx*1.5,m.y+ny*1.5)
            ang=math.degrees(math.atan2(ny,nx))
            side='patio' if COURT.contains(sg.Point(q.x+dx,q.y)) else 'calle'
            segs.append(dict(ang=round(ang),len=round(L,2),side=side))
    return segs
def classify(a,cx,cy):
    if 60<a<120: return 'C/ Torres Quevedo' if cy>440 else 'Patio interior (piscina)'
    if -120<a<-60: return 'C/ Antonio de Ulloa' if cy<417 else 'Patio interior (piscina)'
    if -30<a<30: return 'C/ Severo Ochoa' if cx>850 else 'Patio interior (piscina)'
    if abs(a)>150: return 'Testero oeste' if cx<805 else 'Patio interior (piscina)'
    return None
def street(segs,cx,cy):
    tot=collections.Counter()
    for f in segs:
        k=classify(f['ang'],cx,cy)
        if k: tot[k]+=f['len']
    return [k for k,v in tot.most_common() if v>=2.0]
EXT={'Terraza','Tendedero','Terraza-patio'}
units=[]
def mk(u,rooms,floor,dx):
    rs=[rooms[i] for i in u['ids']]
    P=unary_union([r['poly'] for r in rs])
    c=P.centroid; cxt=c.x+dx
    # portal: nearest common polygon touching
    if floor>0:
        touch=[cm for cm in commons if cm['poly'].distance(P)<0.5]
        ref=min(touch,key=lambda cm:cm['poly'].distance(P)).poly.centroid if False else None
        best=None
        for cm in touch:
            cc=cm['poly'].centroid
            pn=min(PORT,key=lambda k:math.dist(PORT[k],(cc.x,cc.y)))
            d=math.dist(PORT[pn],(cc.x,cc.y))
            if best is None or d<best[1]: best=(pn,d)
        portal=best[0] if best else min(PORT,key=lambda k:math.dist(PORT[k],(cxt,c.y)))
    else:
        portal=min(PORT,key=lambda k:math.dist(PORT[k],(cxt,c.y)))
    inter=[r for r in rs if r['name'] not in EXT]
    segs=facades(P,ALL[floor],dx)
    return dict(floor=floor,portal=portal,cx=cxt,cy=c.y,
        util=round(sum(r['area'] for r in inter),2), ext=round(sum(r['area'] for r in rs if r['name'] in EXT),2),
        cons=round(unary_union([r['poly'] for r in inter]).buffer(0.15,join_style=2).area,1),
        dorm=sum(1 for r in rs if r['name'].startswith('Dormitorio')), banos=sum(1 for r in rs if r['name'] in('Baño','Aseo')),
        rooms=[dict(n=r['name'],a=r['area'],p=poly_pts(sg.Polygon([(x+dx,y) for x,y in r['poly'].exterior.coords]))) for r in sorted(rs,key=lambda r:-r['area'])],
        fac=segs, streets=street(segs,cxt,c.y))
# PB outline
pbp=unary_union([r['poly'] for r in RP]).buffer(0.6,join_style=2).buffer(-0.6,join_style=2)
outline_for={0:sg.Polygon(), 1:outline}
pbshift=unary_union([sg.Polygon([(x,y) for x,y in r['poly'].exterior.coords]) for r in RP])
outline_for[0]=max(getattr(pbp,'geoms',[pbp]),key=lambda p:p.area)
ALL={1:envelope([r['poly'] for r in RT]),0:envelope([r['poly'] for r in RP])}
tipo=[mk(u,RT,1,0) for u in UT]
pb=[mk(u,RP,0,250) for u in UP]
# letters per portal
def letters(lst):
    by=collections.defaultdict(list)
    for u in lst: by[u['portal']].append(u)
    for p,us in by.items():
        px,py=PORT[p]
        us.sort(key=lambda u:(math.atan2(u['cx']-px, u['cy']-py))%(2*math.pi))
        for k,u in enumerate(us): u['letter']='ABCDEFGH'[k]
letters(tipo); letters(pb)
out=[]
FL={0:'Baja',1:'1ª',2:'2ª',3:'3ª',4:'4ª',5:'5ª'}
for u in pb:
    out.append(dict(u,id=f"P{u['portal']}-B{u['letter']}",tipo='Estudio'))
for f in range(1,6):
    for u in tipo:
        v=dict(u); v['floor']=f; v['id']=f"P{u['portal']}-{f}{u['letter']}"; v['tipo']=f"{u['dorm']} dorm."; out.append(v)
print(len(out))
print(collections.Counter((u['portal']) for u in out if u['floor']==1), collections.Counter(u['portal'] for u in out if u['floor']==0))
for u in tipo: print(u['portal'],u['letter'],u['util'],u['dorm'],u['banos'],u['streets'])
for u in pb: print('PB',u['portal'],u['letter'],u['util'],u['streets'])
pickle.dump((out,tipo,pb,outline),open('/home/claude/work/export.pkl','wb'))
