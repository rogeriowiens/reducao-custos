/* Service worker — Quiet Ledger PWA
 * Estratégia: app shell em cache, network-first para Firebase (sempre fresh),
 * cache-first para estáticos.
 * Web Share Target: recebe POST /share com arquivo de fatura, guarda no cache
 * e redireciona pra app que detecta na carga e abre o importador.
 */
const VERSION = 'ledger-v2';
const SHARED_CACHE = 'ledger-shared';
const SHELL = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png',
  '/icon-512-maskable.png',
  '/apple-touch-icon.png',
  '/favicon-32.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== VERSION && k !== SHARED_CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);

  // ====== WEB SHARE TARGET ======
  // Recebe POST de "Compartilhar fatura PDF" → guarda no cache → redireciona
  if (req.method === 'POST' && url.pathname === '/share') {
    e.respondWith(handleShare(req));
    return;
  }

  if (req.method !== 'GET') return;

  // Nunca cachear chamadas Firebase
  if (
    url.hostname.includes('firebaseio.com') ||
    url.hostname.includes('googleapis.com') ||
    url.hostname.includes('firebaseapp.com') ||
    url.hostname.includes('identitytoolkit') ||
    url.hostname.includes('google.com')
  ) {
    return;
  }

  // Endpoint interno pra app ler o que foi compartilhado
  if (url.pathname === '/shared/meta.json') {
    e.respondWith(caches.match('shared:meta').then(r => r || new Response('null', { headers: { 'Content-Type': 'application/json' } })));
    return;
  }
  if (url.pathname === '/shared/file') {
    e.respondWith(caches.match('shared:file').then(r => r || new Response('', { status: 404 })));
    return;
  }

  // Cache-first padrão
  e.respondWith(
    caches.match(req).then((cached) => {
      if (cached) {
        fetch(req).then((resp) => {
          if (resp && resp.ok) {
            const copy = resp.clone();
            caches.open(VERSION).then((c) => c.put(req, copy)).catch(() => {});
          }
        }).catch(() => {});
        return cached;
      }
      return fetch(req).then((resp) => {
        if (resp && resp.ok && (url.origin === self.location.origin || url.hostname.endsWith('jsdelivr.net'))) {
          const copy = resp.clone();
          caches.open(VERSION).then((c) => c.put(req, copy)).catch(() => {});
        }
        return resp;
      }).catch(() => {
        if (req.mode === 'navigate') return caches.match('/index.html');
        return new Response('', { status: 504 });
      });
    })
  );
});

async function handleShare(req) {
  try {
    const formData = await req.formData();
    const file = formData.get('file');
    const title = formData.get('title') || '';
    const text = formData.get('text') || '';
    const url = formData.get('url') || '';

    const meta = {
      title: String(title || ''),
      text: String(text || ''),
      url: String(url || ''),
      filename: file && file.name ? file.name : null,
      mime: file && file.type ? file.type : null,
      size: file && file.size ? file.size : 0,
      receivedAt: Date.now()
    };

    const cache = await caches.open(SHARED_CACHE);
    await cache.put('shared:meta', new Response(JSON.stringify(meta), { headers: { 'Content-Type': 'application/json' } }));
    if (file) {
      // Guarda o arquivo como Response
      const blob = new Blob([await file.arrayBuffer()], { type: file.type || 'application/octet-stream' });
      await cache.put('shared:file', new Response(blob, { headers: { 'Content-Type': file.type || 'application/octet-stream', 'X-Filename': encodeURIComponent(file.name || 'fatura') } }));
    } else {
      // Limpa arquivo antigo
      await cache.delete('shared:file');
    }

    // Avisa qualquer aba aberta
    const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    clients.forEach(c => c.postMessage({ type: 'shared-received', meta }));

    // Redireciona pra app com flag
    return Response.redirect('/?shared=1', 303);
  } catch (e) {
    return Response.redirect('/?shared=error', 303);
  }
}

self.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
  if (e.data && e.data.type === 'CLEAR_SHARED') {
    caches.open(SHARED_CACHE).then(c => {
      c.delete('shared:meta');
      c.delete('shared:file');
    });
  }
});
