const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const b=await chromium.launch(); const p=await b.newPage();
 p.on('console',m=>console.log('PAGE',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
 await p.route('http://sk.local/**',r=>{const u=r.request().url(); if(u.endsWith('/')) return r.fulfill({body:'<html><body></body></html>',contentType:'text/html'}); r.fulfill({path:__dirname+'/node_modules/straight-skeleton/dist/index.js',contentType:'application/javascript'});});
 await p.goto('http://sk.local/'); await p.addScriptTag({url:'http://sk.local/index.js'});
 const D={g3:{skinT:JSON.parse(fs.readFileSync('ring_s.json','utf8'))}};
 const out=await p.evaluate(async(ring0)=>{const SB=(window.SkeletonBuilder||window['straight-skeleton']?.SkeletonBuilder); if(!SB) return {keys:Object.keys(window).filter(k=>/skel/i.test(k))};
   let ring=ring0.map(p=>[p[0],p[1]]);
   const simp=(r,eps)=>{let out=r.slice(); let ch=true; while(ch){ch=false; for(let i=0;i<out.length;i++){const a=out[(i-1+out.length)%out.length],b=out[i],c=out[(i+1)%out.length]; const ab=Math.hypot(b[0]-a[0],b[1]-a[1]); const cr=Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/Math.max(1e-9,Math.hypot(c[0]-a[0],c[1]-a[1])); if(ab<1e-3||cr<eps){out.splice(i,1);ch=true;break;}}} return out;};
   ring=simp(ring,0.02); let A=0; for(let i=0;i<ring.length;i++){const [x1,y1]=ring[i],[x2,y2]=ring[(i+1)%ring.length];A+=x1*y2-x2*y1;} if(A<0) ring.reverse();
   await SB.init(); const res=SB.buildFromPolygon([[...ring,ring[0]]]); return {v:res.vertices,f:res.polygons,ring};
 }, D.g3.skinT[0]);
 if(out.keys){console.log(out.keys); const ks=await p.evaluate(()=>Object.keys(window).slice(-20)); console.log(ks);} else { fs.writeFileSync('roof_raw.json',JSON.stringify(out)); const t=out.v.map(v=>v[2]); console.log('ring',out.ring.length,'verts',out.v.length,'faces',out.f.length,'maxT',Math.max(...t)); const h={}; t.filter(x=>x>0).forEach(x=>{const k=x.toFixed(1);h[k]=(h[k]||0)+1}); console.log(Object.entries(h).sort((a,b)=>b[1]-a[1]).slice(0,8)); }
 await b.close();})();
