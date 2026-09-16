const CACHE='laxman-apps-v13';
const CORE=['/apps/','/apps/mobile-parity.css','/apps/interactive-clean.js','/apps/quick-look.js','/apps/catalog-fallback.js','/apps/launcher-enhancements.js','/apps/launcher-next.js','/apps/launcher-cards.js','/apps/launcher-identity.js','/apps/launcher-metadata.js','/apps/launcher-details.js','/manifest.webmanifest','/assets/app-icon.svg','/assets/css/style.css','/assets/css/light.css','/assets/css/gadgetbyte-home.css'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(async c=>{await Promise.all(CORE.map(async u=>{try{const r=await fetch(u,{cache:'no-store'});if(r.ok)await c.put(u,r)}catch{}})}).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('laxman-apps-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET')return;
 const u=new URL(e.request.url);if(u.origin!==location.origin)return;
 e.respondWith((async()=>{
   const cached=await caches.match(e.request);
   try{
     const fresh=await fetch(e.request);
     if(fresh.ok&&(/\.webp$|\.css$|\.js$|\.html$|\.webmanifest$|\.svg$/.test(u.pathname)||u.pathname==='/apps/'||u.pathname==='/apps/index.html'))){
       caches.open(CACHE).then(c=>c.put(e.request,fresh.clone()));
     }
     return fresh;
   }catch{return cached||new Response('Offline',{status:503})}
 })());
});
