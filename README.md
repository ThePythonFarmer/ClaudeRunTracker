# Riviera Race Spotter

A one-page iPhone web app for following a runner in the **Marathon des Alpes-Maritimes Nice–Cannes (Sunday 8 November 2026)** and working out which train to take to see them again.

## What it does

- **Now**: estimates where your runner is, and lists the spots you can still reach before they do, with the walk/train/walk legs and the minutes you'll have spare.
- **Plan**: a leapfrog itinerary that fits in the most sightings from where you are. It is recalculated whenever the projection changes.
- **Course**: 15 viewing spots from the start on the Promenade des Anglais to the finish on La Croisette, each with its nearest TER station, walk time and an Apple Maps link. You can edit any km or walk time.
- **Splits**: tap *I just saw them here*, or enter a chip split from the official live tracking. Projections then use their real pace (plus a slowdown % you set).
- **Rehearse**: a slider lets you try the app at any race-day time before Sunday.

Everything is stored on the phone (localStorage). Times are Paris time.

## Install on iPhone

The app has to be served once over HTTPS. Then, in Safari, tap **Share → Add to Home Screen**. The service worker keeps it working without signal.

Easiest: enable **GitHub Pages** for this repo (Settings → Pages → Deploy from branch, root), then open `https://<user>.github.io/<repo>/` on the phone.

## Build

`src/app.html` is the source. `python3 build.py` regenerates `index.html`, `manifest.webmanifest`, `sw.js` and the icons.

## Assumptions to check

- Km positions are estimates, apart from the start, Fort Carré (21.1 km, relay changeover) and the finish (42.195). Compare them with the official course map on marathon06.com.
- Train ride times are approximate for stopping TERs. The default assumes a train every 20 min and that you've just missed one. Check SNCF Connect on the day.
- SNCF *Pass Marathon*: €8, unlimited travel Nice-Riquier ↔ Cannes on race day. Access to Cannes station is controlled after the race.
