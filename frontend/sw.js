// Desi Card Games - Service Worker (PWA)
const CACHE_NAME = "desi-games-v1.1.3";

const PRECACHE_ASSETS = [
    "./",
    "index.html",
    "style.css",
    "config.js",
    "cards.js",
    "audio.js",
    "i18n.js",
    "rules.js",
    "app.js",
    "pwa.js",
    "manifest.webmanifest",
    "favicon.svg",
    "icons/icon-192.png",
    "icons/icon-512.png",
    "cards/BLUE_BACK.svg",
    "assets/cards/kathputli-puppet.svg",
    "assets/cards/royal-raja.svg",
    "assets/cards/royal-rani.svg",
    "assets/cards/royal-camel.svg",
    "assets/cards/royal-elephant.svg",
    "assets/cards/jharokha-watermark.svg",
    "assets/cards/bandhani-back.svg"
];

// Install: pre-cache critical app shell
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(PRECACHE_ASSETS).catch((err) => {
                console.warn("SW precache partial failure (non-critical):", err);
            });
        }).then(() => self.skipWaiting())
    );
});

// Activate: clean up old cache versions
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch: Network-first for APIs, Cache-first for static assets
self.addEventListener("fetch", (event) => {
    const request = event.request;
    const url = new URL(request.url);

    // 1. Never cache API endpoints, backend requests, or non-GET requests
    if (request.method !== "GET" || url.pathname.startsWith("/api/") || url.pathname === "/health" || url.pathname === "/docs" || url.pathname === "/openapi.json") {
        return; // Normal browser fetch pass-through
    }

    // 2. Cache-first strategy for static assets (cards, scripts, styles, images)
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
                // Return cached version, and optionally refresh cache in background
                fetch(request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then((cache) => cache.put(request, networkResponse));
                    }
                }).catch(() => {});
                return cachedResponse;
            }

            // Otherwise fetch from network and cache
            return fetch(request).then((networkResponse) => {
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== "basic") {
                    return networkResponse;
                }
                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(request, responseToCache);
                });
                return networkResponse;
            }).catch(() => {
                // If offline and requesting an HTML page, return index.html
                if (request.headers.get("accept") && request.headers.get("accept").includes("text/html")) {
                    return caches.match("index.html");
                }
            });
        })
    );
});
