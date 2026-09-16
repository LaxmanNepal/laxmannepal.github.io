(()=>{
'use strict';
const boot=()=>{
 if(document.getElementById('ln-clean-style'))return;
 const s=document.createElement('style');s.id='ln-clean-style';s.textContent=`
:root{--clean-accent:#111827;--clean-soft:#f3f4f6;--clean-line:rgba(15,23,42,.10)}
html[data-theme=dark]{--clean-accent:#f8fafc;--clean-soft:#1f2937;--clean-line:rgba(255,255,255,.12)}
.app-card{background:var(--panel,#fff)!important;color:var(--text,#111827)!important;border:1px solid var(--clean-line)!important;box-shadow:0 8px 25px rgba(15,23,42,.07)!important;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease!important}
.app-card:before,.app-card:after{display:none!important}.app-info{background:var(--panel,#fff)!important;color:var(--text,#111827)!important;border-top:1px solid var(--clean-line)!important;box-shadow:none!important}.app-info:before,.app-info:after{display:none!important}
.app-icon{background:var(--clean-soft)!important;border-color:var(--clean-line)!important;color:var(--text)!important;box-shadow:none!important}.app-name{text-shadow:none!important}.app-open{color:var(--muted)!important}.status-dot{background:#22c55e!important}.lnx-meta{color:var(--muted)!important}.lnx-meta .pill,.lnx-source{background:var(--clean-soft)!important;border-color:var(--clean-line)!important;color:var(--text)!important}.lnx-source:hover{background:var(--text)!important;color:var(--panel)!important}
.app-card:hover{transform:translateY(-6px)!important;box-shadow:0 18px 38px rgba(15,23,42,.13)!important;border-color:rgba(15,23,42,.22)!important}
.app-card:hover .app-snapshot{transform:scale(1.035)!important}.app-preview{background:var(--clean-soft)!important}
.app-card:focus-visible{outline:3px solid #94a3b8;outline-offset:3px}
.clean-hover{position:absolute;inset:0;z-index:4;pointer-events:none;background:linear-gradient(180deg,transparent 55%,rgba(15,23,42,.08));opacity:0;transition:opacity .2s}.app-card:hover .clean-hover{opacity:1}
.clean-actions{position:absolute;right:10px;top:10px;z-index:8;display:flex;gap:6px;opacity:0;transform:translateY(-4px);transition:.2s}.app-card:hover .clean-actions,.app-card:focus-within .clean-actions{opacity:1;transform:none}.clean-action{width:32px;height:32px;border:1px solid var(--clean-line);border-radius:10px;background:rgba(255,255,255,.88);color:#111827;display:grid;place-items:center;cursor:pointer;backdrop-filter:blur(10px)}html[data-theme=dark] .clean-action{background:rgba(17,24,39,.88);color:#f8fafc}.clean-action:hover{transform:scale(1.06)}
.app-card .fav-btn{right:10px;top:10px;background:rgba(255,255,255,.88)!important;color:#475569!important;border-color:var(--clean-line)!important;backdrop-filter:blur(10px)}html[data-theme=dark] .app-card .fav-btn{background:rgba(17,24,39,.88)!important;color:#cbd5e1!important}.app-card .fav-btn.active{color:#111827!important}
.clean-tip{font-size:10px;color:var(--muted);margin-top:4px}
@media(max-width:760px){.clean-actions{opacity:1;transform:none}.clean-action{width:29px;height:29px}.app-card:hover{transform:translateY(-3px)!important}}
`;
 document.head.appendChild(s);
 document.querySelectorAll('.app-card').forEach(card=>{
  if(card.querySelector('.clean-hover'))return;
  const shade=document.createElement('span');shade.className='clean-hover';card.querySelector('.app-preview')?.appendChild(shade);
  const actions=document.createElement('div');actions.className='clean-actions';
  const preview=document.createElement('button');preview.className='clean-action';preview.type='button';preview.title='Preview';preview.setAttribute('aria-label','Preview app');preview.innerHTML='<i class="fa-regular fa-eye"></i>';
  const open=document.createElement('a');open.className='clean-action';open.href=card.href;open.target='_blank';open.rel='noopener';open.title='Open app';open.setAttribute('aria-label','Open app');open.innerHTML='<i class="fa-solid fa-arrow-up-right-from-square"></i>';
  preview.onclick=e=>{e.preventDefault();e.stopPropagation();card.dispatchEvent(new MouseEvent('dblclick',{bubbles:true,cancelable:true}))};
  actions.append(preview,open);card.appendChild(actions);
  card.setAttribute('tabindex','0');card.setAttribute('role','link');
  card.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();card.click()}if(e.key===' '){e.preventDefault();card.dispatchEvent(new MouseEvent('dblclick',{bubbles:true,cancelable:true}))}});
 });
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
new MutationObserver(boot).observe(document.documentElement,{childList:true,subtree:true});
})();
