// Guarda la app en el celular para que abra sin internet.
// Al publicar cambios, suba el número de VERSION para que se actualice.
const VERSION = "sape-movil-v10";
const ARCHIVOS = [
  "./", "index.html", "estilos.css", "datos.js", "fp.js", "ttr.js", "diagramas.js", "diagramasFp.js",
  "diagramasAnexoA.js", "cfe3d.js", "app.js",
  "manifest.webmanifest", "icono-192.png", "icono-512.png", "icono-180.png",
];

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    caches.open(VERSION).then((cache) => cache.addAll(ARCHIVOS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches.keys()
      .then((claves) => Promise.all(claves.filter((c) => c !== VERSION).map((c) => caches.delete(c))))
      .then(() => self.clients.claim())
  );
});

// Primero la red (para recibir versiones nuevas); sin conexión, la copia guardada.
self.addEventListener("fetch", (evento) => {
  if (evento.request.method !== "GET") return;
  evento.respondWith(
    fetch(evento.request)
      .then((respuesta) => {
        const copia = respuesta.clone();
        caches.open(VERSION).then((cache) => cache.put(evento.request, copia));
        return respuesta;
      })
      .catch(() => caches.match(evento.request, { ignoreSearch: true }).then((r) => r || caches.match("index.html")))
  );
});
