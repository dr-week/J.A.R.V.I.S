// Basic Service Worker for PWA installability
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Let the browser handle fetches natively (no offline cache by default)
  // But registering a fetch handler is required by some browsers to qualify as a PWA
});
