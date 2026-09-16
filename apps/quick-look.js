(()=>{
'use strict';
const boot=()=>{
 if(document.getElementById('ln-quick-look'))return;
 const style=document.createElement('style');style.id='ln-quick-look';style.textContent=`
#ln-quick-panel{position:fixed;right:22px;bottom:22px;width:min(390px,calc(100vw - 32px));z-index:9999;background:var(--panel,#fff);color:var(--text,#111827);border:1px solid rgba(15,23,42,.12);border-radius:22px;box-shadow:0 24px 70px rgba(15,23,42,.22);overflow:hidden;opacity:0;transform:translateY(18px) scale(.97);pointer-events:none;transition:.22s ease}
#ln-quick-panel.open{opacity:1;transform:none;pointer-events:auto}
#ln-quick-head{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid rgba(15,23,42,.08)}
#ln-quick-head img{width:34px;height:34px;border-radius:9px;object-fit:cover;background:#f3f4f6}.ln-ql-title{min-width:0;flex:1}.ln-ql-title strong{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ln-ql-title small{color:var(--muted,#64748b)}
.ln-ql-close{width:30px;height:30px;border:0;border-radius:9px;background:var(--soft,#f3f4f6);color:inherit;cursor:pointer}.ln-ql-shot{height:205px;background:#eef1f5}.ln-ql-shot img{width:100%;height:100%;object-fit:cover;object-position:top}.ln-ql-body{padding:14px}.ln-ql-meta{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}.ln-ql-pill{padding:5px 8px;border-radius:999px;background:var(--soft,#f3f4f6);font-size:11px}.ln-ql-actions{display:flex;gap:8px}.ln-ql-actions a,.ln-ql-actions button{flex:1;border:1px solid rgba(15,23,42,.1);border-radius:11px;padding:9px 10px;text-align:center;text-decoration:none;cursor:pointer;background:var(--soft,#f3f4f6);color:inherit;font:inherit}.ln-ql-actions a.primary{background:var(--text,#111827);color:var(--panel,#fff);border-color:transparent}
@media(max-width:600px){#ln-quick-panel{right:12px;bottom:12px;width:calc(100vw - 24px)}.ln-ql-shot{height:180px}}
`;
 document.head.appendChild(style);
 const panel=document.createElement('aside');panel.id='ln-quick-panel';panel.setAttribute('aria-label','Quick Look preview');panel.innerHTML=`<div id="ln-quick-head"><img id="ln-ql-icon" alt=""><div class="ln-ql-title"><strong id="ln-ql-name"></strong><small id="ln-ql-category"></small></div><button class="ln-ql-close" type="button" aria-label="Close">×</button></div><div class="ln-ql-shot"><img id="ln-ql-shot" alt=""></div><div class="ln-ql-body"><div class="ln-ql-meta" id="ln-ql-meta"></div><div class="ln-ql-actions"><button type="button" id="ln-ql-fav">☆ Favorite</button><a id="ln-ql-source" target="_blank" rel="noopener">GitHub</a><a id="ln-ql-open" class="primary" target="_blank" rel="noopener">Open App ↗</a></div></div>`;
 document.body.appendChild(panel);
 const close=()=>panel.classList.remove('open');panel.querySelector('.ln-ql-close').onclick=close;
 document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
 const show=card=>{
  const name=card.querySelector('.app-name')?.textContent?.trim()||'App';
  const img=card.querySelector('.app-snapshot')?.src||card.querySelector('.app-icon img')?.src||'';
  const icon=card.querySelector('.app-icon img')?.src||'';
  const cat=card.querySelector('.category-badge')?.textContent?.trim()||card.dataset.category||'App';
  const href=card.href||card.querySelector('a')?.href||'#';
  document.getElementById('ln-ql-name').textContent=name;document.getElementById('ln-ql-category').textContent=cat;
  document.getElementById('ln-ql-shot').src=img;document.getElementById('ln-ql-icon').src=icon;
  document.getElementById('ln-ql-open').href=href;
  const source=card.querySelector('.lnx-source')?.href||'';const sb=document.getElementById('ln-ql-source');sb.href=source||('https://github.com/LaxmanNepal/'+encodeURIComponent(name));
  const meta=document.getElementById('ln-ql-meta');meta.innerHTML='';
  [...card.querySelectorAll('.lnx-meta .pill,.status-dot')].slice(0,4).forEach(el=>{const p=document.createElement('span');p.className='ln-ql-pill';p.textContent=el.textContent?.trim()||'Live';if(p.textContent)meta.appendChild(p)});
  const fav=card.querySelector('.fav-btn');const fb=document.getElementById('ln-ql-fav');fb.textContent=fav?.classList.contains('active')?'★ Favorited':'☆ Favorite';fb.onclick=()=>{fav?.click();setTimeout(()=>fb.textContent=fav?.classList.contains('active')?'★ Favorited':'☆ Favorite',30)};
  panel.classList.add('open');
 };
 document.addEventListener('click',e=>{const card=e.target.closest?.('.app-card');if(!card||e.target.closest('.clean-actions,.fav-btn'))return; if(e.ctrlKey||e.metaKey)return; e.preventDefault();show(card)});
 document.addEventListener('dblclick',e=>{if(e.target.closest?.('#ln-quick-panel'))return;const card=e.target.closest?.('.app-card');if(card){e.preventDefault();window.open(card.href,'_blank','noopener')}});
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
