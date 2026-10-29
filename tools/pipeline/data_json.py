import pickle, json
out,tipo,pb,outline,coef=pickle.load(open('/home/claude/work/export2.pkl','rb'))
geo=json.load(open('/home/claude/work/drawgeom.json'))
g3=json.load(open('/home/claude/work/geo3d.json'))
def tmpl(u,k):
    return dict(k=k,portal=u['portal'],letter=u['letter'],util=u['util'],ext=u['ext'],cons=u['cons'],dorm=u['dorm'],banos=u['banos'],
        off=u.get('off'),ori_off=u.get('ori_off'),ori_sym=u.get('ori_sym',False),opcional=u.get('opcional',False),lsrc=u.get('lsrc','provisional'),prices=u.get('prices'),sprices=u.get('sprices'),spsrc=u.get('spsrc'),twin=u.get('twin'),cx=round((u['cx']-795.5)*100),cy=round((471.0-u['cy'])*100),rooms=u['rooms'],fac=[[f['ang'],f['len'],f['side']] for f in u['fac']],streets=u['streets'])
D=dict(elev=json.load(open('/home/claude/work/elev.json')),coef=coef,tipo=[tmpl(u,i) for i,u in enumerate(tipo)], pb=[tmpl(u,i) for i,u in enumerate(pb)], geo=geo, g3=g3)
json.dump(D,open('/home/claude/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
import os; print(os.path.getsize('/home/claude/work/data.json')//1024,'KB')
print(D['tipo'][0]['rooms'][:2])
