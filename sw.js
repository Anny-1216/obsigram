// sw.js — Mi3D Notes Service Worker
// Bump CACHE_VERSION whenever you deploy new files
const CACHE_VERSION = 'mi3d-v2';

const PRECACHE_URLS = [
  'index.html',
  'manifest.json',
  'favicon.ico',
  'https://unpkg.com/three@0.147.0/build/three.min.js',
  'https://unpkg.com/three-spritetext@1.8.1/dist/three-spritetext.min.js',
  'https://unpkg.com/3d-force-graph@1.73.3/dist/3d-force-graph.min.js'
];

// ── Install: pre-cache shell ──────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    }).then(() => self.skipWaiting()) // activate immediately
  );
});

// ── Activate: delete old caches ───────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION)
          .map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim()) // take control of all tabs
  );
});

// ── Fetch: Network-first for navigation, Cache-first for assets ───────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle GET requests on our own origin (+ CDN scripts)
  if (request.method !== 'GET') return;

  // Navigation requests (HTML pages) — network first, fallback to cache
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((c) => c.put(request, clone));
          return response;
        })
        .catch(() => caches.match('/index.html'))
    );
    return;
  }

  // CDN scripts (three.js, 3d-force-graph) — cache first, update in bg
  if (url.hostname !== self.location.hostname) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const networkFetch = fetch(request).then((response) => {
          if (response.ok) {
            caches.open(CACHE_VERSION).then((c) => c.put(request, response.clone()));
          }
          return response;
        });
        return cached || networkFetch;
      })
    );
    return;
  }

  // Local assets — stale-while-revalidate
  event.respondWith(
    caches.open(CACHE_VERSION).then((cache) =>
      cache.match(request).then((cached) => {
        const networkFetch = fetch(request).then((response) => {
          if (response.ok) cache.put(request, response.clone());
          return response;
        }).catch(() => cached); // offline fallback
        return cached || networkFetch;
      })
    )
  );
});
