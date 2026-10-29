# Mansard roof from the straight skeleton (roof_skeleton.js -> roof_raw.json):
# 35° slopes clipped at 2.25 m, flat top above, chimneys and lift/stair overruns. Writes roof.json (stored as data.roof).
import json, math
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=json.load(open('roof_raw.json')); V=R['v']
SLOPE=math.tan(math.radians(35)); HC=2.25; TC=HC/SLOPE
faces=[]; tops=[]
for poly in R['f']:
    pts=[V[i] for i in poly]; n=len(pts); e=None
    for i in range(n):
        a,b=pts[i],pts[(i+1)%n]
        if abs(a[2])<1e-6 and abs(b[2])<1e-6 and math.hypot(b[0]-a[0],b[1]-a[1])>1e-6: e=(a,b); break
    if not e: continue
    a,b=e; L=math.hypot(b[0]-a[0],b[1]-a[1]); dx,dy=(b[0]-a[0])/L,(b[1]-a[1])/L
    P=Polygon([(p[0],p[1]) for p in pts]).buffer(0)
    if P.is_empty: continue
    c=P.representative_point(); nx,ny=-dy,dx
    if (c.x-a[0])*nx+(c.y-a[1])*ny<0: nx,ny=-nx,-ny
    far=500
    hp=Polygon([(a[0]-dx*far,a[1]-dy*far),(a[0]+dx*far,a[1]+dy*far),(a[0]+dx*far+nx*TC,a[1]+dy*far+ny*TC),(a[0]-dx*far+nx*TC,a[1]-dy*far+ny*TC)])
    Q=P.intersection(hp)
    for g in ([Q] if Q.geom_type=='Polygon' else [g for g in getattr(Q,'geoms',[]) if g.geom_type=='Polygon']):
        if g.area<1e-4: continue
        out=[]
        for (x,y) in list(g.exterior.coords)[:-1]:
            t=max(0.0,(x-a[0])*nx+(y-a[1])*ny); u=(x-a[0])*dx+(y-a[1])*dy
            out.append([round(x,3),round(y,3),round(t*SLOPE,3),round(u,3),round(t/math.cos(math.atan(SLOPE)),3)])
        faces.append(out)
    rem=P.difference(hp)
    if not rem.is_empty: tops.append(rem)
top=unary_union(tops).buffer(0.01,join_style=2).buffer(-0.01,join_style=2)
tg=[top] if top.geom_type=='Polygon' else list(top.geoms)
TOP=[{'o':[[round(x,3),round(y,3)] for x,y in g.exterior.coords[:-1]],'h':[[[round(x,3),round(y,3)] for x,y in i.coords[:-1]] for i in g.interiors]} for g in tg if g.area>0.5]
ch=[]
for g in tg:
    inner=g.buffer(-0.9,join_style=2)
    for gg in ([inner] if inner.geom_type=='Polygon' else list(getattr(inner,'geoms',[]))):
        if gg.is_empty: continue
        ext=gg.exterior; k=0; s=2.0
        while s<ext.length:
            p=ext.interpolate(s); ch.append([round(p.x,2),round(p.y,2),[0.55,0.7,1.1][k%3]]); k+=1; s+=6.5+(k%3)*1.3
D=json.load(open('../../src/data.json'))
over=[]
for c in D['g3']['commT']:
    q=Polygon([(x/100,y/100) for x,y in c['o']]).buffer(0).intersection(top)
    if q.area>3: over.append([[round(x,2),round(y,2)] for x,y in list(q.minimum_rotated_rectangle.exterior.coords)[:-1]])
json.dump({'faces':faces,'top':TOP,'h':HC,'ch':ch,'over':over},open('roof.json','w'))
