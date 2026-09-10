/* Shared app-directory visual helpers. No external API calls are required. */
window.LaxmanAppVisuals=(()=>{
  'use strict';
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const favicon=a=>{
    if(a&&a.iconUrl) return String(a.iconUrl);
    try{return new URL(a.url).origin+'/favicon.ico'}catch(e){return ''}
  };
  const markup=(a,cls='app-logo',size='56')=>{
    const src=favicon(a);
    const fallback=esc(a&&a.icon||'📱');
    if(!src)return '<span class="'+cls+' fallback" aria-hidden="true">'+fallback+'</span>';
    return '<span class="'+cls+'" aria-hidden="true"><img src="'+esc(src)+'" alt="" width="'+size+'" height="'+size+'" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.hidden=true;this.nextElementSibling.hidden=false"><span class="fallback" hidden>'+fallback+'</span></span>';
  };
  return {favicon,markup};
})();
