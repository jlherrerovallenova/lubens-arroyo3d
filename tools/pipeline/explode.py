# Explode modelspace into polylines per layer (recursing blocks), save pickle
import ezdxf, sys, pickle, math, collections, logging
logging.disable(logging.WARNING)
from ezdxf.math import Matrix44
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
out = collections.defaultdict(list)   # layer -> list of point lists
texts=[]
def flat(e, layer_override=None, depth=0):
    t = e.dxftype()
    L = e.dxf.layer
    if L == '0' and layer_override: L = layer_override
    try:
        if t == 'INSERT':
            if depth>8: return
            for v in e.virtual_entities(): flat(v, L, depth+1)
            return
        if t in ('TEXT','MTEXT'):
            s = e.dxf.text if t=='TEXT' else e.plain_text()
            texts.append((L, e.dxf.insert.x, e.dxf.insert.y, s, e.dxf.get('rotation',0))); return
        if t == 'LINE':
            out[L].append([(e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)]); return
        if t in ('LWPOLYLINE','POLYLINE','ARC','CIRCLE','ELLIPSE','SPLINE'):
            from ezdxf import path
            p = path.make_path(e)
            pts = [(v.x,v.y) for v in p.flattening(0.02)]
            if len(pts)>1: out[L].append(pts)
            return
        if t == 'MLINE':
            for v in e.virtual_entities(): flat(v, L, depth+1)
            return
        if t == 'HATCH':
            from ezdxf import path
            for p in path.from_hatch(e):
                pts=[(v.x,v.y) for v in p.flattening(0.05)]
                if len(pts)>1: out['HATCH::'+L].append(pts)
            return
        if t == 'DIMENSION':
            return
    except Exception as ex:
        pass
for e in msp: flat(e)
pickle.dump((dict(out),texts), open(sys.argv[2],'wb'))
for k,v in sorted(out.items(), key=lambda kv:-len(kv[1]))[:60]: print(len(v),k)
print('texts',len(texts))
