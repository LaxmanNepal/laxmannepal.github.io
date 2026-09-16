(()=>{
'use strict';
const boot=()=>{
 if(document.getElementById('lnx-card-style'))return;
 const s=document.createElement('style');s.id='lnx-card-style';s.textContent=`
.app-card{padding:0!important;justify-content:flex-end!important;border-radius:24px!important}
.app-card .app-snapshot{position:absolute!important;inset:0 0 30%!important;width:100%!important;height:70%!important;opacity:1!important;z-index:0!important;object-fit:cover!important;mix-blend-mode:normal!important;background:#eef2ff}
.app-card .app-snapshot:before{content:""}
.app-card .app-icon{position:absolute!important;left:16px;bottom:calc(30% - 29px);z-index:5!important;width:58px;height:58px}
.app-card .app-info{position:absolute!important;left:0;right:0;bottom:0;height:30%;min-height:82px;margin:0!important;padding:40px 14px 12px!important;display:flex;flex-direction:column;justify-content:flex-end;align-items:flex-start!important;text-align:left!important;background:linear-gradient(145deg,var(--c1),var(--c2) 55%,var(--c3))!important}
.app-card .app-name{width:100%;padding-right:4px;font-size:15px!important}
.app-card .app-open{justify-content:flex-start!important;margin-top:5px!important;font-size:10px!important}
.app-card .app-info:after{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:rgba(255,255,255,.34)}
.app-card .lnx-browser{position:absolute;left:9px;right:9px;top:9px;height:22px;border-radius:9px;background:rgba(255,255,255,.78);backdrop-filter:blur(10px);z-index:3;display:flex;align-items:center;padding:0 8px;gap:4px;box-shadow:0 3px 12px rgba(15,23,42,.12)}
.app-card .lnx-browser i{width:6px;height:6px;border-radius:50%;background:rgba(15,23,42,.28);display:block}
.app-card .lnx-browser span{height:5px;flex:1;max-width:70px;margin-left:5px;border-radius:99px;background:rgba(15,23,42,.12)}
.app-card .lnx-badge{position:absolute;right:13px;bottom:13px;z-index:6;padding:5px 8px;border:1px solid rgba(255,255,255,.28);border-radius:999px;background:rgba(255,255,255,.16);color:#fff;font-size:9px;font-weight:900;backdrop-filter:blur(8px)}
@media(max-width:460px){.app-card{border-radius:18px!important}.app-card .app-info{min-height:72px;padding:34px 10px 9px!important}.app-card .app-icon{left:10px}.app-card .lnx-browser{left:7px;right:7px;top:7px}}
`;
 document.head.appendChild(s);
 document.querySelectorAll('.app-card').forEach((c,i)=>{
  if(c.dataset.cardUpgrade)return;c.dataset.cardUpgrade='1';
  const bar=document.createElement('span');bar.className='lnx-browser';bar.setAttribute('aria-hidden','true');bar.innerHTML='<i></i><i></i><i></i><span></span>';c.appendChild(bar);
  const badge=document.createElement('span');badge.className='lnx-badge';badge.textContent='OPEN ↗';c.appendChild(badge);
 });
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
new MutationObserver(boot).observe(document.documentElement,{childList:true,subtree:true});
})();
