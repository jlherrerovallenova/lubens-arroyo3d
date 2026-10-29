import pickle, json, math, numpy as np
OFF = {
 ('09','A'):(84.18,10.70,109.85,[255,260,265,270,275]),('09','B'):(79.01,2.59,96.18,[230,235,240,245,250]),
 ('09','C'):(79.09,2.59,97.24,[225,230,235,240,245]),('09','D'):(74.05,8.07,94.51,[210,215,220,225,230]),
 ('10','A'):(83.95,10.70,109.43,[255,260,265,270,275]),('10','B'):(71.28,6.15,88.13,[205,210,215,220,225]),
 ('10','C'):(70.83,8.07,91.26,[200,205,210,215,220]),('10','D'):(69.05,4.70,87.26,[190,195,200,205,210]),
 ('11','A'):(77.96,9.46,101.50,[240,245,250,255,260]),('11','B'):(90.89,17.71,127.37,[285,290,295,300,305]),
 ('12','A'):(86.72,7.85,111.37,[250,255,260,265,270])}
PRICE_ONLY={('12','B'):[190,195,200,205,210],('12','C'):[215,220,225,230,235],('12','D'):[255,260,265,270,275]}
ORI={('09','A'):('Noreste','Exterior'),('09','B'):('Noreste','Exterior'),('09','C'):('Suroeste','Interior'),('09','D'):('Suroeste','Interior'),
 ('10','A'):('Noreste','Exterior'),('10','B'):('Noreste','Exterior'),('10','C'):('Suroeste','Interior'),('10','D'):('Suroeste','Interior y rincón'),
 ('11','A'):('Sureste','Exterior y esquina'),('11','B'):('Noreste','Exterior'),
 ('12','A'):('Noroeste','Interior y rincón'),('12','B'):('Noroeste','Interior'),('12','C'):('Sureste','Exterior'),('12','D'):('Sureste','Exterior')}
OPC={('09','B'),('09','C'),('12','B')}
SWAP={'Noreste':'Suroeste','Suroeste':'Noreste','Sureste':'Sureste','Noroeste':'Noroeste'}
# my (portal,letter) -> official letter
MAP={('09','A'):'A',('09','D'):'B',('09','C'):'C',('09','B'):'D',('10','A'):'A',('10','D'):'B',('10','C'):'C',('10','B'):'D',
     ('11','A'):'A',('11','B'):'B',('12','D'):'A',('12','C'):'B',('12','B'):'C',('12','A'):'D'}
out,tipo,pb,outline=pickle.load(open('/home/claude/work/export.pkl','rb'))
# fix terrace 9.78 from 11A to 11B and mirrors 14A->14B
def find(p,l): return next(u for u in tipo if u['portal']==p and u['letter']==l)
for (pa,la),(pb_,lb) in [(('11','A'),('11','B')),(('14','A'),('14','B'))]:
    ua,ub=find(pa,la),find(pb_,lb)
    r=next((r for r in ua['rooms'] if r['n']=='Terraza' and abs(r['a']-9.78)<0.01),None)
    if r: ua['rooms'].remove(r); ub['rooms'].append(r); ua['ext']=round(ua['ext']-r['a'],2); ub['ext']=round(ub['ext']+r['a'],2); print('moved terrace',pa,'->',pb_)
    else: print('no 9.78 in',pa,la,[x['a'] for x in ua['rooms'] if x['n']=='Terraza'])
AX=428.55
for u in tipo:
    u['oldletter']=u['letter']
    k=(u['portal'],u['letter'])
    if k in MAP:
        L=MAP[k]; u['letter']=L; u['lsrc']='ficha' if (u['portal'],L) in OFF else 'provisional'
        o=OFF.get((u['portal'],L))
        if o: u['off']=dict(util=o[0],ext=o[1],cons=o[2],src=f"Ficha comercial Portal {int(u['portal'])} {L}"); u['prices']=[p*1000 for p in o[3]]; u['psrc']='lista'
        if (u['portal'],L) in PRICE_ONLY: u['prices']=[p*1000 for p in PRICE_ONLY[(u['portal'],L)]]; u['psrc']='lista'; u['lsrc']='lista de precios'
        if (u['portal'],L) in ORI: u['ori_off']=list(ORI[(u['portal'],L)])
        u['opcional']=(u['portal'],L) in OPC
for u in tipo:
    if u['portal'] in ('13','14','15','16'):
        m=min((t for t in tipo if t['portal'] in ('09','10','11','12')),key=lambda t:math.hypot(t['cx']-u['cx'],t['cy']-(2*AX-u['cy'])))
        u['twin']=f"P{m['portal']}-{m['letter']}"
        u['letter']=m['letter']; u['lsrc']='simetría'
        if m.get('ori_off'): u['ori_off']=[SWAP[m['ori_off'][0]], m['ori_off'][1]]; u['ori_sym']=True
        u['opcional']=False
        if m.get('off'):
            u['off']=dict(m['off']); u['off']['src']=f"Simétrica de Portal {int(m['portal'])} {m['letter']}"
        print(u['portal'],u['oldletter'],'twin',m['portal'],m['letter'],round(u['util'],2),round(m['util'],2))
# letters unique per portal?
import collections
c=collections.Counter((u['portal'],u['letter']) for u in tipo); print([k for k,v in c.items() if v>1])
# regression base price (1st floor) on util & ext, excluding 11B 1º typo (use 2º-5)
X=[];y=[]
for (p,l),o in OFF.items():
    X.append([1,o[0],o[1]]); y.append(o[3][0])
X=np.array(X);y=np.array(y); coef,res,_,_=np.linalg.lstsq(X,y,rcond=None)
pred=X@coef; print('coef',coef,'rmse',np.sqrt(np.mean((pred-y)**2)))
for (k,o),pp in zip(OFF.items(),pred): print(k,o[3][0],round(pp,1))
for u in tipo:
    if u.get('prices'): continue
    if u.get('twin'):
        t=next(t for t in tipo if f"P{t['portal']}-{t['letter']}"==u['twin'])
        if t.get('prices'): u['sprices']=list(t['prices']); u['spsrc']=f"igual que su simétrica {u['twin']}"; continue
    ut=u['off']['util'] if u.get('off') else u['util']-1.0
    ex=u['off']['ext'] if u.get('off') else u['ext']
    b=coef[0]+coef[1]*ut+coef[2]*ex; b=round(b/5)*5
    u['sprices']=[int((b+5*i)*1000) for i in range(5)]; u['spsrc']='modelo sobre la lista de precios (útil y terraza)'
for u in tipo: print(u['portal'],u['letter'],u.get('lsrc'),u.get('prices',[None])[0],u.get('sprices',[None])[0],u.get('spsrc'))
pickle.dump((out,tipo,pb,outline,coef.tolist()),open('/home/claude/work/export2.pkl','wb'))
