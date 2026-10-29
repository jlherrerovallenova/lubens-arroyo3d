import pickle, collections, json, re
import shapely.geometry as sg
from shapely.ops import unary_union
g,texts=pickle.load(open('/home/claude/work/geom.pkl','rb'))
R=pickle.load(open('/home/claude/work/rooms2.pkl','rb'))
dw=pickle.load(open('/home/claude/work/dw.pkl','rb'))
def infer(r):
    a=r['area'];f=r['fur'];c=r['poly'].centroid
    if c.x>859.4: return 'Terraza'
    if a<2.3: return 'Armario'
    if f['COCINA']>100 and a>20: return 'Salón-cocina-comedor'
    if f['COCINA']>100: return 'Cocina'
    if f['MOBILIARIO']>40: return 'Salón-comedor'
    if f['SANITARIOS']>5: return 'Baño'
    if a>=9: return 'Dormitorio'
    if a<3: return 'Tendedero'
    if a>4.5: return 'Vestíbulo'
    return 'Pasillo'
for r in R:
    if not r['name']: r['name']=infer(r); r['src']='infer'
    r['name']=r['name'].strip()
big=[(A,ids,c) for A,ids,c in dw if A>40]
small=[(A,ids,c) for A,ids,c in dw if A<=40]
groups=[list(ids) for A,ids,c in big]
U=[unary_union([R[i]['poly'] for i in ids]) for ids in groups]
for A,ids,c in small:
    for i in ids:
        d=[(U[k].distance(R[i]['poly']),k) for k in range(len(U))]
        dmin,k=min(d)
        print('leftover',R[i]['name'],R[i]['area'],'->',round(dmin,2))
        if dmin<0.7: groups[k].append(i)
EXT={'Terraza','Tendedero','Terraza-patio'}
for ids in groups:
    ds=sorted([R[i] for i in ids if R[i]['name'].startswith('Dormitorio')],key=lambda r:-r['area'])
    for k,r in enumerate(ds): r['name']='Dormitorio principal' if k==0 else f'Dormitorio {k+1}'
    # merge: Terraza-patio normalize

# architect total labels
tot=[]
for t in texts:
    if t[0]=='0-SUPERFICIES @ 0.2' and 790<t[1]<870 and 383<t[2]<475:
        try:
            v=float(t[3]);
            if v>40: tot.append((sg.Point(t[1],t[2]),v))
        except: pass
units=[]
for ids in groups:
    rooms=[R[i] for i in ids]
    inter=[r for r in rooms if r['name'] not in EXT]
    ext=[r for r in rooms if r['name'] in EXT]
    ui=sum(r['area'] for r in inter); ue=sum(r['area'] for r in ext)
    poly=unary_union([r['poly'] for r in rooms])
    polyi=unary_union([r['poly'] for r in inter])
    cons=polyi.buffer(0.15,join_style=2).buffer(-0.0).area
    dorms=sorted([r for r in rooms if r['name'].startswith('Dormitorio')],key=lambda r:-r['area'])
    baths=[r for r in rooms if r['name'] in ('Baño','Aseo')]
    near=[v for p,v in tot if poly.buffer(1.5).contains(p)]
    c=poly.centroid
    units.append(dict(ids=ids,util=round(ui,2),ext=round(ue,2),cons=round(cons,2),dorm=len(dorms),banos=len(baths),cx=c.x,cy=c.y,arch=near))
    print(f"({c.x:.1f},{c.y:.1f}) util {ui:6.2f} ext {ue:5.2f} cons~{cons:6.1f} D{len(dorms)} B{len(baths)} arch {near}  ",sorted(r['name'] for r in rooms))
pickle.dump((R,units),open('/home/claude/work/units_tipo.pkl','wb'))
