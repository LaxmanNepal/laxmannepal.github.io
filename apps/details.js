(()=>{'use strict';
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slug=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const catalog=Array.isArray(window.LAXMAN_APP_CATALOG)?window.LAXMAN_APP_CATALOG.map(a=>({...a,url:new URL(a.url,location.origin).href,slug:slug(a.name)})):[];
const key=new URLSearchParams(location.search).get('app')||'';
const app=catalog.find(a=>a.slug===key);
if(!app){$('#detail-state').innerHTML='<strong>App not found.</strong><p>Choose an app from the main directory.</p><a class="detail-btn primary" href="/apps/">Browse all apps</a>';}
else{
 document.title=app.name+' — App details | Laxman Nepal';
 $('meta[name="description"]').content=app.description+' Explore features and open the official app from Laxman Nepal.';
 $('#detail-state').hidden=true;
 const image='/assets/app-snapshots/'+app.slug+'.webp';
 $('#app-detail').hidden=false;
 $('#app-detail').innerHTML='<section class="detail-hero"><div><div class="detail-eyebrow">Laxman Nepal Apps Directory</div><h1 class="detail-title">'+esc(app.name)+'</h1><p class="detail-description">'+esc(app.description||'Explore this app from the Laxman Nepal digital collection.')+'</p><div class="detail-domain">'+esc(new URL(app.url).hostname)+'</div><div class="detail-actions"><a class="detail-btn primary" href="'+esc(app.url)+'" target="_blank" rel="noopener noreferrer">Open app ↗</a><a class="detail-btn" href="'+esc(app.url)+'" target="_blank" rel="noopener noreferrer">Visit website</a><a class="detail-btn" href="/apps/">← All apps</a></div><div class="detail-meta"><span class="detail-pill">Web app</span><span class="detail-pill">External website</span><span class="detail-pill">Free to explore</span></div><p class="detail-notice">You are leaving Laxman Nepal when opening this app. Availability, features and privacy practices are controlled by the destination website.</p></div><div class="detail-preview"><img src="'+esc(image)+'" alt="'+esc(app.name)+' preview" onerror="this.remove();this.parentElement.innerHTML=\'<div class=&quot;preview-placeholder&quot;><strong>'+esc(app.name)+'</strong><p>Preview image is not available yet.</p></div>\'"></div></section>';
 const others=catalog.filter(a=>a.slug!==app.slug).slice(0,6);
 $('#related-apps').innerHTML=others.map(a=>'<a class="related-card" href="/apps/details/?app='+encodeURIComponent(a.slug)+'"><span class="related-icon">✦</span><span><strong>'+esc(a.name)+'</strong><small>'+esc(a.description)+'</small></span></a>').join('');
}
})();