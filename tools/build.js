const fs = require('fs');

let s = fs.readFileSync('src/app_template.html', 'utf8');
const d = fs.readFileSync('src/data.json', 'utf8').replace(/<\//g, '<\\/');
s = s.replace('/*DATA*/', d);

const old1 = '    downloads = dl || null;';
if (!s.includes(old1)) throw new Error('old1 not found');
s = s.replace(old1, '    downloads = dl || (window.claude ? null : {save: async ({filename, data}) => { const blob = data instanceof Blob ? data : new Blob([data], {type: filename.endsWith(\'.svg\')?\'image/svg+xml\':\'text/csv;charset=utf-8\'}); const a = document.createElement(\'a\'); a.href = URL.createObjectURL(blob); a.download = filename; document.body.appendChild(a); a.click(); setTimeout(()=>{URL.revokeObjectURL(a.href); a.remove();}, 1000); }});');

const old2 = '    const [dbc, uc, dl] = await Promise.all(';
if (!s.includes(old2)) throw new Error('old2 not found');
s = s.replace(old2, '    if(!window.claude){ document.documentElement.classList.add(\'standalone\'); }\n    const [dbc, uc, dl] = await Promise.all(');

s = s.replace('    if(!db){ note.textContent = \'Estados en modo local: inicia sesión para ver y guardar los del equipo.\'; return; }', '    if(!db){ note.textContent = window.claude ? \'Estados en modo local: inicia sesión para ver y guardar los del equipo.\' : \'\'; return; }');

s = s.replace('@media (prefers-reduced-motion:reduce)', '.standalone .status-edit{display:none}\n@media (prefers-reduced-motion:reduce)');

const head = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style></head><body>';

fs.writeFileSync('index.html', head + s + '</body></html>', 'utf8');
console.log('build ok: index.html updated');
