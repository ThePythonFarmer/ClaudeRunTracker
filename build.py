"""Wrap src/app.html into a standalone, installable index.html (PWA) for iPhone."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).parent
body = (root / "src/app.html").read_text()

head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Race Spotter">
<meta name="theme-color" content="#0B6A86">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>
"""
tail = """
<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  navigator.serviceWorker.register('sw.js').catch(function(){});
}
</script>
</body>
</html>
"""
# Split the fragment so <title>/<link>/<style> go in <head> and the rest in <body>.
marker = "<header class=\"top\">"
i = body.index(marker)
(root / "index.html").write_text(head + body[:i] + "</head>\n<body>\n" + body[i:] + tail)

(root / "manifest.webmanifest").write_text("""{
  "name": "Riviera Race Spotter",
  "short_name": "Race Spotter",
  "start_url": "./index.html#now",
  "display": "standalone",
  "background_color": "#EEF4F5",
  "theme_color": "#0B6A86",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}
  ]
}
""")

(root / "sw.js").write_text("""const CACHE = 'race-spotter-v1';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // Network first so updates arrive, cache fallback so it works with no signal.
  e.respondWith(fetch(e.request).then(r => {
    const copy = r.clone();
    if (r.ok && new URL(e.request.url).origin === location.origin) caches.open(CACHE).then(c => c.put(e.request, copy));
    return r;
  }).catch(() => caches.match(e.request).then(m => m || caches.match('./index.html'))));
});
""")

def icon(size):
    img = Image.new("RGB", (size, size), "#0B6A86")
    d = ImageDraw.Draw(img)
    s = size / 180
    # sea band, coast line and the runner's sun-coloured dot
    d.rectangle([0, int(118 * s), size, size], fill="#08546B")
    d.line([(int(14*s), int(118*s)), (int(70*s), int(100*s)), (int(110*s), int(112*s)), (int(166*s), int(92*s))], fill="#EEF4F5", width=max(3, int(6*s)))
    r = int(20 * s)
    cx, cy = int(110 * s), int(112 * s)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#E39A12", outline="#EEF4F5", width=max(2, int(5*s)))
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", int(40 * s))
    except OSError:
        f = ImageFont.load_default()
    d.text((int(18*s), int(26*s)), "42.2", font=f, fill="#EEF4F5")
    img.save(root / f"icon-{size}.png")

for n in (180, 192, 512):
    icon(n)
print("built index.html, manifest, sw.js, icons")
