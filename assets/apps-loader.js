(() => {
  'use strict';

  const FALLBACK = {
    version: 2,
    updatedAt: '2026-08-30T00:00:00Z',
    apps: [
      {id:'nisulka-tools',name:'Nisulka Tools',description:'Free browser-based tools for everyday productivity and creators.',category:'Tools',url:'https://apps.laxmannepal.com.np/Nisulka-Tools/',icon:'🛠️',featured:true,keywords:['tools','productivity','creator']},
      {id:'nepali-patro',name:'Nepali Patro',description:'Nepali calendar and useful Nepali date, festival and cultural information.',category:'Nepal',url:'https://apps.laxmannepal.com.np/Nepali-Patro/',icon:'📅',featured:true,keywords:['nepali calendar','patro','date','festival']},
      {id:'nepse',name:'NEPSE',description:'Nepal stock-market focused tools and company information.',category:'Finance',url:'https://apps.laxmannepal.com.np/NEPSE/',icon:'📈',featured:true,keywords:['nepse','shares','stocks','finance']},
      {id:'live-tv',name:'Live TV',description:'A web interface for discovering available live television streams.',category:'Media',url:'https://apps.laxmannepal.com.np/Live-TV/',icon:'📺',featured:false,keywords:['tv','live tv','television']},
      {id:'nepali-movies',name:'Nepali Movies',description:'A Nepali cinema discovery project.',category:'Media',url:'https://apps.laxmannepal.com.np/Nepali-Movies/',icon:'🎬',featured:false,keywords:['nepali movies','cinema','films']},
      {id:'south-movies',name:'South Movies',description:'South Indian movie discovery and streaming information.',category:'Media',url:'https://apps.laxmannepal.com.np/South-Movies/',icon:'🎞️',featured:false,keywords:['south movies','movies','cinema']},
      {id:'hindu',name:'Hindu',description:'A searchable collection of Hindu scriptures, texts and related information.',category:'Culture',url:'https://apps.laxmannepal.com.np/Hindu/',icon:'🕉️',featured:false,keywords:['hindu','grantha','scriptures','purana']}
    ]
  };

  function baseCandidates() {
    const p = location.pathname.replace(/\\/g, '/');
    const clean = p.endsWith('/') ? p : p + '/';
    const root = clean.split('/').filter(Boolean)[0];
    const candidates = [
      new URL('data/apps.json', location.origin + '/').href,
      new URL('../data/apps.json', location.href).href,
      new URL('./data/apps.json', location.href).href
    ];
    if (root) candidates.push(new URL('/' + root + '/data/apps.json', location.origin).href);
    return [...new Set(candidates)];
  }

  function valid(data) {
    return data && Array.isArray(data.apps) && data.apps.length > 0 && data.apps.every(a => a && a.id && a.name && a.url);
  }

  async function load() {
    for (const url of baseCandidates()) {
      try {
        const r = await fetch(url + (url.includes('?') ? '&' : '?') + 'v=' + Date.now(), {cache:'no-store',headers:{Accept:'application/json'}});
        if (!r.ok) continue;
        const data = await r.json();
        if (valid(data)) return data;
      } catch (_) {}
    }
    try {
      const cached = JSON.parse(localStorage.getItem('laxman-apps-cache') || 'null');
      if (valid(cached)) return cached;
    } catch (_) {}
    return FALLBACK;
  }

  window.LaxmanApps = { load, FALLBACK };
})();
