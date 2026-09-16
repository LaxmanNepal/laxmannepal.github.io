(()=>{
'use strict';
const boot=()=>{
 if(document.getElementById('lnx-next-style'))return;
 const style=document.createElement('style');
 style.id='lnx-next-style';
 style.textContent=`
.apps-grid{position:relative;isolation:isolate}
.apps-grid:before,.apps-grid:after{content:"";position:absolute;z-index:-1;border-radius:999px;filter:blur(70px);pointer-events:none;opacity:.24}
.apps-grid:before{width:260px;height:260px;left:-100px;top:8%;background:#8b5cf6}
.apps-grid:after{width:300px;height:300px;right:-110px;bottom:8%;background:#06b6d4}
.app-card{--mx:50%;--my:50%;--glow:rgba(255,255,255,.32);overflow:hidden!important;will-change:transform;backface-visibility:hidden}
.app-card:before{background:radial-gradient(180px 180px at var(--mx) var(--my),rgba(255,255,255,.34),transparent 62%),linear-gradient(145deg,rgba(255,255,255,.32),rgba(255,255,255,0) 43%,rgba(0,0,0,.14))!important;z-index:-1}
.app-card:after{width:220px!important;height:220px!important;right:-100px!important;top:-110px!important;background:radial-gradient(circle,rgba(255,255,255,.28),rgba(255,255,255,0) 68%)!important;transition:transform .45s ease,opacity .3s ease}
.app-card:hover:after{transform:translate(-35px,38px) scale(1.18);opacity:.8}
.app-card .app-snapshot{filter:saturate(1.08) contrast(1.02);transition:opacity .3s ease,transform .55s cubic-bezier(.2,.8,.2,1),filter .3s ease}
.app-card:hover .app-snapshot{filter:saturate(1.18) contrast(1.04);transform:scale(1.055) translate3d(0,-2px,0)!important}
.app-card .app-icon{position:relative;z-index:4;box-shadow:inset 0 1px 0 rgba(255,255,255,.42),0 12px 28px rgba(0,0,0,.18)!important}
.app-card .app-icon:after{content:"";position:absolute;inset:3px;border-radius:14px;border:1px solid rgba(255,255,255,.16);pointer-events:none}
.app-card .app-info{position:relative;overflow:hidden}
.app-card .app-info:before{content:"";position:absolute;inset:-80% -20%;background:linear-gradient(115deg,transparent 38%,rgba(255,255,255,.18) 48%,transparent 58%);transform:translateX(-55%);transition:transform .7s ease;pointer-events:none}
.app-card:hover .app-info:before{transform:translateX(55%)}
.app-card .app-name,.app-card .app-open{position:relative;z-index:1}
@media(max-width:760px){.app-card:hover{transform:translateY(-5px) scale(1.01)!important}.apps-grid:before,.apps-grid:after{filter:blur(55px);opacity:.18}}
@media(prefers-reduced-motion:reduce){.app-card,.app-card:after,.app-card .app-snapshot,.app-card .app-info:before{transition:none!important}.app-card:hover{transform:none!important}}
`;
 document.head.appendChild(style);
 const cards=()=>document.querySelectorAll('.app-card');
 cards().forEach(card=>{
  if(card.dataset.lnxNext)return;
  card.dataset.lnxNext='1';
  card.addEventListener('pointermove',e=>{
   const r=card.getBoundingClientRect();
   card.style.setProperty('--mx',`${((e.clientX-r.left)/r.width)*100}%`);
   card.style.setProperty('--my',`${((e.clientY-r.top)/r.height)*100}%`);
  },{passive:true});
  card.addEventListener('pointerleave',()=>{card.style.setProperty('--mx','50%');card.style.setProperty('--my','50%')},{passive:true});
 });
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
new MutationObserver(boot).observe(document.documentElement,{childList:true,subtree:true});
})();
