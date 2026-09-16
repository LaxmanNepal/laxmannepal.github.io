(()=>{
'use strict';
const boot=()=>{
 if(document.getElementById('lnx-identity-style'))return;
 const s=document.createElement('style');s.id='lnx-identity-style';s.textContent=`
.app-card .lnx-domain{position:absolute;left:12px;top:38px;z-index:4;max-width:calc(100% - 24px);padding:4px 7px;border:1px solid rgba(255,255,255,.35);border-radius:999px;background:rgba(15,23,42,.3);color:#fff;font-size:8px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;backdrop-filter:blur(9px);text-shadow:0 1px 2px rgba(0,0,0,.2)}
.app-card .lnx-live{position:absolute;right:11px;top:42px;z-index:4;display:inline-flex;align-items:center;gap:4px;padding:4px 7px;border-radius:999px;background:rgba(15,23,42,.3);border:1px solid rgba(255,255,255,.3);color:#fff;font-size:8px;font-weight:900;backdrop-filter:blur(9px)}
.app-card .lnx-live i{width:5px;height:5px;border-radius:50%;background:#fbbf24;box-shadow:0 0 7px currentColor}.app-card .lnx-live.ok i{background:#4ade80}.app-card .lnx-live.bad i{background:#fb7185}
.app-card .app-icon img{position:relative;z-index:3;display:block!important}.app-card .app-icon i{z-index:2}
`;
 document.head.appendChild(s);
 document.querySelectorAll('.app-card').forEach(card=>{
  if(card.dataset.identity)return;card.dataset.identity='1';
  let host='App';try{host=new URL(card.href).hostname.replace(/^www\./,'')}catch{}
  const domain=document.createElement('span');domain.className='lnx-domain';domain.textContent=host;card.appendChild(domain);
  const live=document.createElement('span');live.className='lnx-live';live.innerHTML='<i></i><span>Checking</span>';card.appendChild(live);
  const icon=card.querySelector('.app-icon');
  if(icon&&host){const img=document.createElement('img');img.src='https://www.google.com/s2/favicons?domain='+encodeURIComponent(host)+'&sz=128';img.alt='';img.loading='lazy';img.referrerPolicy='no-referrer';img.onerror=()=>img.remove();icon.prepend(img)}
  fetch(card.href,{method:'HEAD',mode:'no-cors',cache:'no-store'}).then(()=>{live.classList.add('ok');live.querySelector('span').textContent='Live'}).catch(()=>{live.classList.add('bad');live.querySelector('span').textContent='Check'})
 });
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
new MutationObserver(boot).observe(document.documentElement,{childList:true,subtree:true});
})();
