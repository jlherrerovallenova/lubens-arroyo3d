import pickle, json, base64, io, subprocess
import shapely.geometry as sg
from shapely.ops import unary_union
from PIL import Image
out,tipo,pb,outline,coef=pickle.load(open('/home/claude/work/export2.pkl','rb'))
RT,UT=pickle.load(open('/home/claude/work/units_tipo.pkl','rb'))
SRC='/mnt/user-data/attachments/18124c89-ebff-5c67-b850-22d328d2dc05/'
F={ # page coords @100dpi
 'A2':dict(pdf='92b83ebf-31-LV-VA-01-ARQUITECTURA-A08.pdf',crop=(130,90,1490,600),fx=(158,1438),pa=('x',861.7,795.9),segs=[(0,9999,505)],name='C/ Torres Quevedo',band=sg.box(780,468.5,880,480)),
 'A1':dict(pdf='1f66a0d4-31-LV-VA-01-ARQUITECTURA-A07.pdf',crop=(880,140,2190,620),fx=(902,2162),pa=('x',795.9,861.7),segs=[(0,9999,538)],name='C/ Antonio de Ulloa',band=sg.box(780,370,880,388.6)),
 'A3':dict(pdf='5c5f4fdd-31-LV-VA-01-ARQUITECTURA-A09_bis.pdf',crop=(80,800,1720,1290),fx=(100,1700),pa=('y',387.0,470.25),segs=[(0,900,1228),(900,9999,1194)],name='C/ Severo Ochoa',band=sg.box(860,370,880,480)),
 'A4':dict(pdf='5c5f4fdd-31-LV-VA-01-ARQUITECTURA-A09_bis.pdf',crop=(50,70,1720,560),fx=(80,1690),pa=('y',470.25,387.0),segs=[(0,880,466),(880,9999,501)],name='Patio interior',band=unary_union([sg.box(780,370,797.6,480),sg.box(843.0,404,845.6,453)])),
}
S=1.5  # render at 150 dpi
res={}
for k,c in F.items():
    png=f'/home/claude/work/elev/{k}'
    subprocess.run(['pdftoppm','-r','150','-png','-singlefile',SRC+c['pdf'],png],check=True,stderr=subprocess.DEVNULL)
    im=Image.open(png+'.png').convert('RGB')
    x0,y0,x1,y1=[int(v*S) for v in c['crop']]
    im=im.crop((x0,y0,x1,y1))
    b=io.BytesIO(); im.save(b,'JPEG',quality=78,optimize=True,progressive=True)
    data='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
    print(k,im.size,len(b.getvalue())//1024,'KB')
    # transform helpers in crop px @150
    fx0,fx1=[v*S - x0 for v in c['fx']]
    ax,p0,p1=c['pa']
    segs=[(a*S-x0,bb*S-x0,yb*S-y0) for a,bb,yb in c['segs']]
    units=[]
    for i,u in enumerate(UT):
        P=unary_union([RT[j]['poly'] for j in u['ids']])
        I=P.intersection(c['band'])
        if I.is_empty or I.area<0.3: continue
        bx=I.bounds
        lo,hi=(bx[0],bx[2]) if ax=='x' else (bx[1],bx[3])
        if hi-lo<1.0: continue
        # map plan -> px
        m=lambda v: fx0+(v-p0)/(p1-p0)*(fx1-fx0)
        a,bp=sorted([m(lo),m(hi)])
        cx=(a+bp)/2
        yb=next(s[2] for s in segs if s[0]<=cx<s[1])
        units.append(dict(k=i,x0=round(a,1),x1=round(bp,1),yb=round(yb,1)))
    res[k]=dict(name=c['name'],img=data,w=im.size[0],h=im.size[1],pitch=57.5*S,units=units)
    print('  units',[(tipo[u['k']]['portal'],tipo[u['k']]['letter'],u['x0'],u['x1']) for u in units])
json.dump(res,open('/home/claude/work/elev.json','w'))
