# Riviera Race Spotter

An iPhone web app for following a runner in the **Marathon des Alpes-Maritimes Nice–Cannes (Sunday 8 November 2026)** and catching them again by train.

## Tabs

- **Live**: one card answers *where do I go now?* It shows the next spot, when to leave, the walk/train/walk legs and **Navigate** buttons that open Google Maps. Below it: the runner's predicted km, pace and finish, and every spot you can still reach in time.
- **Map**: the course routed along the seafront roads, with a predicted runner position, the stretch covered so far, km markers, 15 viewing spots and 11 TER stations. Tap a spot or station for timings and Google Maps directions. Use **Me** to show your GPS position.
- **Plan**: the train-hopping itinerary that fits in the most sightings, ending with meeting them at the finish. It updates whenever predictions change.
- **Runner**: name, target time, start time, positions from the official tracking, train assumptions, rehearsal mode, spot adjustments.

Predictions start from the target time. Tap **I just saw them** at a spot, or add a split from the official tracking, and they switch to the runner's real pace. Everything is stored on the phone. Times are Paris time.

## Where the numbers come from

- **Course line**: routed with OpenStreetMap (`tools/route_course.py`) through seafront waypoints in all seven towns, then calibrated (`tools/calibrate_course.py`) to the official fixed points: start 0, Fort Carré relay 21.1 km, finish 42.195 km. Output: `data/course.json`.
- **Stations and landmarks**: geocoded with OpenStreetMap Nominatim.
- **Walk times**: routed station → course on foot at 4.8 km/h.
- **Train ride times**: estimates for stopping TERs. The default assumes a train every 20 min and that you've just missed one. Check SNCF Connect on the day.

## Install on iPhone (works offline)

Enable GitHub Pages for this repo and branch (Settings → Pages → Deploy from a branch → `/ (root)`). Open the site in Safari, then **Share → Add to Home Screen**. Open the Map once on Wi-Fi so the tiles are cached.

## Build

`src/app.html` is the source (also published as a claude.ai artifact). `python3 build.py` fills in the course data and Leaflet CSS, then writes `index.html`, `manifest.webmanifest`, `sw.js` and the icons.

Map data © OpenStreetMap contributors, tiles © CARTO. Leaflet (BSD-2).
