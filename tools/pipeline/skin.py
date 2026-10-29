import pickle, json
import shapely.geometry as sg
from shapely.ops import unary_union
RT,UT=pickle.load(open('/home/claude/work/units_tipo.pkl','rb'))
RP,UP=pickle.load(open('/home/claude/work/units_pb2.pkl','rb'))
OX,OY=795.5,471.0
L=lambda x,y,dx=0:[round(x+dx-OX,3),round(OY-y,3)]   # local metres (x right, y down)
def env(polys,r=0.7):
    return unary_union(polys).buffer(r,join_style=2).buffer(-r,join_style=2)
def rings(g,dx=0):
    out=[]
    for p in getattr(g,'geoms',[g]):
        if p.area<4: continue
        out.append([L(x,y,dx) for x,y in list(p.simplify(0.05).exterior.coords)[:-1]])
    return out
skinT=env([r['poly'] for r in RT]).buffer(0.25,join_style=2)
skinP=env([r['poly'] for r in RP],0.6).buffer(0.25,join_style=2)
ov=[]
for u in UT:
    P=unary_union([RT[i]['poly'] for i in u['ids']]).buffer(0.5,join_style=2).buffer(-0.1,join_style=2)
    ov.append([[L(x,y) for x,y in list(p.simplify(0.05).exterior.coords)[:-1]] for p in getattr(P,'geoms',[P]) if p.area>0.5])
S=1.5
def cfg(crop,fx,axis,p0,p1,segs):
    x0,y0=crop[0]*S,crop[1]*S
    loc=(lambda v:v-OX) if axis=='x' else (lambda v:OY-v)
    return dict(axis=axis,a0=round(loc(p0),3),a1=round(loc(p1),3),px0=fx[0]*S-x0,px1=fx[1]*S-x0,
                segs=[[a*S-x0 if a>0 else -1e9, b*S-x0 if b<9000 else 1e9, yb*S-y0] for a,b,yb in segs])
M={'A2':cfg((130,90),(158,1438),'x',861.7,795.9,[(0,9999,505)]),
   'A1':cfg((880,140),(902,2162),'x',795.9,861.7,[(0,9999,538)]),
   'A3':cfg((80,800),(100,1700),'y',387.0,470.25,[(0,900,1228),(900,9999,1194)]),
   'A4':cfg((50,70),(80,1690),'y',470.25,387.0,[(0,880,466),(880,9999,501)])}
D=json.load(open('/home/claude/work/data.json'))
D['g3']['skinT']=rings(skinT); D['g3']['skinP']=rings(skinP,250); D['g3']['ovT']=ov; D['elevmap']=M
json.dump(D,open('/home/claude/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
print(len(D['g3']['skinT']),[len(r) for r in D['g3']['skinT']],len(D['g3']['skinP']), M['A3'])
print('skin bounds',skinT.bounds)
