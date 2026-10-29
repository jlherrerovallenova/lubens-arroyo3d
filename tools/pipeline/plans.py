import json, numpy as np, base64, io
from PIL import Image
A='/mnt/user-data/attachments/18124c89-ebff-5c67-b850-22d328d2dc05/'
files=['7c0e5160','5acce58d','5523f1ad','2a2e8c27','54c501c1','4ee12cb2','8d093441','354ad328','908b6d85','8f6447ea','969a5399','2e324bd0','4a625367','2be99567','ae379560']
MAP=[('09','B',True),('12','C',False),('12','B',False),('12','B',True),('12','A',False),('12','D',False),('11','A',False),('11','B',False),('10','D',False),('10','C',False),('10','B',False),('10','A',False),('09','D',False),('09','A',False),('09','C',False)]
D=json.load(open('/home/claude/work/data.json'))
tipo=D['tipo']; foot=D['g3']['footT']
out={}
for f,(p,l,opt) in zip(files,MAP):
    im=Image.open(A+f+'-image.jpg').convert('RGB'); a=np.array(im).astype(int)
    # purple label mask
    purple=(abs(a[:,:,0]-128)<40)&(abs(a[:,:,1]-96)<40)&(abs(a[:,:,2]-128)<45)&(a[:,:,0]>a[:,:,1]+15)
    dark=(a.sum(2)<450)&~purple
    # remove purple label region area (dilate)
    ys,xs=np.nonzero(dark)
    # robust bbox: ignore isolated pixels by percentiles
    x0,x1=np.percentile(xs,[0.05,99.95]).astype(int); y0,y1=np.percentile(ys,[0.05,99.95]).astype(int)
    # erase label
    a2=np.array(im); a2[purple]=255
    # also clear text of label (black letter inside purple box): fill bbox of purple region with white
    py,px=np.nonzero(purple)
    if len(px): a2[py.min():py.max()+1, px.min():px.max()+1]=255
    crop=Image.fromarray(a2).crop((x0,y0,x1+1,y1+1))
    k=next(i for i,t in enumerate(tipo) if t['portal']==p and t['letter']==l)
    xs_=[pt[0] for s in foot[k] for pt in s['o']]; ys_=[pt[1] for s in foot[k] for pt in s['o']]
    bw,bh=(max(xs_)-min(xs_))/100,(max(ys_)-min(ys_))/100
    ar_img=(x1-x0)/(y1-y0); ar_u=bw/bh
    W=1100; sc=W/crop.size[0]; crop=crop.resize((W,int(crop.size[1]*sc)),Image.LANCZOS)
    b=io.BytesIO(); crop.save(b,'JPEG',quality=82,optimize=True)
    key=f"{p}{l}{'o' if opt else ''}"
    out[key]=dict(img='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode(),w=crop.size[0],h=crop.size[1],k=k,opt=opt,
                  bbox=[min(xs_),min(ys_),max(xs_),max(ys_)])
    crop.save(f'/home/claude/work/plans/{key}.jpg')
    print(key, 'img AR %.3f unit AR %.3f'%(ar_img,ar_u), 'm/px x %.4f y %.4f'%(bw/(x1-x0), bh/(y1-y0)), len(b.getvalue())//1024,'KB')
json.dump(out,open('/home/claude/work/plans.json','w'))
