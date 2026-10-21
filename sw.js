// Cache para abrir rápido e funcionar sem internet com a última versão vista.
// Página e dados: rede primeiro (preço sempre atualizado). Fotos e fontes: cache primeiro.
const VERSAO = "egua-v2";
const BASE = ["./", "index.html", "js/config.js", "data/produtos.json", "manifest.webmanifest", "img/marca/logo-horizontal.jpg", "img/marca/icone-192.png"];

self.addEventListener("install", e => { e.waitUntil(caches.open(VERSAO).then(c => c.addAll(BASE))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const estatico = /\.(jpg|png|webp|woff2?)$/.test(url.pathname) || url.host.includes("fonts.g");
  if (estatico) {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
      if (res.ok || res.type === "opaque") { const cp = res.clone(); caches.open(VERSAO).then(c => c.put(req, cp)); }
      return res;
    })));
  } else if (url.origin === location.origin) {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) { const cp = res.clone(); caches.open(VERSAO).then(c => c.put(req, cp)); }
      return res;
    }).catch(() => caches.match(req)));
  }
});
