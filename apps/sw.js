const CACHE='laxman-apps-v18';
const CORE=['/apps/','/apps/mobile-parity.css','/apps/launcher-ui-v1.css','/apps/launcher-ui-v2.css','/apps/launcher-ui-v5.css','/apps/launcher-ui-v4.css','/apps/launcher-ui-v3.css','/apps/interactive-clean.js','/apps/quick-look.js','/apps/launcher-enhancements.js','/apps/launcher-next.js','/apps/launcher-cards.js','/apps/launcher-identity.js','/apps/launcher-metadata.js','/apps/launcher-details.js','/manifest.webmanifest','/assets/app-icon.svg','/assets/css/style.css','/assets/css/light.css','/assets/css/gadgetbyte-home.css'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(async c=>{await Promise.all(CORE.map(async u=>{try{const r=await fetch(u,{cache:'no-store'});if(r.ok)await c.put(u,r)}catch{}})}).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('laxman-apps-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
async function inject(response){
 if(!response||!response.ok)return response;
 try{
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html'))return response;
  const text=await response.text();let injected=text;
  const styles=['mobile-parity.css?v=17'];
  styles.forEach(href=>{const path='/apps/'+href.split('?')[0];if(!injected.includes(path))injected=injected.replace('</head>','<link rel="stylesheet" href="/apps/'+href+'"></head>')});
  /* Launcher behavior is owned by launcher.js; avoid legacy script injection here. */
  const headers=new Headers(response.headers);headers.delete('content-length');
  return new Response(injected,{status:response.status,statusText:response.statusText,headers});
 }catch{return response}
}
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET')return;
 const u=new URL(e.request.url);if(u.origin!==location.origin)return;
 e.respondWith((async()=>{
   const cached=await caches.match(e.request);
   try{
     const fresh=await fetch(e.request);
     if(u.pathname==='/apps/'||u.pathname==='/apps/index.html'){
       const enhanced=await inject(fresh);
       caches.open(CACHE).then(c=>c.put(e.request,enhanced.clone()));
       return enhanced;
     }
     if(fresh.ok&&/\.webp$|\.css$|\.js$|\.html$|\.webmanifest$|\.svg$/.test(u.pathname))caches.open(CACHE).then(c=>c.put(e.request,fresh.clone()));
     return fresh;
   }catch{return cached||new Response('Offline',{status:503})}
 })());
});
