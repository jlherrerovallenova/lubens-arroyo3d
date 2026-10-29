s=open('src/app_template.html').read()
d=open('src/data.json').read().replace('</','<\\/')
s=s.replace('/*DATA*/',d)
old="""    downloads = dl || null;"""
assert old in s
s=s.replace(old,"""    downloads = dl || (window.claude ? null : {save: async ({filename, data}) => { const blob = data instanceof Blob ? data : new Blob([data], {type: filename.endsWith('.svg')?'image/svg+xml':'text/csv;charset=utf-8'}); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename; document.body.appendChild(a); a.click(); setTimeout(()=>{URL.revokeObjectURL(a.href); a.remove();}, 1000); }});""")
old="""    const [dbc, uc, dl] = await Promise.all("""
assert old in s
s=s.replace(old,"""    if(!window.claude){ document.documentElement.classList.add('standalone'); }
    const [dbc, uc, dl] = await Promise.all(""")
s=s.replace("""    if(!db){ note.textContent = 'Estados en modo local: inicia sesión para ver y guardar los del equipo.'; return; }""","""    if(!db){ note.textContent = window.claude ? 'Estados en modo local: inicia sesión para ver y guardar los del equipo.' : ''; return; }""")
s=s.replace("@media (prefers-reduced-motion:reduce)",".standalone .status-edit{display:none}\n@media (prefers-reduced-motion:reduce)")
head='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
open('index.html','w').write(head+s+'</body></html>')
print('netlify build ok')
