'use strict';

const CACHE_NAME = 'ln-nepali-typing-v8';
const PRECACHE_URLS = [
  './',
  './index.html',
  './style.css',
  './editor-range.js?v=20261025-2',
  './engines/romanized.js?v=20261025-2',
  './engines/typing-lexicon.js?v=20261025-1',
  './engines/smart-typing.js?v=20261025-1',
  './app.js?v=20261025-9',
  './workspace-tools.js?v=20261025-4',
  './pwa.js?v=20261025-1',
  './manifest.webmanifest',
  '/assets/css/style.css',
  '/assets/css/blog.css',
  '/assets/css/shared-shell.css',
  '/assets/js/shared-shell.js',
  '/assets/app-icon.svg'
];

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(PRECACHE_URLS);
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith('ln-nepali-typing-') && name !== CACHE_NAME).map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  // Never cache remote suggestions, speech, or other third-party requests.
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (response && response.ok) {
          const cache = await caches.open(CACHE_NAME);
          await cache.put(request, response.clone());
        }
        return response;
      } catch (_) {
        return (await caches.match(request)) ||
          (await caches.match('./index.html')) ||
          (await caches.match('./')) ||
          Response.error();
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;
    try {
      const response = await fetch(request);
      if (response && response.ok) {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, response.clone());
      }
      return response;
    } catch (_) {
      return Response.error();
    }
  })());
});
