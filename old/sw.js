const CACHE='ln-home-v3';
const CORE=['/','/index.html','/manifest.webmanifest','/assets/site-enhancements.js','/assets/apps-homepage.js','/assets/site-intelligence.js'];
const DATA_PREFIX='/data/';
const CACHEABLE_DESTINATIONS=new Set(['style','script','font','image']);

self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting()));
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(key=>key.startsWith('ln-home-')&&key!==CACHE).map(key=>caches.delete(key))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET') return;
  const url=new URL(event.request.url);
  if(url.origin!==self.location.origin) return;

  if(url.pathname.startsWith(DATA_PREFIX)){
    const stableRequest=new Request(url.origin+url.pathname,{method:'GET'});
    event.respondWith(
      fetch(event.request).then(response=>{
        if(response.ok){
          const copy=response.clone();
          caches.open(CACHE).then(cache=>cache.put(stableRequest,copy));
        }
        return response;
      }).catch(()=>caches.match(stableRequest))
    );
    return;
  }

  if(event.request.mode==='navigate'){
    event.respondWith(
      fetch(event.request).then(response=>{
        if(response.ok){
          const copy=response.clone();
          caches.open(CACHE).then(cache=>cache.put('/',copy));
        }
        return response;
      }).catch(()=>caches.match('/').then(response=>response||caches.match('/index.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cached=>cached||fetch(event.request).then(response=>{
      if(response.ok && CACHEABLE_DESTINATIONS.has(event.request.destination)){
        const copy=response.clone();
        caches.open(CACHE).then(cache=>cache.put(event.request,copy));
      }
      return response;
    }))
  );
});
