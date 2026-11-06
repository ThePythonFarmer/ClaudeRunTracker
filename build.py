"""Fill course data + Leaflet CSS into src/app.html (the page published as an Artifact),
then wrap it into a standalone, installable index.html (PWA) for iPhone."""
import json, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).parent
SPOT_META = [  # id, name, town, station, note
 ("start", "Start · Promenade des Anglais", "Nice", "nice", "By the Théâtre de Verdure. Handisport 07:57, elites 08:00, main field 08:03. Stand west of the start pens."),
 ("magnan", "Promenade · Magnan", "Nice", "nice", "A long walk from Nice Ville; tram line 2 gets you closer."),
 ("airport", "Promenade · airport", "Nice", "staug", "Wide promenade beside the airport, easy viewing."),
 ("stlaurent", "Saint-Laurent seafront", "Saint-Laurent-du-Var", "stl", "Just after the Var bridge, by Cap 3000."),
 ("cros", "Cros-de-Cagnes seafront", "Cagnes-sur-Mer", "cros", "Old fishing-village seafront, short walk from the station."),
 ("plage", "Cagnes seafront · Hippodrome", "Cagnes-sur-Mer", "cagnes", "Long straight; you can see runners coming from far off."),
 ("baie", "Marina Baie des Anges", "Villeneuve-Loubet", "vlp", "The 20 km race finishes nearby, so expect crowds."),
 ("biot", "La Brague · Biot", "Biot", "biot", "Quieter stretch, good for a clear shout."),
 ("fort", "Fort Carré · halfway", "Antibes", "antibes", "Duo relay changeover. Busy and loud."),
 ("port", "Port Vauban", "Antibes", "antibes", "Last easy spot before the Cap d’Antibes loop."),
 ("salis", "Plage de la Salis", "Cap d’Antibes", "antibes", "Start of the Cap loop; the climb to La Garoupe follows."),
 ("juan", "Juan-les-Pins · Pinède", "Antibes Juan-les-Pins", "juan", "The train cuts across the Cap, so this is the best leapfrog of the day."),
 ("gj", "Golfe-Juan old port", "Vallauris Golfe-Juan", "gj", "The final push begins here; runners appreciate support."),
 ("palm", "Pointe Croisette · Palm Beach", "Cannes", "cannes", "Long walk from Cannes station; a bus or taxi helps."),
 ("finish", "Finish · La Croisette", "Cannes", "cannes", "Opposite the Martinez. Agree a meeting point beyond the finish area."),
]
course = json.loads((root / "data/course.json").read_text())
spots = []
for sid, name, town, st, note in SPOT_META:
    c = course["spots"][sid]
    spots.append({"id": sid, "name": name, "town": town, "st": st, "note": note,
                  "km": 42.195 if sid == "finish" else c["km"], "walk": c["walk"], "lat": c["lat"], "lon": c["lon"]})
line = course["line"]
line[-1][2] = 42.195

def fill(text, tag, value):
    return re.sub(rf"/\*{tag}:BEGIN\*/.*?/\*{tag}:END\*/", lambda m: f"/*{tag}:BEGIN*/{value}/*{tag}:END*/", text, flags=re.S)

css = (root / "vendor/leaflet.css").read_text()
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
css = re.sub(r"\s+", " ", css).replace("*/", "")
src = (root / "src/app.html").read_text()
src = fill(src, "COURSE", json.dumps(line, separators=(",", ":")))
src = fill(src, "SPOTS", json.dumps(spots, ensure_ascii=False, separators=(",", ":")))
src = fill(src, "LEAFLET_CSS", css)
(root / "src/app.html").write_text(src)

# ---- standalone PWA ----
body = src.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>',
                   '<script src="vendor/leaflet.js"></script>')
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
i = body.index('<header class="top">')
(root / "index.html").write_text(head + body[:i] + "</head>\n<body>\n" + body[i:] + tail)

(root / "manifest.webmanifest").write_text("""{
  "name": "Riviera Race Spotter",
  "short_name": "Race Spotter",
  "start_url": "./index.html#live",
  "display": "standalone",
  "background_color": "#EDF3F5",
  "theme_color": "#0B6A86",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}
  ]
}
""")

(root / "sw.js").write_text("""const CACHE = 'race-spotter-v2';
const TILES = 'race-spotter-tiles';
const FILES = ['./', './index.html', './manifest.webmanifest', './vendor/leaflet.js', './icon-180.png', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== TILES).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.hostname.endsWith('basemaps.cartocdn.com') || url.hostname.endsWith('fonts.gstatic.com') || url.hostname === 'fonts.googleapis.com') {
    // Map tiles and fonts: cache first, so areas you've viewed work without signal.
    e.respondWith(caches.open(TILES).then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(r => { c.put(e.request, r.clone()); return r; }))));
    return;
  }
  if (url.origin !== location.origin) return;
  // App files: network first so updates arrive, cache fallback when offline.
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); if (r.ok) caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })
    .catch(() => caches.match(e.request).then(m => m || caches.match('./index.html'))));
});
""")

def icon(size):
    img = Image.new("RGB", (size, size), "#0B6A86")
    d = ImageDraw.Draw(img); s = size / 180
    d.rectangle([0, int(118 * s), size, size], fill="#084E63")
    d.line([(int(14*s), int(118*s)), (int(70*s), int(100*s)), (int(110*s), int(112*s)), (int(166*s), int(92*s))], fill="#EDF3F5", width=max(3, int(6*s)))
    r = int(20 * s); cx, cy = int(110 * s), int(112 * s)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#E8A015", outline="#EDF3F5", width=max(2, int(5*s)))
    try: f = ImageFont.truetype("DejaVuSans-Bold.ttf", int(40 * s))
    except OSError: f = ImageFont.load_default()
    d.text((int(18*s), int(26*s)), "42.2", font=f, fill="#EDF3F5")
    img.save(root / f"icon-{size}.png")
for n in (180, 192, 512): icon(n)
print("built: src/app.html data filled,", len(line), "course points,", len(spots), "spots; index.html + PWA files")
