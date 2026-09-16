const CACHE='laxman-apps-v8';
const CORE=['/apps/','/apps/mobile-parity.css','/apps/launcher-enhancements.js','/apps/launcher-next.js','/apps/launcher-cards.js','/apps/launcher-identity.js','/apps/launcher-metadata.js','/manifest.webmanifest','/assets/app-icon.svg','/assets/css/style.css','/assets/css/light.css','/assets/css/gadgetbyte-home.css'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('laxman-apps-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
async function inject(response){
 if(!response||!response.ok)return response;
 try{
  const type=response.headers.get('content-type')||'';if(!type.includes('text/html'))return response;
  const text=await response.text();let injected=text;
  const styles=['mobile-parity.css?v=8'];
  styles.forEach(href=>{const path='/apps/'+href.split('?')[0];if(!injected.includes(path))injected=injected.replace('</head>','<link rel="stylesheet" href="/apps/'+href+'"></head>')});
  const scripts=['launcher-enhancements.js?v=8','launcher-next.js?v=8','launcher-cards.js?v=8','launcher-identity.js?v=8','launcher-metadata.js?v=8'];
  scripts.forEach(src=>{const path='/apps/'+src.split('?')[0];if(!injected.includes(path))injected=injected.replace('</body>','<script src="/apps/'+src+'" defer></script></body>')});
  const headers=new Headers(response.headers);headers.delete('content-length');
  return new Response(injected,{status:response.status,statusText:response.statusText,headers});
 }catch{return response}
}
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==location.origin)return;
 e.respondWith((async()=>{const cached=await caches.match(e.request);try{const fresh=await fetch(e.request);if(u.pathname==='/apps/'){const enhanced=await inject(fresh);caches.open(CACHE).then(c=>c.put(e.request,enhanced.clone()));return enhanced}if(fresh.ok&&/\.webp$|\.css$|\.js$|\.html$|\.webmanifest$|\.svg$/.test(u.pathname))caches.open(CACHE).then(c=>c.put(e.request,fresh.clone()));return fresh}catch{return cached||new Response('Offline',{status:503})}})())
});
