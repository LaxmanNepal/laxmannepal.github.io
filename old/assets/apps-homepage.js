(() => {
  'use strict';

  const esc = value => String(value ?? '').replace(/[&<>\"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[char]));
  const card = app => `<a class="lnHomeAppCard" href="${esc(app.url)}" data-app-id="${esc(app.id)}"><div class="lnHomeAppIcon">${esc(app.icon || '◉')}</div><div class="lnHomeAppBody"><div class="lnHomeAppTop"><h3>${esc(app.name)}</h3><span class="lnHomeAppBadge">${app.featured ? 'Featured' : esc(app.category || 'App')}</span></div><p>${esc(app.description || 'Explore this app.')}</p><span class="lnHomeAppOpen">Open App ↗</span></div></a>`;

  function styles() {
    if (document.getElementById('lnHomeAppsStyles')) return;
    const s = document.createElement('style');
    s.id = 'lnHomeAppsStyles';
    s.textContent = `
      .lnHomeAppSection{margin:0 0 26px}.lnHomeAppHeading{display:flex;align-items:end;justify-content:space-between;gap:15px;margin:0 0 13px}.lnHomeAppHeading h3{font:700 1.05rem Poppins;margin:0}.lnHomeAppHeading span{font-size:.72rem;color:var(--muted)}
      .lnHomeAppGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px}.lnHomeAppCard{display:flex;gap:14px;min-height:132px;padding:17px;border-radius:22px;background:var(--glass);border:1px solid var(--border);box-shadow:var(--shadow);backdrop-filter:blur(20px);text-decoration:none;color:inherit;transition:.35s var(--ease)}.lnHomeAppCard:hover{transform:translateY(-6px);box-shadow:0 25px 60px rgba(31,38,50,.15)}.lnHomeAppIcon{width:48px;height:48px;min-width:48px;display:grid;place-items:center;border-radius:15px;background:rgba(22,119,255,.1);font-size:23px;border:1px solid var(--border)}.lnHomeAppBody{min-width:0;flex:1}.lnHomeAppTop{display:flex;gap:8px;align-items:center;justify-content:space-between}.lnHomeAppTop h3{margin:0;font:700 .94rem Poppins}.lnHomeAppBadge{font-size:.61rem;padding:4px 7px;border-radius:999px;background:rgba(22,119,255,.1);color:var(--blue);white-space:nowrap}.lnHomeAppBody p{margin:7px 0 11px;color:var(--muted);font-size:.72rem;line-height:1.5}.lnHomeAppOpen{font-size:.68rem;color:var(--blue);font-weight:800}.lnHomeAppEmpty{padding:17px;border:1px dashed #98a2b3;border-radius:18px;color:var(--muted);font-size:.75rem}
      @media(max-width:850px){.lnHomeAppGrid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.lnHomeAppGrid{grid-template-columns:1fr}.lnHomeAppCard{min-height:112px;padding:14px}.lnHomeAppHeading{align-items:center}}
      @media(prefers-reduced-motion:reduce){.lnHomeAppCard{transition:none}}
    `;
    document.head.appendChild(s);
  }

  function recentIds() { try { return JSON.parse(localStorage.getItem('ln:recentApps') || '[]'); } catch { return []; } }
  function saveRecent(id) { try { const ids=[id,...recentIds().filter(x=>x!==id)].slice(0,6); localStorage.setItem('ln:recentApps',JSON.stringify(ids)); return ids; } catch { return []; } }

  function render(container, apps, title, subtitle, items) {
    const section=document.createElement('div'); section.className='lnHomeAppSection';
    section.innerHTML=`<div class="lnHomeAppHeading"><h3>${title}</h3><span>${subtitle}</span></div><div class="lnHomeAppGrid">${items.length ? items.map(card).join('') : '<div class="lnHomeAppEmpty">No recently opened apps yet. Open an app below and it will appear here.</div>'}</div>`;
    container.appendChild(section);
    section.querySelectorAll('.lnHomeAppCard').forEach(a=>a.addEventListener('click',()=>saveRecent(a.dataset.appId)));
  }

  function refresh(container, apps) {
    container.querySelectorAll('.lnHomeAppSection').forEach(x=>x.remove());
    const featured=apps.filter(a=>a.featured).slice(0,3);
    const map=new Map(apps.map(a=>[a.id,a]));
    const recent=recentIds().map(id=>map.get(id)).filter(Boolean).slice(0,3);
    if(featured.length) render(container,apps,'Featured apps','Hand-picked projects',featured);
    if(recent.length) render(container,apps,'Recently opened','On this device',recent);
  }

  async function init(){
    const section=document.getElementById('apps');
    const host=section?.querySelector('.apps');
    if(!section||!host||document.getElementById('lnHomeAppEnhancements')) return;
    styles();
    const marker=document.createElement('div'); marker.id='lnHomeAppEnhancements';
    host.parentNode.insertBefore(marker,host);
    try{
      const r=await fetch(`/data/apps.json?v=${Date.now()}`,{cache:'no-store'}); if(!r.ok) throw new Error(r.status);
      const data=await r.json(); const apps=Array.isArray(data.apps)?data.apps.filter(a=>a.status==='online'):[];
      refresh(marker,apps);
      document.addEventListener('click',event=>{
        const target=event.target.closest?.('.app,.lnAppCard');
        const id=target?.dataset?.appId || target?.getAttribute?.('href') && apps.find(a=>a.url===target.getAttribute('href'))?.id;
        if(id){saveRecent(id);setTimeout(()=>refresh(marker,apps),80);}
      },{passive:true});
    }catch(e){console.warn('[Laxman Nepal] App highlights failed',e);}
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true}); else init();
})();
