# Tablet Flip Clock v1.0

Offline-first Android tablet flip-clock PWA with optional online weather and an ON/OFF screen-awake control.

## Deploy to GitHub Pages
1. Create a public GitHub repository (for example `tablet-flip-clock`).
2. Upload **all four files** (`index.html`, `sw.js`, `manifest.webmanifest`, `icon.svg`) to the repository root.
3. In **Settings → Pages**, choose **Deploy from a branch**, `main`, `/ (root)`, and Save.
4. Wait for GitHub Pages to publish, then visit the HTTPS Pages URL in Android Chrome.
5. Open Chrome's three-dot menu and choose **Install app** or **Add to Home screen**. Launch it once while online to cache files.
6. Turn off Wi-Fi and mobile data, close and reopen the installed app, and confirm the clock still works.

## Screen awake
Open **Settings → Keep screen awake** and turn it ON. This uses the browser Screen Wake Lock API, supported in many recent Android Chromium browsers over HTTPS. A lock may be released when the app loses visibility, the device enters power-saving mode, or Android imposes restrictions. The app attempts to reacquire it when visible again. Turn the toggle OFF to release it. A browser may require a direct tap to enable the lock; if the status says unavailable, try toggling OFF and ON. This is **not** a system-level override of Android's screen timeout.

## Weather
Weather is **OFF by default**. Enable it in Settings, then search a city or grant location permission. Weather uses the Open-Meteo geocoding and forecast endpoints. Last successful conditions are saved locally and marked as cached when offline. Weather may become stale; offline forecasts are not generated. No account or API key is required for non-commercial use; review Open-Meteo terms for other uses.

## Other notes
- The clock uses the tablet's device time and timezone; offline accuracy depends on correct device time.
- Settings are stored locally in browser storage; clearing site data removes them and may remove offline cache.
- For best PWA install compatibility, consider adding PNG icons of 192px and 512px to the manifest later. SVG works in Chromium but installation prompts can vary.
- No external JS or CSS assets are needed.
- `file://` opening is not equivalent to PWA installation; service workers require HTTPS or localhost.
