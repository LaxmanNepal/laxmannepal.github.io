const CACHE='laxman-apps-v30';
const CORE=[
  '/apps/','/apps/index.html','/apps/launcher-ui-v3.css',
  '/apps/interactive-clean.js','/apps/quick-look.js','/apps/launcher.js',
  '/apps/catalog.js','/apps/details/','/apps/details/index.html',
  '/apps/details.css','/apps/details.js','/manifest.webmanifest',
  '/assets/app-icon.svg','/assets/css/style.css','/assets/css/light.css',
  '/assets/css/gadgetbyte-home.css'
];
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await Promise.all(CORE.map(async url => {
      try {
        const response = await fetch(url, { cache: 'no-store' });
        if (response.ok) await cache.put(url, response);
      } catch (_) {}
    }));
    await self.skipWaiting();
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith('laxman-apps-') && key !== CACHE).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  event.respondWith((async () => {
    const cached = await caches.match(event.request);
    try {
      const fresh = await fetch(event.request);
      if (fresh.ok && /\\.(?:webp|css|js|html|webmanifest|svg)$/.test(url.pathname)) {
        const cache = await caches.open(CACHE);
        await cache.put(event.request, fresh.clone());
      }
      return fresh;
    } catch (_) {
      return cached || new Response('Offline', { status: 503 });
    }
  })());
});