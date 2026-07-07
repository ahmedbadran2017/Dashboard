// Justyol Ops Dashboard — service worker.
//
// Strategy:
//   • App shell (the built JS/CSS bundle + host page) → stale-while-revalidate,
//     so the PWA opens instantly offline and updates in the background.
//   • API calls (/api/method/...) → network-first with a short cache fallback,
//     so a flaky connection still shows the last known numbers (clearly stale).
//   • Everything else → network, falling back to cache.
// Served from the SITE ROOT (Frappe www/ → /sw.js) so it can legally claim the
// /ops/ scope. A worker served from /assets/... cannot control /ops/ without a
// Service-Worker-Allowed header Frappe does not send, so registration would fail.
const VERSION = "ops-v2";
const SHELL_CACHE = `${VERSION}-shell`;
const API_CACHE = `${VERSION}-api`;

const SHELL_ASSETS = [
  "/ops/home",
  "/assets/ops_dashboard/ops_dashboard.bundle.js",
  "/assets/ops_dashboard/ops_dashboard.bundle.css",
  "/assets/ops_dashboard/manifest.webmanifest",
  "/assets/ops_dashboard/icons/icon-192.png",
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(SHELL_CACHE).then((c) => Promise.allSettled(SHELL_ASSETS.map((u) => c.add(u))))
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => !k.startsWith(VERSION)).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);

  // API: network-first, cache fallback.
  if (url.pathname.startsWith("/api/method/")) {
    event.respondWith(
      fetch(request)
        .then((res) => {
          const copy = res.clone();
          caches.open(API_CACHE).then((c) => c.put(request, copy));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Shell + assets: stale-while-revalidate.
  if (url.pathname.startsWith("/assets/ops_dashboard/") || url.pathname.startsWith("/ops/")) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const network = fetch(request)
          .then((res) => {
            const copy = res.clone();
            caches.open(SHELL_CACHE).then((c) => c.put(request, copy));
            return res;
          })
          .catch(() => cached);
        return cached || network;
      })
    );
  }
});
