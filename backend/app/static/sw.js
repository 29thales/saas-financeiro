self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// Passa todas as requisições direto pra rede, sem cache.
// Isso garante que os dados financeiros sempre venham atualizados do servidor.
self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request));
});
