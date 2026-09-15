const CACHE='laxman-apps-v1';
const CORE=['/apps/','/manifest.webmanifest','/assets/app-icon.svg','/assets/css/style.css','/assets/css/light.css','/assets/css/gadgetbyte-home.css'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==location.origin)return;e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{if(r.ok&&/\.webp$|\.css$|\.js$|\.html$|\.webmanifest$|\.svg$/.test(u.pathname)){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return r}).catch(()=>cached)))});
